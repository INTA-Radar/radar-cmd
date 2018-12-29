# -*- coding: utf-8 -*-

from .RainbowRadar import RainbowRadar
from geopy.distance import vincenty
from geopy.units import degrees,nautical
import setuptools
import pyart.map
from .Utils import getBsp,fig2img,PNG,JPEG,gen_ticks
from pyart.graph import common, GridMapDisplay
import os
import matplotlib.pyplot as plt
import matplotlib as mpl

class MosaicGenerator(object):
    """

    """
    def __init__(self, radars=None):
        '''

        :param radars: list of RainbowRadar
        :type radars: list of RainbowRadar
        '''
        self.__radars = []
        self.__mosaicGrids = {}
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

    def __getMaxLonPoint(self, elevation):
        res = None
        for radar in self.__radars:
            if res is None or res < radar.getMaxLon(elevation):
                res = radar.getMaxLon(elevation)

        return self.__getCenterCoordinates()[0], res

    def __getMinLonPoint(self, elevation):
        res = None
        for radar in self.__radars:
            if res is None or res > radar.getMinLon(elevation):
                res = radar.getMinLon(elevation)

        return self.__getCenterCoordinates()[0], res

    def __getMinLatPoint(self, elevation):
        res = None
        for radar in self.__radars:
            if res is None or res > radar.getMinLat(elevation):
                res = radar.getMinLat(elevation)

        return res, self.__getCenterCoordinates()[1]

    def __getMaxLatPoint(self, elevation):
        res = None
        for radar in self.__radars:
            if res is None or res < radar.getMaxLat(elevation):
                res = radar.getMaxLat(elevation)

        return res, self.__getCenterCoordinates()[1]

    def getMosaicGrid(self, elevation=0, _bsp='calculate'):

        if elevation not in self.__mosaicGrids:

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

            distances = [   vincenty(center_point, self.__getMinLatPoint(elevation), ellipsoid=elipse).meters,
                            vincenty(center_point, self.__getMaxLatPoint(elevation), ellipsoid=elipse).meters,
                            vincenty(center_point, self.__getMinLonPoint(elevation), ellipsoid=elipse).meters,
                            vincenty(center_point, self.__getMaxLonPoint(elevation), ellipsoid=elipse).meters]

            # Obtengo la maxima distancia
            meters = 1000

            limit_min_lat = (self.__grid_adjust * meters) + distances[0]
            limit_max_lat = (self.__grid_adjust * meters) + distances[1]
            limit_min_lon = (self.__grid_adjust * meters) + distances[2]
            limit_max_lon = (self.__grid_adjust * meters) + distances[3]


            # Obtengo los sweeps en base a la elevacion
            radar_sweeps = []
            for radar in self.__radars:
                radar_sweeps.append(radar.getSweep(elevation))

            if _bsp == 'calculate':
                _bsp = getBsp(stopRange, radar_sweeps[0].fixed_angle['data'][0])
            elif _bsp == 'default':
                _bsp = 1.0
            elif type(_bsp) != float:
                raise Exception('Los valores posibles de BSP son \'calculate\', \'default\' o un float indicando el valor.')

            # Ahora genero la grilla en base a los datos anteriores:
            grid = pyart.map.grid_from_radars(
                tuple(radar_sweeps),
                grid_shape=(1, 480 * len(self.__radars), 480 * len(self.__radars)),
                grid_limits=(
                    (200, 4 * meters),
                    (-limit_min_lat, limit_max_lat),
                    (-limit_min_lon, limit_max_lon)
                ),
                nb=radar_sweeps[0].fixed_angle['data'][0],
                bsp=_bsp,
                grid_origin=center_point,
                fields=[self.__radars[0].getRadarVariable()[1]]
            )

            self.__mosaicGrids[elevation] = grid

        return self.__mosaicGrids[elevation]

    def getMosaicImage(self, elevation=0, figsize=(20, 20), dpi=200, font=None, bsp_value = 'calculate'):
        """

        :param elevation:
        :param figsize: tamaño de la figura a generar
        :param dpi: calidad de la imagen a generar.
        :param font: configuracion de las fuentes del grafico --> ``Matplotlib.rc('font', **font)``. Por defecto:  ``{'family': 'sans-serif', 'size': 35}``.
        :param bsp_value: valor de BSP a usar en :func:`~MosaicGenerator.getMosaicGrid`
        :return:
        """
        plt.clf()

        if font is None:
            font = {'family': 'sans-serif', 'size': 35}

        mpl.rc('font', **font)

        fig = plt.figure(figsize=figsize, dpi=dpi)
        fig.add_subplot(1, 1, 1, aspect=1.0)

        grid = self.getMosaicGrid(elevation,_bsp=bsp_value)

        titulo = common.generate_title(self.__radars[0].getRadar(), self.__radars[0].getRadarVariable()[1], elevation,
                                            datetime_format = '%d-%m-%Y %M:%S')



        grid_plot = GridMapDisplay(grid)
        grid_plot.plot_grid(self.__radars[0].getRadarVariable()[1],
                            colorbar_label=self.__radars[0].getRadarVariable()[0],
                            title=titulo,
                            title_flag=True,
                            vmin=self.__radars[0].getRadarVariable()[3],
                            vmax=self.__radars[0].getRadarVariable()[4],
                            cmap=self.__radars[0].getRadarVariable()[2])
        grid_plot.plot_basemap(resolution='h')
        grid_plot.basemap.readshapefile(os.path.dirname(__file__) + '/departamento/departamento',
                                        'departamentos')

        center_point = self.__getCenterCoordinates()

        d_correc = degrees(arcminutes=nautical(kilometers=self.__grid_adjust))

        lat_ticks = gen_ticks(center_point[0],
                              self.__getMinLatPoint(elevation)[0]-d_correc,
                              self.__getMaxLatPoint(elevation)[0]+d_correc)
        lon_ticks = gen_ticks(center_point[1],
                              self.__getMinLonPoint(elevation)[1]-d_correc,
                              self.__getMaxLonPoint(elevation)[1]+d_correc)

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
        _image_params = {'elevation': 0}

        if image_params is not None:
            _image_params.update(image_params)

        elevationImg = self.getMosaicImage(**_image_params)

        if imageType == JPEG:
            elevationImg.convert("RGB").save(pathOutput + fileOutput + "_elevacion_" + str(_image_params['elevation']) + '.' + imageType)
        else:
            elevationImg.save(pathOutput + fileOutput + "_elevacion_" + str(_image_params['elevation']) + '.' + imageType)

    def saveToNETCDF(self, elevation, filePath, fileName,bsp_value='calculate'):
        pyart.io.write_grid(filePath + fileName + "_elevacion_" + str(elevation) + ".grib",
                            self.getMosaicGrid(elevation, _bsp=bsp_value),
                            format='NETCDF3_64BIT',
                            arm_time_variables=True)

    def saveToGTiff(self, elevation, outFilePath, outFileName,bsp_value='calculate'):

        grid = self.getMosaicGrid(elevation,_bsp=bsp_value)

        pyart.io.write_grid_geotiff(grid, filename=outFilePath + outFileName
                                                   + "_elevacion_" + str(elevation) + ".tif",
                                    field=self.__radars[0].getRadarVariable()[1],
                                    warp=False)
