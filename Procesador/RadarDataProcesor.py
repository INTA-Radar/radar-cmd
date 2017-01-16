# -*- coding: utf-8 -*-
__author__ = "Andres Giordano"
__version__ = "1.0"
__maintainer__ = "Andres Giordano"
__email__ = "andresgiordano.unlu@gmail.com"
__status__ = "Produccion"

from pylab import *
import Image
import matplotlib.pyplot as plt
from scipy.stats import linregress
from geopy.distance import vincenty
from matplotlib import colors
import numpy
import os.path
import pyart.aux_io
from pyart.graph import RadarDisplay,common,GridMapDisplay,RadarMapDisplay
import pyart.map
import pyart.config
import wradlib as wrl
import pyart.io

def radar_colormap():
    nws_reflectivity_colors = [
        "#646464",  # ND
        "#ccffff",  # -30
        "#cc99cc",  # -25
        "#996699",  # -20
        "#663366",  # -15
        "#cccc99",  # -10
        "#999966",  # -5
        "#646464",  # 0
        "#04e9e7",  # 5
        "#019ff4",  # 10
        "#0300f4",  # 15
        "#02fd02",  # 20
        "#01c501",  # 25
        "#008e00",  # 30
        "#fdf802",  # 35
        "#e5bc00",  # 40
        "#fd9500",  # 45
        "#fd0000",  # 50
        "#d40000",  # 55
        "#bc0000",  # 60
        "#f800fd",  # 65
        "#9854c6",  # 70
        "#fdfdfd"  # 75
    ]

    cmap = mpl.colors.ListedColormap(nws_reflectivity_colors)
    return cmap

def fig2data(fig):
    """
    @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
    @param fig a matplotlib figure
    @return a numpy 3D array of RGBA values
    """
    # draw the renderer
    fig.canvas.draw()

    # Get the RGBA buffer from the figure
    w, h = fig.canvas.get_width_height()
    buf = numpy.fromstring(fig.canvas.tostring_argb(), dtype=numpy.uint8)
    buf.shape = (w, h, 4)

    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = numpy.roll(buf, 3, axis=2)
    return buf

def fig2img(fig):
    """
    @brief Convert a Matplotlib figure to a PIL Image in RGBA format and return it
    @param fig a matplotlib figure
    @return a Python Imaging Library ( PIL ) image
    """
    # put the figure pixmap into a numpy array
    buf = fig2data(fig)
    w, h, d = buf.shape
    return Image.frombytes("RGBA", (w, h), buf.tostring())

# bsp = { 'stoprange': { 'degrees':'bsp'}}
bsp =   {120:    {0.5:2,
                    1.3:1.3,
                    2.3:1.1,
                    3.5:1.05,
                    5:1.02,
                    6.9:1,
                    9.1:0.99,
                    11.8:0.9769,
                    15.1:0.9729,
                    19.2:0.97},
         240: {0.5: 2.56,
                   0.9:1.85,
                   1.3: 1.58,
                   1.9:1.36,
                   2.3: 1.285,
                   3:1.2,
                   3.5: 1.165,
                   5: 1.1,
                   6.9: 1.06,
                   9.1: 1.035,
                   11.8: 1.015,
                   15.1: 1.004,
                   19.2: 1},
         480:{0.3:6.3}
            }

PNG = 'png'
JPEG = 'jpeg'

dBZ = ('dBZ', 'reflectivity',radar_colormap(),-30,70)
ZDR = ('ZDR', 'differential_reflectivity',pyart.config.get_field_colormap('differential_reflectivity'),None,None)
RhoHV = ('RhoHV', 'cross_correlation_ratio',pyart.config.get_field_colormap('cross_correlation_ratio'),None,None)
uPhiDP = ('uPhiDP', 'uncorrected_differential_phase',pyart.config.get_field_colormap('uncorrected_differential_phase'),None,None)

