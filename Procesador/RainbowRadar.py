# -*- coding: utf-8 -*-
__author__ = "Andres Giordano"
__version__ = "1.0"
__maintainer__ = "Andres Giordano"
__email__ = "andresgiordano.unlu@gmail.com"
__status__ = "Produccion"

from .Utils import getBsp

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

        self.__elevationCartesianGrids = {}
        self.__mask = ''
        self.__radarVariable = None
        self.__filePath = vol_file_path
        self.__fileName = vol_file_name

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
        self.__applyMask(swp)
        return swp

    def getNSweeps(self):
        return self.__radar.nsweeps

    def getFilePath(self):
        return self.__filePath

    def getFileName(self):
        return self.__fileName

    def getStopRange(self):
        return self.__stopRange

    def getCartesianGrid(self, elevation, _bsp = 'calculate'):

        if not elevation in self.__elevationCartesianGrids:

            ele = self.getSweep(elevation)
            metros = 1000.0

            if _bsp == 'calculate':
                _bsp = getBsp(self.__stopRange, ele.fixed_angle['data'][0])
            elif _bsp == 'default':
                _bsp = 1.0
            elif type(_bsp) != float:
                raise Exception('Los valores posibles de BSP son \'calculate\', \'default\' o un float indicando el valor.')


            self.__elevationCartesianGrids[elevation] = pyart.map.grid_from_radars(
                (ele,),
                grid_shape=(1, 480, 480),
                grid_limits=((200, 4 * metros), (-self.__stopRange * metros, self.__stopRange * metros),
                             (-self.__stopRange * metros, self.__stopRange * metros)),
                weighting_function='Cressman',
                fields=[self.__radarVariable[1]],

                nb=ele.fixed_angle['data'][0],
                bsp=_bsp,

                roi_func='dist_beam',

                # Posición del RADAR
                grid_origin=(ele.latitude['data'][0], ele.longitude['data'][0])

            )

        return self.__elevationCartesianGrids[elevation]

    def getMaxLat(self,elevation):
        return self.getCartesianGrid(elevation).point_latitude['data'][0].max()

    def getMinLat(self, elevation):
        return self.getCartesianGrid(elevation).point_latitude['data'][0].min()

    def getMaxLon(self,elevation):
        return self.getCartesianGrid(elevation).point_longitude['data'][0].max()

    def getMinLon(self, elevation):
        return self.getCartesianGrid(elevation).point_longitude['data'][0].min()

    def setMask(self,maskString):
        self.__mask = maskString

    def __applyMask(self,swp):
        """
        Aplica la mascara establecida para el objeto radar. Se usa antes de devolver una elevacion especifica
        con :func:`~getSweep`.

        :param swp: objeto radar al cual se le aplica la mascara.
        :type swp: pyart.core.Radar
        """
        if self.__mask != '':
            a = swp.fields[self.getRadarVariable()[1]]['data']
            ma.masked_where(eval(self.__mask), a,copy=False)

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



