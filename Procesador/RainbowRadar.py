# -*- coding: utf-8 -*-

__author__ = "Andres Giordano"
__version__ = "1.0"
__maintainer__ = "Andres Giordano"
__email__ = "andresgiordano.unlu@gmail.com"
__status__ = "Produccion"

import wradlib as wrl
import pyart.aux_io
import numpy.ma as ma

#var_name = (var_id, pyart_variable, cmap, vmin, vmax, colorbar_label)
dBZ = ('dBZ', 'reflectivity', pyart.config.get_field_colormap('reflectivity'), -30, 70, 'Reflectivity') # Pasado a pyart_NWSRef en base a actualizacion Diciembre 2018
V = ('V', 'velocity', pyart.config.get_field_colormap('velocity'), None, None,'Velocidad Doppler')
ZDR = ('ZDR', 'differential_reflectivity', pyart.config.get_field_colormap('differential_reflectivity'), None, None, 'Differential Reflectivity')
RhoHV = ('RhoHV', 'cross_correlation_ratio', pyart.config.get_field_colormap('cross_correlation_ratio'), None, None, 'Cross correlation ratio')
uPhiDP = (
'uPhiDP', 'uncorrected_differential_phase', pyart.config.get_field_colormap('uncorrected_differential_phase'), None,
            None, 'Uncorrected Differential Pphase')

R = ('R', 'pp_dbz', 'pyart_NWSRef', 0, 300,'mm/hr')

class RainbowRadar(object):

    def __init__(self, vol_file_path, vol_file_name, radarVariable=dBZ, radar = None):

        self.__mask = ''
        self.__radarVariable = None
        self.__filePath = vol_file_path
        self.__fileName = vol_file_name
        self.__grid = None

        if radar is None:
            self.__radar = pyart.aux_io.read_rainbow_wrl(self.__filePath + self.__fileName)
        else:
            self.__radar = radar

        self.__stopRange = int(
            wrl.io.get_RB_header(self.getFilePath() + self.getFileName())['volume']['scan']['pargroup']['stoprange'])

        if radarVariable[1] in self.__radar.fields:
            self.__radarVariable = radarVariable
        else:
            raise Exception("La variable elegida " + str(radarVariable[
                                                             1]) + " no se encuentra disponible en el archivo " + self.getFilePath() + self.getFileName())

    def getRadarVariable(self):
        return self.__radarVariable

    def getRadar(self):
        """

        :return: Archivo de radar pyart.core.Radar
        :rtype:  pyart.core.Radar
        """

        return self.__radar

    def getSweepData(self,elevation,field=None):
        if field is None:
            return self.getSweep(elevation).fields[self.__radarVariable[1]]['data']
        else:
            return self.getSweep(elevation).fields[field]['data']

    def getSweep(self, n):
        swp = self.__radar.extract_sweeps([n])
        return swp

    def getNSweeps(self):
        return self.__radar.nsweeps

    def getFilePath(self):
        return self.__filePath

    def getFileName(self):
        return self.__fileName

    def getStopRange(self):
        return self.__stopRange

    def getCartesianGrid(self):

        if self.__grid is None:

            metros = 1000.0

            z = 29
            self.__grid = pyart.map.grid_from_radars(
                (self.__radar,),
                grid_shape=(z, 480, 480),
                grid_limits=((0, z * metros), (-self.__stopRange * metros, self.__stopRange * metros),
                             (-self.__stopRange * metros, self.__stopRange * metros)),
                #weighting_function='Cressman',
                fields=[self.__radarVariable[1]],
                min_radius=1100,
                grid_origin=(self.getLatitude(), self.getLongitude())

            )

        return self.__grid

    def getMaxLat(self):
        return self.getCartesianGrid().point_latitude['data'][0].max()

    def getMinLat(self):
        return self.getCartesianGrid().point_latitude['data'][0].min()

    def getMaxLon(self):
        return self.getCartesianGrid().point_longitude['data'][0].max()

    def getMinLon(self):
        return self.getCartesianGrid().point_longitude['data'][0].min()

    def setMask(self,maskString,dst='grid', level=None):
        """
        Aplica una mascara a los datos del radar o la grilla generada.

        :param maskString: string que indica la mascara. Debe respetar el formato de numpy
        :param dst: destino de la mascara. Si se elige 'grid' se aplica a la grilla, 'raw' aplica directo
        sobre los datos originales del radar, en este ultimo caso tener en cuenta que luego si se hace el grillado
        habra datos que no estarán disponibles (a los que se le aplico la mascara)
        :param level: nivel a donde se aplica la mascara, si es None se aplica a todos los niveles de la grilla.

        """
        if maskString != '':

            if dst == 'grid':
                if self.__grid is not None:
                    if level is not None:
                        a = self.__grid.fields[self.getRadarVariable()[1]]['data'][level]
                        ma.masked_where(eval(maskString), a, copy=False)
                    else:
                        for x in range(len(self.__grid.fields[self.getRadarVariable()[1]]['data'])):
                            a = self.__grid.fields[self.getRadarVariable()[1]]['data'][x]
                            ma.masked_where(eval(maskString), a, copy=False)
                else:
                    raise Exception('La grilla aun no ha sido creada')
            elif dst == 'raw':
                a = self.__radar.fields[self.getRadarVariable()[1]]['data']
                ma.masked_where(eval(maskString), a, copy=False)
            else:
                raise Exception('Opcion no reconocida')


    def getLatitude(self):
        return self.__radar.latitude['data'][0]

    def getLongitude(self):
        return self.__radar.longitude['data'][0]

    def getAnio(self):
        return self.__radar.time['units'][14:18]

    def getMes(self):
        return self.__radar.time['units'][19:21]

    def getDia(self):
        return self.__radar.time['units'][22:24]

    def getHora(self):
        return self.__radar.time['units'][25:27] + self.__radar.time['units'][28:30]



