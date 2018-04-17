import os
import sys
sys.path.extend(['../'])
from Procesador.RadarDataProcesor import RainbowRadar,RainbowRadarProcessor,MosaicGenerator
import Procesador.RadarDataProcesor as rdp
import matplotlib.pyplot as plt
import matplotlib.cbook
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)

files = {
'f_240_ZDR' : [rdp.ZDR,'datos/240/2009112306100500ZDR.vol'],
'f_240_dBZ':  [rdp.dBZ,'datos/240/2009112306100500dBZ.vol'],
'f_240_uPhiDP':  [rdp.uPhiDP,'datos/240/2009112306100500uPhiDP.vol'],
'f_240_RhoHV':  [rdp.RhoHV,'datos/240/2009112306100500RhoHV.vol'],
'f_480_dBZ':  [rdp.dBZ,'datos/480/2016122000073000dBZ.azi'],
'f_120_RhoHV':  [rdp.RhoHV,'datos/120/2009112306135000RhoHV.vol'],
'f_120_uPhiDP':  [rdp.uPhiDP,'datos/120/2009112306135000uPhiDP.vol'],
'f_120_dBZ':  [rdp.dBZ,'datos/120/2009112306135000dBZ.vol'],
'f_120_ZDR':  [rdp.ZDR,'datos/120/2009112306135000ZDR.vol']
}

files_mosaico = {
'Mosaico_PER_dBZ':  [rdp.dBZ,'datos/Mosaico/240/PER/2016122616204500dBZ.vol'],
'Mosaico_PAR_dBZ':  [rdp.dBZ,'datos/Mosaico/240/PAR/2016122616200500dBZ.vol'],
'Mosaico_ANG_dBZ':  [rdp.dBZ,'datos/Mosaico/240/ANG/2016122616200300dBZ.vol']

}

#################################################################
# Simple images

for name,file in files.iteritems():
    rr = RainbowRadar()
    rr.readRadar('',file[1])
    p = RainbowRadarProcessor(rainbowRadar=rr, radarVariable=file[0])
    p.saveImageToFile(elevation=0,imageType=rdp.PNG, pathOutput='res/', fileOutput=name)
    p.saveImageToFile(elevation=0,imageType=rdp.JPEG, pathOutput='res/', fileOutput=name)
    p.saveToGTiff(elevation=0, outFilePath='res/',outFileName=name)
    p.saveToNETCDF(elevation=0, outFilePath='res/',outFileName=name)


#################################################################
# Mosaic

radars = []
for name,file in files_mosaico.iteritems():
    radar = RainbowRadar()
    radar.readRadar('',file[1])
    radars.append(radar)

mg = MosaicGenerator(radars=radars, radarVariable=rdp.dBZ)

mg.saveImageToFile(elevation=0,imageType=rdp.PNG, pathOutput='res/', fileOutput='mosaico')
mg.saveImageToFile(elevation=0,imageType=rdp.JPEG, pathOutput='res/', fileOutput='mosaico')
mg.saveToGTiff(elevation=0, outFilePath='res/',outFileName='mosaico')
mg.saveToNETCDF(0, 'res/','mosaico')