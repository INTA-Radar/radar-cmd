# -*- coding: utf-8 -*-

from .RainbowRadar import RainbowRadar,dBZ,R
import pyart
import numpy as np

class Precipitation(object):
    """
    El objetivo de esta clase es procesar un objeto :class:`.RainbowRadar` con variable dBZ para computar el indice
    de precipitaciones (:func:`~computePrecipitations`). Luego, con la funcion :func:`~genRainRainbowRadar` se puede obtener
    un objeto :class:`.RainbowRadar` con la variable R cargada para poder procesarla con :class:`.RainbowRadarProcessor`
    """
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

        if self.__rainbowRadar.getRadarVariable() != dBZ:
            raise Exception("Solo se permite la variable dBZ para procesar precipitaciones")

        self.__volPath = self.__rainbowRadar.getFilePath()
        self.__volFileName = self.__rainbowRadar.getFileName()
        self.__RADAR_FILE_OUT = self.__volPath + self.__volFileName + "_ppi.grib"

        # Coeficientes en la estimacion de QPE
        # Convectivos para los NEXRAD

        self.__a = 300
        self.__b = 1.4
        self.__precipitationRadar = None

    def setA(self,a):
        self.__a = a

    def setB(self,b):
        self.__b = b

    def computePrecipitations(self,elevation=0,saveNetCDF=True):
        # Cuantos elementos hay ray y bins hay y cuales son las elevaciones

        self.__precipitationRadar = self.__rainbowRadar.getSweep(elevation)

        dbz = self.__rainbowRadar.getSweepData(elevation)

        fecha = self.__rainbowRadar.getAnio() + self.__rainbowRadar.getMes() + self.__rainbowRadar.getDia() + \
                self.__rainbowRadar.getHora()

        nb = self.__precipitationRadar.ngates
        nr = self.__precipitationRadar.nrays

        ## Transformo el dbz en mm6 m-3

        dbz_lineal = 10.0 ** (0.1 * dbz)

        rain_dbz = np.zeros((nr, nb))

        for j in range(0, nr):
            for h in range(0, nb):
                rain_dbz[j, h] = np.exp(np.log(dbz_lineal[j, h] / self.__a) / self.__b)

        rain = np.ma.masked_invalid(rain_dbz)

        ######## Agrego las nuevas variables filtradas a una nueva y las viejas a un solo archivo nc #####
        # Agrega la variable 'pp_dbz'
        self.__precipitationRadar.add_field_like('reflectivity', 'pp_dbz', rain, replace_existing=True)
        self.__precipitationRadar.fields['pp_dbz']['standard_name'] = 'Rain_Rate_with_reflectivity'

        if saveNetCDF:
            ####### GUARDO EL NUEVO NETCDF ############
            pyart.io.write_cfradial(self.__rainbowRadar.getFilePath() + fecha + '.nc', self.__precipitationRadar)

    def getRainData(self):
        """
        Retorna los datos de precipitaciones del ultimo resultado obtenido en 'computePrecipitations'.
        NO genera copia de los mismos.

        :return: datos de precipitaciones calculados.
        """

        return self.__precipitationRadar.fields['pp_dbz']['data']



    def genRainRainbowRadar(self):
        """
        Genera una instancia de RainbowRadar con los datos calculados de precipitacion. Usa la variable R de RainbowRadar.

        :return: instancia de RainbowRadar con los datos de la precipitacion.
        :rtype: RainbowRadar
        """
        return RainbowRadar(self.__rainbowRadar.getFilePath(),
                            self.__rainbowRadar.getFileName(),
                            radarVariable=R,
                            radar=self.__precipitationRadar)