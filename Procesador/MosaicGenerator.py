from RainbowRadar import RainbowRadar
from geopy.distance import vincenty
import setuptools
import pyart.map
from Utils import getBsp,fig2img,PNG,JPEG
from pyart.graph import common, GridMapDisplay
import os
import matplotlib.pyplot as plt

class MosaicGenerator(object):

    def __init__(self, radars=None):
        '''

        :param radarVariable:
        :param radars: list of RainbowRadar
        :type radars: list of RainbowRadar
        '''
        self.__radars = []
        self.__mosaicGrids = {}
        self.__mosaicImages = {}

        if radars != None:
            for radar in radars:
                self.addRadar(radar)

    def addRadar(self, radar):
        if isinstance(radar, RainbowRadar):
            self.__radars.append(radar)
        else:
            raise Exception("El parametro 'radar' no es un objeto del tipo RainbowRadar")

    def getMosaicGrid(self, elevation=0):

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

            # Obtengo las coordenadas de todos los radares
            points = []
            for radar in self.__radars:
                points.append((radar.getLatitude(), radar.getLongitude()))

            # Ahora voy a calcular el punto medio de los N radares. Simplemente sumo las latitudes y las longitudes cada una
            # por su lado, luego promedio por la cantidad de radares.
            latitude_sum = 0
            longitude_sum = 0

            for p in points:
                latitude_sum += p[0]
                longitude_sum += p[1]

            latitude_center = latitude_sum / len(points)
            longitude_center = longitude_sum / len(points)

            center_point = (latitude_center, longitude_center)

            # Ahora vamos a calcular la cantidad de metros que tiene que abarcar la grilla para contener a los N radares.
            # Para lograr esto calculamos el radar con maxima latitud y el radar con maxima longitud (puede ser el mismo), luego
            # para el punto de maxima latitud fijamos su longitud a la longitud del punto central y luego calculamos la distancia
            # entre estos puntos. Lo mismo para el punto de maxima longitud pero fijando la latitud (siempre la distancia es en metros).
            # Luego, se agregara el rango de barrido del radar en kilometros mas un valor de ajuste (1 o 2 kilometros mas) para que entren
            # perfectamente todos los radares en la grilla.
            #
            #

            elipse = 'WGS-84'

            # Obtengo todas las latitudes
            lats = [p[0] for p in points]

            # Punto de maxima latitud
            actual_max = 0
            max_lat = latitude_center
            for l in lats:
                dif = abs(abs(latitude_center) - abs(l))
                if dif > actual_max:
                    actual_max = dif
                    max_lat = l

            # max_lat =max(lats)
            max_lat_point = (max_lat, longitude_center)

            # Obtengo todas las longitudes
            longs = [p[1] for p in points]

            # Punto de maxima longitud
            actual_max = 0
            max_long = longitude_center
            for l in longs:
                dif = abs(abs(longitude_center) - abs(l))
                if dif > actual_max:
                    actual_max = dif
                    max_long = l

            # max_long = max(longs)

            max_long_point = (latitude_center, max_long)

            # Obtengo las distancias entre el punto central y el de maxima longitud y el de maxima latitud

            distances = [vincenty(center_point, max_lat_point, ellipsoid=elipse).meters,
                         vincenty(center_point, max_long_point, ellipsoid=elipse).meters]

            # Valor de ajuste en km
            adjust = 3

            # Obtengo la maxima distancia
            meters = 1000
            max_distance = max(distances)
            limit = ((adjust + stopRange) * meters) + max_distance

            # Obtengo los sweeps en base a la elevacion
            radar_sweeps = []
            for radar in self.__radars:
                radar_sweeps.append(radar.getSweep(elevation))

            # Ahora genero la grilla en base a los datos anteriores:
            grid = pyart.map.grid_from_radars(
                tuple(radar_sweeps),
                grid_shape=(1, 480 * len(self.__radars), 480 * len(self.__radars)),
                grid_limits=(
                    (200, 4 * meters),
                    (-limit, limit),
                    (-limit, limit)
                ),
                nb=radar_sweeps[0].fixed_angle['data'][0],
                bsp=getBsp(stopRange, radar_sweeps[0].fixed_angle['data'][0]),
                grid_origin=center_point,
                fields=[self.__radars[0].getRadarVariable()[1]]
            )

            self.__mosaicGrids[elevation] = grid

        return self.__mosaicGrids[elevation]

    def getMosaicImage(self, elevation):
        plt.clf()
        if elevation not in self.__mosaicImages:
            grid = self.getMosaicGrid(elevation)

            titulo = common.generate_title(self.__radars[0].getRadar(), self.__radars[0].getRadarVariable()[1], elevation)

            grid_plot = GridMapDisplay(grid)
            grid_plot.plot_grid(self.__radars[0].getRadarVariable()[1],
                                colorbar_label=self.__radars[0].getRadarVariable()[0],
                                title=titulo,
                                title_flag=True,
                                vmin=self.__radars[0].getRadarVariable()[3],
                                vmax=self.__radars[0].getRadarVariable()[4],
                                cmap=self.__radars[0].getRadarVariable()[2])
            grid_plot.plot_basemap(resolution='h')
            grid_plot.basemap.readshapefile(os.path.dirname(__file__) + '/DEPARTAMENTOS_2D/departamentos_2d',
                                            'departamentos')

            self.__mosaicImages[elevation] = fig2img(plt.gcf())

        return self.__mosaicImages[elevation]

    def saveImageToFile(self, pathOutput, fileOutput, elevation=0, imageType=PNG):

        elevationImg = self.getMosaicImage(elevation=elevation)

        if imageType == JPEG:
            elevationImg.convert("RGB").save(pathOutput + fileOutput + "_elevacion_" + str(elevation) + '.' + imageType)
        else:
            elevationImg.save(pathOutput + fileOutput + "_elevacion_" + str(elevation) + '.' + imageType)

    def saveToNETCDF(self, elevation, filePath, fileName):
        pyart.io.write_grid(filePath + fileName + "_elevacion_" + str(elevation) + ".grib",
                            self.getMosaicGrid(elevation),
                            format='NETCDF3_64BIT',
                            arm_time_variables=True)

    def saveToGTiff(self, elevation, outFilePath, outFileName):

        grid = self.getMosaicGrid(elevation)

        pyart.io.write_grid_geotiff(grid, filename=outFilePath + outFileName
                                                   + "_elevacion_" + str(elevation) + ".tif",
                                    field=self.__radars[0].getRadarVariable()[1],
                                    warp=False)
