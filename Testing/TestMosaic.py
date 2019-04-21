# -*- coding: utf-8 -*-

import sys

sys.path.extend(['../'])

import matplotlib.cbook
import warnings
import os

os.environ['PYART_QUIET'] = 'True'
warnings.filterwarnings("ignore", category=FutureWarning)


from Procesador.RainbowRadar import RainbowRadar,dBZ
from Procesador.MosaicGenerator import MosaicGenerator
from Procesador.Utils import PNG,JPEG


warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)


files_mosaico = {
'Mosaico_PER_dBZ':  [dBZ,'datos/Mosaico/240/PER/2016122616204500dBZ.vol'],
'Mosaico_PAR_dBZ':  [dBZ,'datos/Mosaico/240/PAR/2016122616200500dBZ.vol'],
'Mosaico_ANG_dBZ':  [dBZ,'datos/Mosaico/240/ANG/2016122616200300dBZ.vol']

}

#################################################################
# Mosaic


radars = []
for name,file in files_mosaico.items():
    print(name, ' ; ', file)
    radar = RainbowRadar('',file[1], radarVariable=dBZ)
    radars.append(radar)

mg = MosaicGenerator(radars=radars)

# Sin mascara
print('Sin mascara')
mg.saveImageToFile(imageType=PNG, pathOutput='res/', fileOutput='mosaico',image_params={'level':0})
mg.saveImageToFile(imageType=JPEG, pathOutput='res/', fileOutput='mosaico',image_params={'level':0})
mg.saveToGTiff(0, outFilePath='res/',outFileName='mosaico')
mg.saveToNETCDF('res/','mosaico')
# Con mascara
print('Con mascara')
mg.saveImageToFile(imageType=PNG, pathOutput='res/', fileOutput='masked_mosaico',image_params={'level':0,'mask':'(20 > a) | (a > 40)'})
mg.saveImageToFile(imageType=JPEG, pathOutput='res/', fileOutput='masked_mosaico',image_params={'level':0,'mask':'(20 > a) | (a > 40)'})
mg.saveToGTiff(0, outFilePath='res/',outFileName='masked_mosaico')
mg.saveToNETCDF('res/','masked_mosaico')