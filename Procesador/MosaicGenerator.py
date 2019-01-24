# -*- coding: utf-8 -*-

from .RainbowRadar import RainbowRadar
from geopy.distance import vincenty
from geopy.units import degrees,nautical
import setuptools
import pyart.map
from .Utils import fig2img,PNG,JPEG,gen_ticks
from pyart.graph import common, GridMapDisplay
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy.ma as ma

class MosaicGenerator(object):

    def __init__(self, radars=None):
        """

        :param radars: list of RainbowRadar
        :type radars: list of RainbowRadar
        """

        self.__radars = []
        self.__grid = None
        self.__mosaicImages = {}

        # Ajuste de la grilla en KM
        self.__grid_adjust = 0

        if radars is not None:
            for radar in radars:
                self.addRadar(radar)

    def addRadar(self, radar):
        if isinstance(radar, RainbowRadar):
            self.__radars.append(radar)
        else:
            raise Exception("El parametro 'radar' no es un objeto del tipo RainbowRadar")

    def __getCenterCoordinates(self):
        """
        Calcula el centro de masa entre los radares que componen el mosaico a partir de sus coordenadas.

        :return: latitud y longitud del punto central
        """
        # Obtengo las coordenadas de todos los radares
        points = self.__getRadarsCoordinates()

        latitude_sum = 0
        longitude_sum = 0

        for p in points:
            latitude_sum += p[0]
            longitude_sum += p[1]

        latitude_center = latitude_sum / len(points)
        longitude_center = longitude_sum / len(points)

        return latitude_center, longitude_center

    def __getRadarsCoordinates(self):
        """
        Devuelve una lista con las coordenadas de todos los radares que componen el mosaico.

        :return: lista de coordenadas
        :rtype: list of tuple of float
        """
        points = []

        for radar in self.__radars:
            points.append((radar.getLatitude(), radar.getLongitude()))

        return points

    def __getMaxLonPoint(self):
        res = None
        for radar in self.__radars:
            if res is None or res < radar.getMaxLon():
                res = radar.getMaxLon()

        return self.__getCenterCoordinates()[0], res

    def __getMinLonPoint(self):
        res = None
        for radar in self.__radars:
            if res is None or res > radar.getMinLon():
                res = radar.getMinLon()

        return self.__getCenterCoordinates()[0], res

    def __getMinLatPoint(self):
        res = None
        for radar in self.__radars:
            if res is None or res > radar.getMinLat():
                res = radar.getMinLat()

        return res, self.__getCenterCoordinates()[1]

    def __getMaxLatPoint(self):
        res = None
        for radar in self.__radars:
            if res is None or res < radar.getMaxLat():
                res = radar.getMaxLat()

        return res, self.__getCenterCoordinates()[1]

    def getMosaicGrid(self):

        if self.__grid is None:

            # Verificamos que se haya cargado  al menos dos radares
            if len(self.__radars) <= 1:
                raise Exception("No se han cargado radares suficientes para generar un mosaico")

            # Verifico que todos los radares hagan un barrido de la misma distancia (en km) ya que influye en el valor de nb y bsp.
            stopRange = self.__radars[0].getStopRange()

            for radar in self.__radars:
                if radar.getStopRange() != stopRange:
                    raise Exception(
                        "Los rangos de los radares son diferentes. Solo se permite que sean todos de 120km , 240km o 480km")



            # Obtengo las distancias entre el punto central y el de maxima longitud y el de maxima latitud
            elipse = 'WGS-84'
            center_point = self.__getCenterCoordinates()

            distances = [   vincenty(center_point, self.__getMinLatPoint(), ellipsoid=elipse).meters,
                            vincenty(center_point, self.__getMaxLatPoint(), ellipsoid=elipse).meters,
                            vincenty(center_point, self.__getMinLonPoint(), ellipsoid=elipse).meters,
                            vincenty(center_point, self.__getMaxLonPoint(), ellipsoid=elipse).meters]

            # Obtengo la maxima distancia
            meters = 1000

            limit_min_lat = (self.__grid_adjust * meters) + distances[0]
            limit_max_lat = (self.__grid_adjust * meters) + distances[1]
            limit_min_lon = (self.__grid_adjust * meters) + distances[2]
            limit_max_lon = (self.__grid_adjust * meters) + distances[3]


            # Obtengo los sweeps en base a la elevacion
            all_radars = []
            for radar in self.__radars:
                all_radars.append(radar.getRadar())

            # Ahora genero la grilla en base a los datos anteriores:
            z = 29
            self.__grid = pyart.map.grid_from_radars(
                tuple(all_radars),
                grid_shape=(z, 480 * len(self.__radars), 480 * len(self.__radars)),
                grid_limits=(
                    (0, z * meters),
                    (-limit_min_lat, limit_max_lat),
                    (-limit_min_lon, limit_max_lon)
                ),
                weighting_function='Cressman', # Segun Jian Zhang "THREE-DIMENSIONAL GRIDDING AND MOSAIC OF REFLECTIVITIES FROM MULTIPLE WSR-88D RADARS" se prefiere usar esta funcion para mosaico
                grid_origin=center_point,
                fields=[self.__radars[0].getRadarVariable()[1]]
            )

        return self.__grid

    def setMask(self, mask, level=0):
        if mask != '':
            if self.__grid is not None:
                if level is not None:
                    a = self.__grid.fields[self.__radars[0].getRadarVariable()[1]]['data'][level]
                    ma.masked_where(eval(mask), a, copy=False)
                else:
                    for x in range(len(self.__grid.fields[self.__radars[0].getRadarVariable()[1]]['data'])):
                        a = self.__grid.fields[self.__radars[0].getRadarVariable()[1]]['data'][x]
                        ma.masked_where(eval(mask), a, copy=False)
            else:
                raise Exception('La grilla aun no ha sido creada')

    def getMosaicImage(self, level=0, mask=None, figsize=(20, 20), dpi=200, font=None):
        """
        Genera un mosaico con los radares que componen la instancia y luego crea un grafico CAPPI de la elevacion indicada.

        :param level: nivel de la grilla a graficar.
        :param mask: mascara a aplicar a la grilla del mosaico.
        :param figsize: tamaño de la figura a generar
        :param dpi: calidad de la imagen a generar.
        :param font: configuracion de las fuentes del grafico --> ``Matplotlib.rc('font', **font)``. Por defecto:  ``{'family': 'sans-serif', 'size': 35}``.
        :return:
        """
        plt.clf()

        if font is None:
            font = {'family': 'sans-serif', 'size': 35}

        mpl.rc('font', **font)

        fig = plt.figure(figsize=figsize, dpi=dpi)
        fig.add_subplot(1, 1, 1, aspect=1.0)

        grilla = self.getMosaicGrid()

        if mask is not None:
            self.setMask(mask,level=level)

        time_str = common.generate_grid_time_begin(grilla).strftime('%d-%m-%Y %M:%S')
        height = grilla.z['data'][level] / 1000.
        l1 = "%s %.1f km %s " % (common.generate_grid_name(grilla), height,
                                 time_str)
        field_name = common.generate_field_name(grilla, self.__radars[0].getRadarVariable()[1])
        titulo = l1 + '\n' + field_name

        grid_plot = GridMapDisplay(grilla)
        grid_plot.plot_grid(self.__radars[0].getRadarVariable()[1],
                            colorbar_label=self.__radars[0].getRadarVariable()[0],
                            title=titulo,
                            title_flag=True,
                            vmin=self.__radars[0].getRadarVariable()[3],
                            vmax=self.__radars[0].getRadarVariable()[4],
                            cmap=self.__radars[0].getRadarVariable()[2],
                            level=level
                            )
        grid_plot.plot_basemap(resolution='h')
        grid_plot.basemap.readshapefile(os.path.dirname(__file__) + '/departamento/departamento',
                                        'departamentos')

        center_point = self.__getCenterCoordinates()

        d_correc = degrees(arcminutes=nautical(kilometers=self.__grid_adjust))

        lat_ticks = gen_ticks(center_point[0],
                              self.__getMinLatPoint()[0]-d_correc,
                              self.__getMaxLatPoint()[0]+d_correc)
        lon_ticks = gen_ticks(center_point[1],
                              self.__getMinLonPoint()[1]-d_correc,
                              self.__getMaxLonPoint()[1]+d_correc)

        grid_plot.basemap.drawparallels(lat_ticks, labels=[1, 0, 0, 0], labelstyle='+/-',
                                        fmt='%.2f', linewidth=0, rotation=45)
        grid_plot.basemap.drawmeridians(lon_ticks, labels=[0, 0, 0, 1], labelstyle='+/-',
                                        fmt='%.2f', linewidth=0, rotation=45)

        res = fig2img(plt.gcf())
        plt.close(plt.gcf())

        return res

    def saveImageToFile(self, pathOutput, fileOutput, imageType=PNG, image_params=None):
        """
        Guarda en un archivo el grafico de la elevacion seleccionada.

        :param pathOutput: Carpeta destino. Por defecto, la carpeta del archivo .vol
        :param fileOutput: Archivo destino. Por defecto el nombre del archivo .vol__ele[elevation]
        :param imageType: Formato en que se va a almacenar la imagen.
        :param image_params: diccionario con los parametros a pasar a la funcion que genera el grafico de radar :func:`~MosaicGenerator.getMosaicImage`
        :return:
        """
        _image_params = {'level': 0}

        if image_params is not None:
            _image_params.update(image_params)

        elevationImg = self.getMosaicImage(**_image_params)

        if imageType == JPEG:
            elevationImg.convert("RGB").save(pathOutput + fileOutput + "_nivel_" + str(_image_params['level']) + '.' + imageType)
        else:
            elevationImg.save(pathOutput + fileOutput + "_nivel_" + str(_image_params['level']) + '.' + imageType)

    def saveToNETCDF(self, filePath, fileName):
        pyart.io.write_grid(filePath + fileName + ".netCDF",
                            self.getMosaicGrid(),
                            format='NETCDF3_64BIT',
                            arm_time_variables=True)

    def saveToGTiff(self, level, outFilePath, outFileName):

        pyart.io.write_grid_geotiff(self.getMosaicGrid(),
                                    filename=outFilePath + outFileName
                                                   + "_nivel_" + str(level) + ".tif",
                                    field=self.__radars[0].getRadarVariable()[1],
                                    level=level,
                                    rgb=True,
                                    cmap=self.__radars[0].getRadarVariable()[2],
                                    vmin=self.__radars[0].getRadarVariable()[3],
                                    vmax=self.__radars[0].getRadarVariable()[4],
                                    warp=True
                                    )