def getBsp(stopRange, nb):

    if nb in bsp[stopRange]:
        return bsp[stopRange][nb]
    else:
        # Obtengo el bsp haciendo una regresion lineal entre X=nb e Y=(nb*bsp)
        print
        print 'Obteniendo bsp por regresion lineal. Stoprange =',stopRange,' nb =',nb

        Y = [y for y in bsp[stopRange].itervalues()]
        X = [x for x in bsp[stopRange].iterkeys()]

        i = 0
        for y in Y:
            print y
            print X[i]
            Y[i] = y * X[i]
            i += 1

        print 'nb =',X
        print 'nb*bsp =',Y
        coeffs = linregress(X, Y)

        # Si el r-cuad da 0.0 quiere decir que no se pudo generar una regresion lineal.
        # Esto pasa cuando existe un unico punto.

        if coeffs[2]==0.0 :
            raise Exception('No se pudo crear una regresion lineal para '+str(stopRange)+'km')

        print 'Funcion a usar = ' + str(coeffs[0])+'*nb+'+str(coeffs[1])
        print 'Coeficiente de correlacion R-cuad = ',coeffs[2]
        print 'Bsp = (' + str(coeffs[0]) + '*nb + ' + str(coeffs[1]) + ')/nb'
        bsp_val = (coeffs[0]*nb+coeffs[1])/nb
        print 'Bsp = ',bsp_val
        print
        return bsp_val

class RainbowRadar(object):

    def __init__(self):
        self.__fileName = ""
        self.__filePath = ""
        self.__radar = None

    def readRadar(self,rainbowFilePath, rainbowFileName):
        self.__filePath = rainbowFilePath
        self.__fileName = rainbowFileName
        self.__radar = pyart.aux_io.read_rainbow_wrl(self.__filePath+self.__fileName)
        self.__stopRange = int(wrl.io.get_RB_header(self.getFilePath() + self.getFileName())['volume']['scan']['pargroup']['stoprange'])

    def getRadar(self):
        return self.__radar

    def getSweep(self,n):
        self.__radar.extract_sweeps([n])

    def getNSweeps(self):
        return self.__radar.nsweeps

    def getFilePath(self):
        return  self.__filePath

    def getFileName(self):
        return self.__fileName

    def getStopRange(self):
        return self.__stopRange

