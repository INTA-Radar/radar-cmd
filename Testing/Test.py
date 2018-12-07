import sys

from numpy import pad

sys.path.extend(['../'])

import matplotlib.cbook
import warnings


warnings.filterwarnings("ignore", category=FutureWarning)

from Procesador.RainbowRadarProcessor import RainbowRadarProcessor
from Procesador.RainbowRadar import RainbowRadar,ZDR,dBZ,uPhiDP,RhoHV
from Procesador.MosaicGenerator import MosaicGenerator
from Procesador.Utils import PNG,JPEG
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
'f_x_dBZ'       :   [dBZ,'datos/2009112306135000dBZ.vol']
}

files_mosaico = {
'Mosaico_PER_dBZ':  [dBZ,'datos/Mosaico/240/PER/2016122616204500dBZ.vol'],
'Mosaico_PAR_dBZ':  [dBZ,'datos/Mosaico/240/PAR/2016122616200500dBZ.vol'],
'Mosaico_ANG_dBZ':  [dBZ,'datos/Mosaico/240/ANG/2016122616200300dBZ.vol']

}



#################################################################
# Simple images

for name,file in files.items():
    print(name,' ; ',file)
    rr = RainbowRadar()
    rr.readRadar('',file[1], radarVariable=file[0])
    p = RainbowRadarProcessor(rainbowRadar=rr)

    p.saveImageToFile(elevation=0,imageType=PNG,paddingImg=1, pathOutput='res/', fileOutput=name)
    p.saveImageToFile(elevation=0,imageType=JPEG, pathOutput='res/', fileOutput=name)

    p.saveImageToFile(elevation=0, imageType=PNG, paddingImg=10, pathOutput='res/', fileOutput=name+'_simple', method='simple')
    p.saveImageToFile(elevation=0, imageType=JPEG, pathOutput='res/', fileOutput=name+'_simple', method='simple')

    p.saveToGTiff(elevation=0, outFilePath='res/',outFileName=name)
    p.saveToNETCDF(elevation=0, outFilePath='res/',outFileName=name)


#################################################################
# Mosaic

radars = []
for name,file in files_mosaico.items():
    print(name, ' ; ', file)
    radar = RainbowRadar()
    radar.readRadar('',file[1], radarVariable=dBZ)
    # Aplico una mascara a datos menores a 20 y mayores a 40
    radar.setMask("(20 > a) | (a > 40)")
    radars.append(radar)

mg = MosaicGenerator(radars=radars)

mg.saveImageToFile(elevation=0,imageType=PNG, pathOutput='res/', fileOutput='mosaico')
mg.saveImageToFile(elevation=0,imageType=JPEG, pathOutput='res/', fileOutput='mosaico')
mg.saveToGTiff(elevation=0, outFilePath='res/',outFileName='mosaico')
mg.saveToNETCDF(0, 'res/','mosaico')