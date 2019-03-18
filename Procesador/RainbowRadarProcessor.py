# -*- coding: utf-8 -*-

__author__ = "Andres Giordano"
__version__ = "1.0"
__maintainer__ = "Andres Giordano"
__email__ = "andresgiordano.unlu@gmail.com"
__status__ = "Produccion"

import matplotlib as mpl

import matplotlib.pyplot as plt

import setuptools
import os.path
from pyart.graph import RadarDisplay, common, GridMapDisplay, RadarMapDisplay
import pyart.map
import pyart.config
import pyart.io

from .RainbowRadar import RainbowRadar
from .Utils import fig2img,PNG,JPEG,gen_ticks

class RainbowRadarProcessor(object):

    def __init__(self, rainbowRadar):
        """
        Constructor

        :param RainbowRadar rainbowRadar: radar a procesar.
        """

        self.__rainbowRadar = None

        if isinstance(rainbowRadar, RainbowRadar):
            self.__rainbowRadar = rainbowRadar
        else:
            raise Exception("El parametro rainbowRadar no es una instancia de RainbowRadar")

        self.__volPath = self.__rainbowRadar.getFilePath()
        self.__volFileName = self.__rainbowRadar.getFileName()
        self.__RADAR_FILE_OUT = self.__volPath + self.__volFileName + "_ppi.grib"

    def getPPIImage(self, elevation, mask=None, figsize=(25, 25), paddingImg=1, basemapFlag=True, basemapShapeFile=None,
                    dpi=200, font=None):
        """
        Este metodo retorna la imagen bidimensional del retorno radarico segun
        el numero de elevacion que se pase por parametro.

        :param elevation: indica el numero de elevacion a obtener.
        :type elevation: int
        :param mask: mascara a aplicar a los datos de radar.
        :param figsize: es una tupla que indica el tamaño de la imagen a generar
        :type figsize: tuple of int
        :param paddingImg: se usa para agregarle padding a la imagen del radar.
        :type paddingImg: int
        :param basemapFlag: se usa para indicar si se debe tomar :param basemapShapeFile: para indicar el archivo de capa para basemap.
        :type basemapFlag: bool
        :param basemapShapeFile: path al directorio que contiene el archivo de capa (.shp) para basemap.
        :type basemapShapeFile: str
        :param dpi: se usa para indicar calidad del grafico a generar.
        :type dpi: int
        :param font: configuracion de las fuentes del grafico --> ``Matplotlib.rc('font', **font)``. Por defecto:  ``{'family': 'sans-serif', 'size': 35}``.
        :return:

        """

        plt.clf()

        if font is None:
            font = {'family': 'sans-serif', 'size': 35}

        mpl.rc('font', **font)

        # Aplico mascara a los datos del radar antes de obtener la elevacion
        if mask is not None:
            self.__rainbowRadar.setMask(maskString=mask, dst='raw')

        eleN = self.__rainbowRadar.getSweep(elevation)

        display_variable = RadarDisplay(eleN)

        fig = plt.figure(figsize=figsize,dpi=dpi)
        fig.add_subplot(1, 1, 1, aspect=1.0)
        rango_anillos = self.__rainbowRadar.getStopRange() / 4
        anillos = [rango_anillos, rango_anillos * 2, rango_anillos * 3, self.__rainbowRadar.getStopRange()]

        # Obtengo longitud, latitud minima y maxima a partir de la grilla, y le agrego el padding
        min_lat = self.__rainbowRadar.getMinLat() - paddingImg
        max_lat = self.__rainbowRadar.getMaxLat() + paddingImg
        min_lon = self.__rainbowRadar.getMinLon() - paddingImg
        max_lon = self.__rainbowRadar.getMaxLon() + paddingImg

        titulo = common.generate_title(self.__rainbowRadar.getRadar(), self.__rainbowRadar.getRadarVariable()[1],
                                       elevation, datetime_format='%d-%m-%Y %M:%S')

        if basemapFlag:
            display_variable = RadarMapDisplay(eleN)

            # Si hay un shapefile elegido por el usuario se toma ese, en otro caso se toma el shapefile por defecto
            if basemapShapeFile is not None:

                display_variable.plot_ppi_map(self.__rainbowRadar.getRadarVariable()[1],
                                              colorbar_label=self.__rainbowRadar.getRadarVariable()[5],
                                              title=titulo,
                                              vmin=self.__rainbowRadar.getRadarVariable()[3],
                                              vmax=self.__rainbowRadar.getRadarVariable()[4],
                                              cmap=self.__rainbowRadar.getRadarVariable()[2],
                                              shapefile=basemapShapeFile,
                                              min_lat=min_lat,
                                              max_lat=max_lat,
                                              min_lon=min_lon,
                                              max_lon=max_lon
                                              )
            else:
                display_variable.plot_ppi_map(self.__rainbowRadar.getRadarVariable()[1],
                                              colorbar_label=self.__rainbowRadar.getRadarVariable()[5],
                                              title=titulo,
                                              vmin=self.__rainbowRadar.getRadarVariable()[3],
                                              vmax=self.__rainbowRadar.getRadarVariable()[4],
                                              cmap=self.__rainbowRadar.getRadarVariable()[2],
                                              shapefile=os.path.dirname(
                                                  __file__) + '/departamento/departamento',
                                              min_lat=min_lat,
                                              max_lat=max_lat,
                                              min_lon=min_lon,
                                              max_lon=max_lon
                                              )
            display_variable.basemap.fillcontinents(lake_color='aqua',
                                                        alpha=0.2)
            # Se agregan las latitudes y longitudes
            orig_lat = self.__rainbowRadar.getLatitude()
            orig_lon = self.__rainbowRadar.getLongitude()

            lat_ticks = gen_ticks(orig_lat, min_lat, max_lat)
            lon_ticks = gen_ticks(orig_lon, min_lon, max_lon)

            display_variable.basemap.drawparallels(lat_ticks, labels=[1, 0, 0, 0], labelstyle='+/-',
                                            fmt='%.2f', linewidth=0, rotation=45)
            display_variable.basemap.drawmeridians(lon_ticks, labels=[0, 0, 0, 1], labelstyle='+/-',
                                            fmt='%.2f', linewidth=0, rotation=45)

        else:

            radar_range = [-self.__rainbowRadar.getStopRange() - paddingImg, self.__rainbowRadar.getStopRange() + paddingImg]

            display_variable.plot_ppi(self.__rainbowRadar.getRadarVariable()[1],
                                      colorbar_label=self.__rainbowRadar.getRadarVariable()[5],
                                      title=titulo,
                                      axislabels=('Distancia en X (km)', 'Distancia en Y (km)'),
                                      vmin=self.__rainbowRadar.getRadarVariable()[3],
                                      vmax=self.__rainbowRadar.getRadarVariable()[4],
                                      cmap=self.__rainbowRadar.getRadarVariable()[2])

            display_variable.set_limits(radar_range, radar_range)
            display_variable.plot_range_rings(anillos, lw=0.5)

            r_max = self.__rainbowRadar.getStopRange()
            display_variable.plot_cross_hair(r_max)

        res = fig2img(plt.gcf())

        plt.close(fig)


        return res

    def getCAPPIImage(self, level, mask=None, figsize=(25, 25), paddingImg=1, basemapFlag=True,
                      basemapShapeFile=None, dpi=200, font=None):
        """
        Genera la imagen del radar desde la grilla.

        :param level: nivel de la grilla a graficar. Ej. : 3 --> 2km < altitud <= 3 km
        :param mask: mascara a aplicar a al nivel de la grilla una vez generada.
        :param figsize:
        :param paddingImg:
        :param basemapFlag:
        :param basemapShapeFile:
        :param dpi:
        :param font: configuracion de las fuentes del grafico --> ``Matplotlib.rc('font', **font)``. Por defecto:  ``{'family': 'sans-serif', 'size': 35}``.
        :return:
        """

        plt.clf()

        if font is None:
            font = {'family': 'sans-serif', 'size': 35}

        mpl.rc('font', **font)

        grilla = self.__rainbowRadar.getCartesianGrid()

        # Aplico mascara
        if mask is not None:
            self.__rainbowRadar.setMask(mask, level=level)

        # create the plot
        fig = plt.figure(figsize=figsize,dpi=dpi)
        ax = fig.add_subplot(111)

        ############################################################################
        # TITULO
        time_str = common.generate_grid_time_begin(grilla).strftime('%d-%m-%Y %M:%S')
        height = grilla.z['data'][level] / 1000.
        l1 = "%s %.1f km %s " % (common.generate_grid_name(grilla), height,
                                 time_str)
        field_name = common.generate_field_name(grilla, self.__rainbowRadar.getRadarVariable()[1])
        titulo = l1 + '\n' + field_name
        ############################################################################

        if basemapFlag:
            # Se genera el grafico con el mapa debajo
            grid_plot = GridMapDisplay(grilla)
            min_lat = self.__rainbowRadar.getMinLat() - paddingImg
            max_lat = self.__rainbowRadar.getMaxLat() + paddingImg
            min_lon = self.__rainbowRadar.getMinLon() - paddingImg
            max_lon = self.__rainbowRadar.getMaxLon() + paddingImg

            grid_plot.plot_basemap(min_lon=min_lon,max_lon=max_lon,min_lat=min_lat,max_lat=max_lat,auto_range=False,resolution='h', projection='lcc')

            # Si hay un shapefile elegido por el usuario se toma ese, en otro caso se toma el shapefile por defecto
            if basemapShapeFile is not None:
                grid_plot.basemap.readshapefile(basemapShapeFile,
                                                os.path.basename(basemapShapeFile))
            else:
                grid_plot.basemap.readshapefile(os.path.dirname(__file__) + '/departamento/departamento', 'departamento',default_encoding='LATIN1')

            grid_plot.basemap.fillcontinents(lake_color='aqua',
                                             alpha=0.2)

            grid_plot.plot_grid(self.__rainbowRadar.getRadarVariable()[1],
                                colorbar_label=self.__rainbowRadar.getRadarVariable()[5],
                                title=titulo,
                                title_flag=True,
                                colorbar_flag=True,
                                vmin=self.__rainbowRadar.getRadarVariable()[3],
                                vmax=self.__rainbowRadar.getRadarVariable()[4],
                                cmap=self.__rainbowRadar.getRadarVariable()[2],
                                level=level,
                                fig=fig,ax=ax)

            # Se agregan las latitudes y longitudes

            orig_lat = self.__rainbowRadar.getLatitude()
            orig_lon = self.__rainbowRadar.getLongitude()

            lat_ticks = gen_ticks(orig_lat, min_lat, max_lat)
            lon_ticks = gen_ticks(orig_lon, min_lon, max_lon)

            grid_plot.basemap.drawparallels(lat_ticks, labels=[1, 0, 0, 0], labelstyle='+/-',
                                                   fmt='%.2f', linewidth=0, rotation=45)
            grid_plot.basemap.drawmeridians(lon_ticks, labels=[0, 0, 0, 1], labelstyle='+/-',
                                                   fmt='%.2f', linewidth=0, rotation=45)

        else:

            # Se genera el grafico comun con los anillos

            # Limites de la grilla
            radar_range = [-self.__rainbowRadar.getStopRange() - paddingImg, self.__rainbowRadar.getStopRange() + paddingImg]

            # Shift para que el centro de la grafica sea (0,0)
            shift = (-self.__rainbowRadar.getStopRange(), self.__rainbowRadar.getStopRange(), -self.__rainbowRadar.getStopRange(), self.__rainbowRadar.getStopRange())

            # Se genera el grafico
            im = ax.imshow(grilla.fields[self.__rainbowRadar.getRadarVariable()[1]]['data'][level],
                           origin='origin',
                           vmin=self.__rainbowRadar.getRadarVariable()[3],
                           vmax=self.__rainbowRadar.getRadarVariable()[4],
                           cmap=self.__rainbowRadar.getRadarVariable()[2],
                           extent=shift)

            plt.xlabel('Distancia en X (km)')
            plt.ylabel('Distancia en Y (km)')
            plt.title(titulo)

            # Distancia entre los anillos
            rangoAnillos = self.__rainbowRadar.getStopRange() / 4
            anillos = [rangoAnillos, rangoAnillos * 2, rangoAnillos * 3, self.__rainbowRadar.getStopRange()]
            Rmax = self.__rainbowRadar.getStopRange()

            fig.colorbar(im, ax=ax, cax=None)

            # Se generan los anillos, se indican los limites y cross hair con los metodos estaticos de la clase RadarDisplay
            for range_ring_location_km in anillos:
                RadarDisplay.plot_range_ring(range_ring_location_km, lw=0.5)

            RadarDisplay.set_limits(radar_range, radar_range)
            RadarDisplay.plot_cross_hair(Rmax)

        res = fig2img(plt.gcf())

        plt.close(fig) # Para solucionar bug #3

        return res

    def showImage(self, elevation):
        self.getCAPPIImage(elevation).show()

    def saveImageToFile(self, pathOutput=None, fileOutput=None,
                        imageType=PNG, method='grid',  image_method_params=None):
        """
        Guarda en un archivo el grafico de la elevacion seleccionada.

        :param pathOutput: Carpeta destino. Por defecto, la carpeta del archivo .vol
        :param fileOutput: Archivo destino. Por defecto el nombre del archivo .vol__ele[elevation]
        :param imageType: Formato en que se va a almacenar la imagen.
        :param method:  Metodo por el cual se obtiene la imagen. 'grid' obtiene la imagen a partir de la grilla cartesiana :func:`~RainbowRadarProcessor.getImageFromCartesianGrid` y 'simple' :func:`~RainbowRadarProcessor.getRawDataImage` genera la imagen con datos crudos.
        :param image_method_params: en este parametro se pueden indicar los parametros a pasar al metodo de generacion de la imagen indicado por por el parametro `method`. Por defecto, elevation=0
        :type image_method_params: dict
        :return:
        """

        if method == 'grid':

            method_params = {'level': 0}
            if image_method_params is not None:
                method_params.update(image_method_params)
            elevationImg = self.getCAPPIImage(**method_params)
            m_filename_metadata = "_nivel_" + str(method_params['level'])

        elif method == 'simple':

            method_params = {'elevation': 0}
            if image_method_params is not None:
                method_params.update(image_method_params)
            elevationImg = self.getPPIImage(**method_params)
            m_filename_metadata = "_elevacion_" + str(method_params['elevation'])

        else:
            raise Exception(
                "El metodo " + method + " no es un metodo valido para obtener la imagen. Posibles: [grid,simple] ")

        if fileOutput is not None and pathOutput is not None:
            if imageType == JPEG:
                elevationImg.convert("RGB").save(
                    pathOutput + fileOutput + m_filename_metadata + '.' + imageType, quality=95)
            else:
                elevationImg.save(pathOutput + fileOutput + m_filename_metadata + '.' + imageType, quality=95)
        elif fileOutput is None and pathOutput is not None:
            if imageType == JPEG:
                elevationImg.convert("RGB").save(
                    pathOutput + self.__volFileName + m_filename_metadata + '.' + imageType, quality=95)
            else:
                elevationImg.save(pathOutput + self.__volFileName + m_filename_metadata + '.' + imageType, quality=95)
        elif fileOutput is not None and pathOutput is None:
            if imageType == JPEG:
                elevationImg.convert("RGB").save(self.__volPath + fileOutput + '.' + imageType, quality=95)
            else:
                elevationImg.save(self.__volPath + fileOutput + '.' + imageType, quality=95)
        else:
            if imageType == JPEG:
                elevationImg.convert("RGB").save(
                    self.__volPath + self.__volFileName + m_filename_metadata + '.' + imageType, quality=95)
            else:
                elevationImg.save(
                    self.__volPath + self.__volFileName + m_filename_metadata + '.' + imageType, quality=95)

    def saveToNETCDF(self, outFilePath, outFileName):
        """
        Guarda la grilla en formato NETCDF


        :param outFilePath: directorio donde se almacenará el archivo.
        :param outFileName: nombre del archivo a guardar.


        """
        pyart.io.write_grid(outFilePath + outFileName + ".netCDF",
                            self.__rainbowRadar.getCartesianGrid(),
                            format='NETCDF3_64BIT',
                            arm_time_variables=True)

    def saveToGTiff(self, level, outFilePath, outFileName):

        pyart.io.write_grid_geotiff(self.__rainbowRadar.getCartesianGrid(),
                                    filename=outFilePath + outFileName + "_level_" + str(level) + ".tif",
                                    field=self.__rainbowRadar.getRadarVariable()[1],
                                    level=level,
                                    #rgb=True,
                                    #cmap= self.__rainbowRadar.getRadarVariable()[2],
                                    #vmin= self.__rainbowRadar.getRadarVariable()[3],
                                    #vmax= self.__rainbowRadar.getRadarVariable()[4],
                                    warp=True
                                    )