class RainbowRadarProcessor(object):
    """
    @param sweepDistance: indica la distancia de la señal lanzada por el radar. Se usa para ajustar los graficos y crear los anillos
    @param radarVariable: se usa para indicar el tipo de variable que contienen los datos del archivo

    """


    def __init__(self, rainbowRadar, radarVariable=dBZ):

        self.__rainbowRadar = None

        if isinstance(rainbowRadar,RainbowRadar):
            self.__rainbowRadar = rainbowRadar
        else:
            raise Exception("El parametro rainbowRadar no es una instancia de RainbowRadar")

        self.__volPath = self.__rainbowRadar.getFilePath()
        self.__volFileName = self.__rainbowRadar.getFileName()
        self.__radarData = self.__rainbowRadar.getRadar()


        if radarVariable[1] in self.__radarData.fields:
            self.__radarVariable = radarVariable
        else:
            raise Exception("La variable elegida "+str(radarVariable[0])+ " no se encuentra disponible en el archivo "+self.__rainbowRadar.getFilePath()+self.__rainbowRadar.getFileName())

        self.__stopRange = self.__rainbowRadar.getStopRange()
        self.__elevationImages = {}
        self.__elevationImagesFromCartGrid = {}
        self.__elevationCartesianGrids = {}
        self.__RADAR_FILE_OUT = self.__volPath+self.__volFileName+"_ppi.grib"

    def getRadarData(self):
        '''Devuelve un objeto de tipo Radar con los datos del volumen'''
        return self.__radarData

    def getRawDataImage(self, elevation, figsize=(10, 10), paddingImg=5, basemapFlag=True, basemapShapeFile=None):
        '''

        Este metodo retorna la imagen bidimensional del retorno radarico segun
        el numero de elevacion que se pase por parametro.

        @param elevation es el numero de elevacion a obtener
        @param figsize es una tupla que indica el tamaño de la imagen a generar
        @param paddingImg se usa para agregarle un borde en blanco a la imagen
        '''

        if not elevation in self.__elevationImages:

            eleN = self.__radarData.extract_sweeps([elevation])
            display_variable = RadarDisplay(eleN)

            fig = plt.figure(figsize=figsize)
            fig.add_subplot(1, 1, 1, aspect=1.0)
            rangoAnillos = self.__stopRange / 4
            anillos = [rangoAnillos, rangoAnillos * 2, rangoAnillos * 3, self.__stopRange]

            if basemapFlag:
                display_variable = RadarMapDisplay(eleN)
                # Si hay un shapefile elegido por el usuario se toma ese, en otro caso se toma el shapefile por defecto
                if basemapShapeFile != None:

                    display_variable.plot_ppi_map(self.__radarVariable[1],
                                                  colorbar_label=self.__radarVariable[0],
                                                  vmin=self.__radarVariable[3],
                                                  vmax=self.__radarVariable[4],
                                                  cmap=self.__radarVariable[2],
                                                  shapefile=basemapShapeFile)
                else:
                    display_variable.plot_ppi_map(self.__radarVariable[1],
                                                  colorbar_label=self.__radarVariable[0],
                                                  vmin=self.__radarVariable[3],
                                                  vmax=self.__radarVariable[4],
                                                  cmap=self.__radarVariable[2],
                                                  shapefile=os.path.dirname(
                                                      __file__) + '/DEPARTAMENTOS_2D/departamentos_2d')
                    display_variable.basemap.fillcontinents(lake_color='aqua',
                                                            alpha=0.2)
            else:
                xlabel = 'Distancia en X (km)'
                ylabel = 'Distancia en Y (km)'

                range = [-self.__stopRange - paddingImg, self.__stopRange + paddingImg]

                Rmax = self.__stopRange

                display_variable.plot_ppi(self.__radarVariable[1],
                                          colorbar_label=self.__radarVariable[0],
                                          axislabels=(xlabel, ylabel),
                                          vmin=self.__radarVariable[3],
                                          vmax=self.__radarVariable[4],
                                          cmap=self.__radarVariable[2])

                display_variable.set_limits(range, range)
                display_variable.plot_cross_hair(Rmax)

            display_variable.plot_range_rings(anillos, lw=0.5)


            self.__elevationImages[elevation] = fig2img(plt.gcf())

        return self.__elevationImages[elevation]

    def getImageFromCartesianGrid(self, elevation, figsize=(10, 10), paddingImg=10, basemapFlag=True, basemapShapeFile=None):

        if not elevation in self.__elevationImagesFromCartGrid:

            grilla = self.getCartesianGrid(elevation)

            # create the plot
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(111)
            titulo = common.generate_title(self.__radarData, self.__radarVariable[1], elevation)

            if basemapFlag:
                # Se genera el grafico con el mapa debajo
                grid_plot = GridMapDisplay(grilla)
                grid_plot.get_basemap()

                # Si hay un shapefile elegido por el usuario se toma ese, en otro caso se toma el shapefile por defecto
                if basemapShapeFile != None:
                    grid_plot.basemap.readshapefile(basemapShapeFile,
                                                    os.path.basename(basemapShapeFile))
                else:
                    grid_plot.basemap.readshapefile(os.path.dirname(__file__)+'/DEPARTAMENTOS_2D/departamentos_2d',
                                                'departamentos')

                grid_plot.basemap.fillcontinents(lake_color='aqua',
                                                 alpha=0.2)
                grid_plot.plot_grid(self.__radarVariable[1],
                                    colorbar_label=self.__radarVariable[0],
                                    title=titulo,
                                    title_flag=True,
                                    vmin=self.__radarVariable[3],
                                    vmax=self.__radarVariable[4],
                                    cmap=self.__radarVariable[2])

                grid_plot.plot_crosshairs(line_style='k--', linewidth=0.5)

            else:

                # Se genera el grafico comun con los anillos

                #Limites de la grilla
                range = [-self.__stopRange - paddingImg, self.__stopRange + paddingImg]
                # Shift para que el centro de la grafica sea (0,0)
                shift = (-self.__stopRange, self.__stopRange, -self.__stopRange, self.__stopRange)

                # Se genera el grafico
                im = ax.imshow(grilla.fields[self.__radarVariable[1]]['data'][0],
                               origin='origin',
                               vmin=self.__radarVariable[3],
                               vmax=self.__radarVariable[4],
                               cmap=self.__radarVariable[2],
                               extent=shift)

                xlabel = 'Distancia en X (km)'
                ylabel = 'Distancia en Y (km)'

                plt.xlabel(xlabel)
                plt.ylabel(ylabel)
                plt.title(titulo)

                # Distancia entre los anillos
                rangoAnillos = self.__stopRange / 4
                anillos = [rangoAnillos, rangoAnillos * 2, rangoAnillos * 3, self.__stopRange]
                Rmax = self.__stopRange


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
                        imageType=PNG,method='grid'):
        '''
        Guarda en un archivo el grafico de la elevacion seleccionada.

        @param elevation es el numero de elevacion a obtener
        @param pathOutput carpeta destino. Por defecto, la carpeta del archivo .vol
        @param fileOutput  archivo destino. Por defecto el nombre del archivo .vol__ele[elevation]
        @param figsize es una tupla que indica el tamaño de la imagen a generar
        @param paddingImg se usa para agregarle un borde en blanco a la imagen
        @param imageType es el formato de la imagen en que se va a guardar la imagen
        '''
        elevationImg = None
        if method == 'grid':
            elevationImg = self.getImageFromCartesianGrid(elevation=elevation, figsize=figsize,
                                                      paddingImg=paddingImg)
        elif method == 'simple':
            elevationImg = self.getRawDataImage(elevation=elevation, figsize=figsize,
                                                          paddingImg=paddingImg)
        else:
            raise Exception("El metodo "+method+" no es un metodo valido para obtener la imagen. Posibles: [grid,simple] ")

        if (fileOutput != None and pathOutput != None):
            elevationImg.save(pathOutput + fileOutput+"_elevacion_"+str(elevation) + '.' + imageType)
        elif (fileOutput == None and pathOutput != None):
            elevationImg.save(pathOutput + self.__volFileName + "_elevacion_" + str(elevation) + '.' + imageType)
        elif (fileOutput != None and pathOutput == None):
            elevationImg.save(self.__volPath + fileOutput + '.' + imageType)
        else:
            elevationImg.save(self.__volPath + self.__volFileName + "_elevacion_" + str(elevation) + '.' + imageType)

    def getCartesianGrid(self, elevation):

        if not elevation in self.__elevationCartesianGrids:

            ele = self.__radarData.extract_sweeps([elevation])
            metros = 1000.0

            self.__elevationCartesianGrids[elevation] = pyart.map.grid_from_radars(
                (ele,),
                grid_shape=(1, 480, 480),
                grid_limits=((200, 4*metros), (-self.__stopRange * metros, self.__stopRange * metros), (-self.__stopRange * metros, self.__stopRange * metros)),
                weighting_function='Cressman',
                fields=[self.__radarVariable[1]],

                nb=ele.fixed_angle['data'][0],
                bsp=getBsp(self.__stopRange,ele.fixed_angle['data'][0]),

                roi_func='dist_beam',

                # Posición del RADAR
                grid_origin=(ele.latitude['data'][0], ele.longitude['data'][0])

            )
        return self.__elevationCartesianGrids[elevation]

    def saveToNETCDF(self,elevation,outFilePath,outFileName):
        pyart.io.write_grid(outFilePath + outFileName +"_elevacion_" + str(elevation) +".grib",
                            self.getCartesianGrid(elevation),
                            format='NETCDF3_64BIT',
                            arm_time_variables=True)

    def saveToGTiff(self,elevation, outFilePath,outFileName):

        grid = self.getCartesianGrid(elevation)

        pyart.io.write_grid_geotiff(grid, filename=outFilePath+outFileName+"_elevacion_"+str(elevation)+".tif",
                                    field=self.__radarVariable[1],
                                    warp=False)

