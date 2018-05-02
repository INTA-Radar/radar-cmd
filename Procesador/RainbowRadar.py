# -*- coding: utf-8 -*-
__author__ = "Andres Giordano"
__version__ = "1.0"
__maintainer__ = "Andres Giordano"
__email__ = "andresgiordano.unlu@gmail.com"
__status__ = "Produccion"

from Utils import radar_colormap,getBsp

import wradlib as wrl
import pyart.aux_io
import numpy.ma as ma

dBZ = ('dBZ', 'reflectivity', radar_colormap(), -30, 70)
ZDR = ('ZDR', 'differential_reflectivity', pyart.config.get_field_colormap('differential_reflectivity'), None, None)
RhoHV = ('RhoHV', 'cross_correlation_ratio', pyart.config.get_field_colormap('cross_correlation_ratio'), None, None)
uPhiDP = (
'uPhiDP', 'uncorrected_differential_phase', pyart.config.get_field_colormap('uncorrected_differential_phase'), None,
None)

class RainbowRadar(object):

    def __init__(self):
        self.__fileName = ""
        self.__filePath = ""
        self.__radar = None
        self.__elevationCartesianGrids = {}
        self.__mask = ''

    def readRadar(self, rainbowFilePath, rainbowFileName, radarVariable=dBZ):
        self.__filePath = rainbowFilePath
        self.__fileName = rainbowFileName
        self.__radar = pyart.aux_io.read_rainbow_wrl(self.__filePath + self.__fileName)
        self.__stopRange = int(
            wrl.io.get_RB_header(self.getFilePath() + self.getFileName())['volume']['scan']['pargroup']['stoprange'])

        if radarVariable[1] in self.__radar.fields:
            self.__radarVariable = radarVariable
        else:
            raise Exception("La variable elegida " + str(radarVariable[
                                                             0]) + " no se encuentra disponible en el archivo " + self.getFilePath() + self.getFileName())


    def getRadarVariable(self):
        return self.__radarVariable

    def getRadar(self):
        '''

        :return: Archivo de radar pyart.core.Radar
        :rtype:  pyart.core.Radar
        '''
        return self.__radar

    def getSweep(self, n):
        swp = self.__radar.extract_sweeps([n])
        self.__applyMask(swp,copy=False)
        return swp

    def getNSweeps(self):
        return self.__radar.nsweeps

    def getFilePath(self):
        return self.__filePath

    def getFileName(self):
        return self.__fileName

    def getStopRange(self):
        return self.__stopRange

    def getCartesianGrid(self, elevation):

        if not elevation in self.__elevationCartesianGrids:
            # ele = self.__radarData.extract_sweeps([elevation])
            ele = self.getSweep(elevation)
            metros = 1000.0

            self.__elevationCartesianGrids[elevation] = pyart.map.grid_from_radars(
                (ele,),
                grid_shape=(1, 480, 480),
                grid_limits=((200, 4 * metros), (-self.__stopRange * metros, self.__stopRange * metros),
                             (-self.__stopRange * metros, self.__stopRange * metros)),
                weighting_function='Cressman',
                fields=[self.__radarVariable[1]],

                nb=ele.fixed_angle['data'][0],
                bsp=getBsp(self.__stopRange, ele.fixed_angle['data'][0]),

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

    def __applyMask(self,swp,copy=True):
        if self.__mask != '':
            print self.__mask
            a = swp.fields[self.getRadarVariable()[1]]['data']
            ma.masked_where(eval(self.__mask), a,copy=copy)

    def getLatitude(self):
        return self.__radar.latitude['data'][0]

    def getLongitude(self):
        return self.__radar.longitude['data'][0]


