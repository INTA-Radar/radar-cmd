# -*- coding: utf-8 -*-
__author__ = "Andres Giordano"
__version__ = "1.0"
__maintainer__ = "Andres Giordano"
__email__ = "andresgiordano.unlu@gmail.com"
__status__ = "Produccion"

from pylab import *

import matplotlib.pyplot as plt

import setuptools
import os.path
from pyart.graph import RadarDisplay, common, GridMapDisplay, RadarMapDisplay
import pyart.map
import pyart.config
import pyart.io

from .RainbowRadar import RainbowRadar
from .Utils import fig2img,PNG,JPEG

class RainbowRadarProcessor(object):
    """
    @param sweepDistance: indica la distancia de la señal lanzada por el radar. Se usa para ajustar los graficos y crear los anillos
    @param radarVariable: se usa para indicar el tipo de variable que contienen los datos del archivo

    """

    def __init__(self, rainbowRadar):

        self.__rainbowRadar = None

        if isinstance(rainbowRadar, RainbowRadar):
            self.__rainbowRadar = rainbowRadar
        else:
            raise Exception("El parametro rainbowRadar no es una instancia de RainbowRadar")

        self.__volPath = self.__rainbowRadar.getFilePath()
        self.__volFileName = self.__rainbowRadar.getFileName()
        # self.__radarData = self.__rainbowRadar.getRadar()

        self.__elevationImages = {}
        self.__elevationImagesFromCartGrid = {}

        self.__RADAR_FILE_OUT = self.__volPath + self.__volFileName + "_ppi.grib"

    def getRawDataImage(self, elevation, figsize=(10, 10), paddingImg=1, basemapFlag=True, basemapShapeFile=None):
        '''

        Este metodo retorna la imagen bidimensional del retorno radarico segun
        el numero de elevacion que se pase por parametro.

        @param elevation es el numero de elevacion a obtener
        @param figsize es una tupla que indica el tamaño de la imagen a generar
        @param paddingImg se usa para agregarle un borde en blanco a la imagen
        '''
        plt.clf()
        if not elevation in self.__elevationImages:

            eleN = self.__rainbowRadar.getSweep(elevation)

            display_variable = RadarDisplay(eleN)

            fig = plt.figure(figsize=figsize)
            fig.add_subplot(1, 1, 1, aspect=1.0)
            rangoAnillos = self.__rainbowRadar.getStopRange() / 4
            anillos = [rangoAnillos, rangoAnillos * 2, rangoAnillos * 3, self.__rainbowRadar.getStopRange()]

            if basemapFlag:
                display_variable = RadarMapDisplay(eleN)
                # Obtengo longitud, latitud minima y maxima a partir de la grilla, y le agrego el padding
                min_lat = self.__rainbowRadar.getMinLat(elevation) - paddingImg
                max_lat = self.__rainbowRadar.getMaxLat(elevation) + paddingImg
                min_lon = self.__rainbowRadar.getMinLon(elevation) - paddingImg
                max_lon = self.__rainbowRadar.getMaxLon(elevation) + paddingImg

                # Si hay un shapefile elegido por el usuario se toma ese, en otro caso se toma el shapefile por defecto
                if basemapShapeFile != None:

                    display_variable.plot_ppi_map(self.__rainbowRadar.getRadarVariable()[1],
                                                  colorbar_label=self.__rainbowRadar.getRadarVariable()[0],
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
                                                  colorbar_label=self.__rainbowRadar.getRadarVariable()[0],
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
            else:
                xlabel = 'Distancia en X (km)'
                ylabel = 'Distancia en Y (km)'

                range = [-self.__rainbowRadar.getStopRange() - paddingImg, self.__rainbowRadar.getStopRange() + paddingImg]

                Rmax = self.__rainbowRadar.getStopRange()

                display_variable.plot_ppi(self.__rainbowRadar.getRadarVariable()[1],
                                          colorbar_label=self.__rainbowRadar.getRadarVariable()[0],
                                          axislabels=(xlabel, ylabel),
                                          vmin=self.__rainbowRadar.getRadarVariable()[3],
                                          vmax=self.__rainbowRadar.getRadarVariable()[4],
                                          cmap=self.__rainbowRadar.getRadarVariable()[2])

                display_variable.set_limits(range, range)
                display_variable.plot_cross_hair(Rmax)

            display_variable.plot_range_rings(anillos, lw=0.5)

            self.__elevationImages[elevation] = fig2img(plt.gcf())

        return self.__elevationImages[elevation]

    def getImageFromCartesianGrid(self, elevation, figsize=(10, 10), paddingImg=1, basemapFlag=True,
                                  basemapShapeFile=None):
        plt.clf()
        if not elevation in self.__elevationImagesFromCartGrid:

            grilla = self.__rainbowRadar.getCartesianGrid(elevation)

            # create the plot
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(111)
            titulo = common.generate_title(self.__rainbowRadar.getRadar(), self.__rainbowRadar.getRadarVariable()[1], elevation)

            if basemapFlag:
                # Se genera el grafico con el mapa debajo
                grid_plot = GridMapDisplay(grilla)
                min_lat = self.__rainbowRadar.getMinLat(elevation) - paddingImg
                max_lat = self.__rainbowRadar.getMaxLat(elevation) + paddingImg
                min_lon = self.__rainbowRadar.getMinLon(elevation) - paddingImg
                max_lon = self.__rainbowRadar.getMaxLon(elevation) + paddingImg

                grid_plot.plot_basemap(min_lon=min_lon,max_lon=max_lon,min_lat=min_lat,max_lat=max_lat,auto_range=False,resolution='h')
                grid_plot.get_basemap()

                # Si hay un shapefile elegido por el usuario se toma ese, en otro caso se toma el shapefile por defecto
                if basemapShapeFile != None:
                    grid_plot.basemap.readshapefile(basemapShapeFile,
                                                    os.path.basename(basemapShapeFile))
                else:
                    grid_plot.basemap.readshapefile(os.path.dirname(__file__) + '/departamento/departamento', 'departamento',default_encoding='LATIN1')

                grid_plot.basemap.fillcontinents(lake_color='aqua',
                                                 alpha=0.2)


                grid_plot.plot_grid(self.__rainbowRadar.getRadarVariable()[1],
                                    colorbar_label=self.__rainbowRadar.getRadarVariable()[0],
                                    title=titulo,
                                    title_flag=True,
                                    vmin=self.__rainbowRadar.getRadarVariable()[3],
                                    vmax=self.__rainbowRadar.getRadarVariable()[4],
                                    cmap=self.__rainbowRadar.getRadarVariable()[2])

                grid_plot.plot_crosshairs(line_style='k--', linewidth=0.5)

            else:

                # Se genera el grafico comun con los anillos

                # Limites de la grilla
                range = [-self.__rainbowRadar.getStopRange() - paddingImg, self.__rainbowRadar.getStopRange() + paddingImg]
                # Shift para que el centro de la grafica sea (0,0)
                shift = (-self.__rainbowRadar.getStopRange(), self.__rainbowRadar.getStopRange(), -self.__rainbowRadar.getStopRange(), self.__rainbowRadar.getStopRange())

                # Se genera el grafico
                im = ax.imshow(grilla.fields[self.__rainbowRadar.getRadarVariable()[1]]['data'][0],
                               origin='origin',
                               vmin=self.__rainbowRadar.getRadarVariable()[3],
                               vmax=self.__rainbowRadar.getRadarVariable()[4],
                               cmap=self.__rainbowRadar.getRadarVariable()[2],
                               extent=shift)

                xlabel = 'Distancia en X (km)'
                ylabel = 'Distancia en Y (km)'

                plt.xlabel(xlabel)
                plt.ylabel(ylabel)
                plt.title(titulo)

                # Distancia entre los anillos
                rangoAnillos = self.__rainbowRadar.getStopRange() / 4
                anillos = [rangoAnillos, rangoAnillos * 2, rangoAnillos * 3, self.__rainbowRadar.getStopRange()]
                Rmax = self.__rainbowRadar.getStopRange()

                fig.colorbar(im, ax=ax, cax=None)

                # Se generan los anillos, se indican los limites y cross hair con los metodos estaticos de la clase RadarDisplay
                for range_ring_location_km in anillos:
                    RadarDisplay.plot_range_ring(range_ring_location_km, lw=0.5)

                RadarDisplay.set_limits(range, range)
                RadarDisplay.plot_cross_hair(Rmax)

            self.__elevationImagesFromCartGrid[elevation] = fig2img(plt.gcf())


        return self.__elevationImagesFromCartGrid[elevation]

    def showImage(self, elevation):
        self.getImageFromCartesianGrid(elevation).show()

    def saveImageToFile(self, elevation=0, figsize=(10, 10), paddingImg=0, pathOutput=None, fileOutput=None,
                        imageType=PNG, method='grid'):
        '''
        Guarda en un archivo el grafico de la elevacion seleccionada.

        :param elevation: Numero de elevacion a obtener
        :param figsize: Tupla que indica el tamaño de la imagen a generar
        :param paddingImg: Margen entre la imagen del radar y los limites de la imagen.
                            Si se usan los mapas de base (basemap) el valor representa la cantidad de grados.
        :param pathOutput: Carpeta destino. Por defecto, la carpeta del archivo .vol
        :param fileOutput: Archivo destino. Por defecto el nombre del archivo .vol__ele[elevation]
        :param imageType: Formato en que se va a almacenar la imagen.
        :param method:  Metodo por el cual se obtiene la imagen. 'grid' obtiene la imagen a partir de la grilla cartesiana y 'simple' genera la imagen con datos crudos.
        :return:
        '''
        elevationImg = None
        if method == 'grid':
            elevationImg = self.getImageFromCartesianGrid(elevation=elevation, figsize=figsize,
                                                          paddingImg=paddingImg)
        elif method == 'simple':
            elevationImg = self.getRawDataImage(elevation=elevation, figsize=figsize,
                                                paddingImg=paddingImg)
        else:
            raise Exception(
                "El metodo " + method + " no es un metodo valido para obtener la imagen. Posibles: [grid,simple] ")

        if (fileOutput != None and pathOutput != None):
            if imageType == JPEG:
                elevationImg.convert("RGB").save(
                    pathOutput + fileOutput + "_elevacion_" + str(elevation) + '.' + imageType)
            else:
                elevationImg.save(pathOutput + fileOutput + "_elevacion_" + str(elevation) + '.' + imageType)
        elif (fileOutput == None and pathOutput != None):
            if imageType == JPEG:
                elevationImg.convert("RGB").save(
                    pathOutput + self.__volFileName + "_elevacion_" + str(elevation) + '.' + imageType)
            else:
                elevationImg.save(pathOutput + self.__volFileName + "_elevacion_" + str(elevation) + '.' + imageType)
        elif (fileOutput != None and pathOutput == None):
            if imageType == JPEG:
                elevationImg.convert("RGB").save(self.__volPath + fileOutput + '.' + imageType)
            else:
                elevationImg.save(self.__volPath + fileOutput + '.' + imageType)
        else:
            if imageType == JPEG:
                elevationImg.convert("RGB").save(
                    self.__volPath + self.__volFileName + "_elevacion_" + str(elevation) + '.' + imageType)
            else:
                elevationImg.save(
                    self.__volPath + self.__volFileName + "_elevacion_" + str(elevation) + '.' + imageType)



    def saveToNETCDF(self, elevation, outFilePath, outFileName):
        pyart.io.write_grid(outFilePath + outFileName + "_elevacion_" + str(elevation) + ".grib",
                            self.__rainbowRadar.getCartesianGrid(elevation),
                            format='NETCDF3_64BIT',
                            arm_time_variables=True)

    def saveToGTiff(self, elevation, outFilePath, outFileName):

        grid = self.__rainbowRadar.getCartesianGrid(elevation)

        pyart.io.write_grid_geotiff(grid, filename=outFilePath + outFileName + "_elevacion_" + str(elevation) + ".tif",
                                    field=self.__rainbowRadar.getRadarVariable()[1],
                                    warp=False)