class MosaicGenerator(object):

    def __init__(self,radarVariable=dBZ, radars=None):

        self.__radars = []
        self.__mosaicGrids = {}
        self.__mosaicImages = {}
        self.__radarVariable=radarVariable


        if radars != None:
            for radar in radars:
                self.addRadar(radar)

    def addRadar(self,radar):
        if isinstance(radar, RainbowRadar):
            if self.__radarVariable != None:
                if self.__radarVariable[1] in radar.getRadar().fields:
                    self.__radars.append(radar)
                else:
                    raise Exception("La variable elegida " +
                                    str(self.__radarVariable[0]) + " no se encuentra disponible en el archivo " + radar.getFilePath() + radar.getFileName())
        else:
            raise Exception("El parametro 'radar' no es un objeto del tipo RainbowRadar")

    def getMosaicGrid(self,elevation=0):

        if elevation not in self.__mosaicGrids:

            # Verificamos que se haya cargado  al menos dos radares
            if len(self.__radars)<=1:
                raise Exception("No se han cargado radares suficientes para generar un mosaico")

            # Verifico que todos los radares hagan un barrido de la misma distancia (en km) ya que influye en el valor de nb y bsp.
            stopRange = self.__radars[0].getStopRange()
            for radar in self.__radars:
                if radar.getStopRange() != stopRange:
                    raise Exception("Los rangos de los radares son diferentes. Solo se permite que sean todos de 120km , 240km o 480km")

            # Obtengo las coordenadas de todos los radares
            points = []
            for radar in self.__radars:
                points.append((radar.getRadar().latitude['data'][0], radar.getRadar().longitude['data'][0]))

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

            #max_lat =max(lats)
            max_lat_point = (max_lat, longitude_center)

            # Obtengo todas las longitudes
            longs = [p[1] for p in points]

            # Punto de maxima longitud
            actual_max = 0
            max_long = longitude_center
            for l in longs:
                dif = abs(abs(longitude_center)-abs(l))
                if dif > actual_max:
                    actual_max = dif
                    max_long = l

            #max_long = max(longs)

            max_long_point = (latitude_center, max_long)

            # Obtengo las distancias entre el punto central y el de maxima longitud y el de maxima latitud

            distances = [vincenty(center_point, max_lat_point, ellipsoid=elipse).meters,vincenty(center_point,max_long_point,ellipsoid=elipse).meters]

            # Valor de ajuste en km
            adjust = 3

            #Obtengo la maxima distancia
            meters = 1000
            max_distance = max(distances)
            limit = ((adjust + stopRange)*meters) + max_distance

            # Obtengo los sweeps en base a la elevacion
            radar_sweeps = []
            for radar in self.__radars:
                radar_sweeps.append(radar.getRadar().extract_sweeps([elevation]))

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
                bsp=getBsp(stopRange,radar_sweeps[0].fixed_angle['data'][0]),
                grid_origin=center_point,
                fields=[self.__radarVariable[1]]
            )

            self.__mosaicGrids[elevation] = grid

        return self.__mosaicGrids[elevation]

    def getMosaicImage(self,elevation):

        if elevation not in self.__mosaicImages:
            grid = self.getMosaicGrid(elevation)

            titulo = common.generate_title(self.__radars[0].getRadar(), self.__radarVariable[1], elevation)

            grid_plot = GridMapDisplay(grid)
            grid_plot.plot_grid(self.__radarVariable[1],
                                colorbar_label=self.__radarVariable[0],
                                title=titulo,
                                title_flag=True,
                                vmin=self.__radarVariable[3],
                                vmax=self.__radarVariable[4],
                                cmap=self.__radarVariable[2])
            grid_plot.plot_basemap(resolution='h')

            self.__mosaicImages[elevation] = fig2img(plt.gcf())

        return self.__mosaicImages[elevation]

    def saveImageToFile(self, pathOutput, fileOutput, elevation=0, imageType=PNG):

        elevationImg = self.getMosaicImage(elevation=elevation)

        elevationImg.save(pathOutput + fileOutput+"_elevacion_"+str(elevation) + '.' + imageType)

    def saveToNETCDF(self,elevation,filePath,fileName):
        pyart.io.write_grid(filePath+fileName+"_elevacion_"+str(elevation)+".grib",
                            self.getMosaicGrid(elevation),
                            format='NETCDF3_64BIT',
                            arm_time_variables=True)

    def saveToGTiff(self,elevation,outFilePath,outFileName):

        grid = self.getMosaicGrid(elevation)

        pyart.io.write_grid_geotiff(grid, filename=outFilePath+outFileName
                                                   + "_elevacion_" + str(elevation) + ".tif",
                                    field=self.__radarVariable[1],
                                    warp=False)



