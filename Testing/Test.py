# -*- coding: utf-8 -*-

import sys

sys.path.extend(['../'])

import matplotlib.cbook
import warnings
import os

os.environ['PYART_QUIET'] = 'True'
warnings.filterwarnings("ignore", category=FutureWarning)

from Procesador.RainbowRadarProcessor import RainbowRadarProcessor
from Procesador.RainbowRadar import RainbowRadar,ZDR,dBZ,uPhiDP,RhoHV,V
from Procesador.Utils import PNG,JPEG
from Procesador.Precipitation import Precipitation

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)

files = {
'f_240_ZDR'     :   [ZDR,'datos/240/2009112306100500ZDR.vol'],
'f_240_dBZ'     :   [dBZ,'datos/240/2009112306100500dBZ.vol'],
'f_240_uPhiDP'  :   [uPhiDP,'datos/240/2009112306100500uPhiDP.vol'],
'f_240_RhoHV'   :   [RhoHV,'datos/240/2009112306100500RhoHV.vol'],
'f_480_dBZ'     :   [dBZ,'datos/480/2016122000073000dBZ.azi'],
'f_120_RhoHV'   :   [RhoHV,'datos/120/2009112306135000RhoHV.vol'],
'f_120_uPhiDP'  :   [uPhiDP,'datos/120/2009112306135000uPhiDP.vol'],
'f_120_dBZ'     :   [dBZ,'datos/120/2009112306135000dBZ.vol'],
'f_120_ZDR'     :   [ZDR,'datos/120/2009112306135000ZDR.vol'],
'f_x_dBZ'       :   [dBZ,'datos/2009112306135000dBZ.vol'],
'f_x_V'       :   [V,'datos/2015080902143600V.vol'],
'f_400_dBZ'       :   [dBZ,'datos/2018111211413100dBZ.azi']
}

files_precipitaciones = {
'f_240_P'       :   [dBZ,'datos/precipitaciones/2009122815300200dBZ.vol']
}


# Precipitaciones
for name,file in files_precipitaciones.items():
    print(name,' ; ',file)
    rr = RainbowRadar('',file[1], radarVariable=file[0])
    pp = Precipitation(rr)
    pp.computePrecipitations(0)
    p = RainbowRadarProcessor(rainbowRadar=pp.genRainRainbowRadar())
    p.saveImageToFile(imageType=PNG, pathOutput='res/', fileOutput=name,
                      image_method_params={'level': 0,
                                           'paddingImg': 1}
                      )
    p.saveImageToFile(imageType=JPEG, pathOutput='res/', fileOutput=name)

    p.saveImageToFile(imageType=PNG, pathOutput='res/', fileOutput=name + '_simple',
                      method='simple',
                      image_method_params={'elevation': 0,
                                           'paddingImg': 1}
                      )
    p.saveImageToFile(imageType=JPEG, pathOutput='res/', fileOutput=name + '_simple',
                      method='simple',
                      image_method_params={'elevation': 0,
                                           'paddingImg': 1})

    p.saveToGTiff(0, outFilePath='res/', outFileName=name)
    p.saveToNETCDF(outFilePath='res/', outFileName=name)


#################################################################
# Simple images

for name,file in files.items():
    print(name,' ; ',file)
    rr = RainbowRadar('',file[1], radarVariable=file[0])
    p = RainbowRadarProcessor(rainbowRadar=rr)

    p.saveImageToFile(imageType=PNG,  pathOutput='res/', fileOutput=name,
                      image_method_params = {'level': 0,
                                             'paddingImg':1})

    p.saveImageToFile(imageType=JPEG, pathOutput='res/', fileOutput=name,
                      image_method_params=  {'level': 0,
                                             'paddingImg': 1})

    p.saveImageToFile(imageType=PNG,pathOutput='res/', fileOutput=name+'_simple', method='simple',
                      image_method_params=  {'elevation': 0,
                                             'paddingImg': 1})

    p.saveImageToFile(imageType=JPEG, pathOutput='res/', fileOutput=name+'_simple', method='simple',
                      image_method_params=  {'elevation': 0,
                                             'paddingImg': 1})

    p.saveToGTiff(0, outFilePath='res/',outFileName=name)
    p.saveToNETCDF(outFilePath='res/',outFileName=name)


