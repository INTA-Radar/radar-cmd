# -*- coding: utf-8 -*-
__author__ = "Andres Giordano"
__version__ = "1.0"
__maintainer__ = "Andres Giordano"
__email__ = "andresgiordano.unlu@gmail.com"
__status__ = "Produccion"

import argparse
import os
import RadarDataProcesor
from RadarDataProcesor import RainbowRadar,RainbowRadarProcessor,MosaicGenerator
import sys,traceback

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def printException(e):
    print bcolors.FAIL+e+bcolors.ENDC

parser = argparse.ArgumentParser(description='Procesamiento de radares.')

parser.add_argument('-f', metavar='--files', type=str, nargs=1, required=True,
                    help='Archivos de radares .vol')

parser.add_argument('-o', metavar='--output', type=str, nargs=1, required=True,
                    help='Archivo de salida.')

parser.add_argument('-ele', metavar='--elevation', type=int, nargs=1, required=True,
                    help='Numero de elevación (o sweep)')

parser.add_argument('-var', metavar='--variable',choices=['dBZ', 'ZDR','RhoHV','uPhiDP'], type=str, nargs=1, required=True,
                    help='Variable del radar a procesar. Posible valores: dBZ, ZDR, RhoHV y uPhiDP' )

parser.add_argument('-m', action='store_true',
                    help='Indica que se requiere hacer un mosaico de los archivos de entrada.'
                         'En el parametro \'-f\' se deberan indicar los archivos de entrada separados por \',\' (comas). Ej:'
                         '-f radar1.vol,radar2.vol,radar3.vol,radarN.vol')

parser.add_argument('-grid', action='store_true',
                    help='Indica que se requiere guardar la grilla cartesiana en un archivo .grib')

parser.add_argument('-gtif', action='store_true',
                    help='Indica que se requiere generar un archivo georeferenciado .tif')

parser.add_argument('-img', action='store_true',
                    help='Indica que se requiere guardar la salida como imagen')

parser.add_argument('-img_type', metavar='--imageType', type=str, choices=['JPEG','PNG'], nargs=1, default='PNG',
                    help='Tipo de imagen de salida. JPEG y PNG son los parametros posibles')

# Parametrizar grafico individual (grilla o comun)
# Plotear mapa en grafico comun
# Calidad de imagen de salida
# Parametrizar padding grilla

args = vars(parser.parse_args())

files = []
if 'f' in args:
    files = args['f'][0].split(',')


out_file = ''
if args['o'] != None :
    out_file = args['o'][0]

sweep = args['ele'][0]

rainbow_radars = []

for file in files:
    rr = RainbowRadar()

    rr.readRadar(os.path.dirname(file) + "/",os.path.basename(file))
    rainbow_radars.append(rr)

radar_variable = None
if str(args['var'][0]).upper() == RadarDataProcesor.dBZ[0].upper():
    radar_variable = RadarDataProcesor.dBZ
elif str(args['var'][0]).upper() == RadarDataProcesor.RhoHV[0].upper():
    radar_variable = RadarDataProcesor.RhoHV
elif str(args['var'][0]).upper() == RadarDataProcesor.ZDR[0].upper():
    radar_variable = RadarDataProcesor.ZDR
elif str(args['var'][0]).upper() == RadarDataProcesor.uPhiDP[0].upper():
    radar_variable = RadarDataProcesor.uPhiDP

out_path = os.path.dirname(os.path.abspath(out_file)) + "/"
out_file_name = os.path.basename(out_file)

imgType = None
if (args['img_type'][0].upper() == 'PNG'):
    imgType = RadarDataProcesor.PNG
else:
    imgType = RadarDataProcesor.JPEG

try:
    if args['m']:
        mg = MosaicGenerator(radars=rainbow_radars, radarVariable=radar_variable)

        if args['img']:
            mg.saveImageToFile(out_path,out_file_name,sweep,imgType)
        if args['gtif']:
            mg.saveToGTiff(sweep, out_path, out_file_name)
        if args['grid']:
            mg.saveToNETCDF(sweep, out_path, out_file_name)

    else:
        if len(files) > 1:
            print bcolors.WARNING+'#########################'
            print '# ATENCION!!!!!'
            print '#'
            print '# Se han detectado varios archivos de radares de entrada y  el parametro \'-m\' no fue ingresado.'
            print '# NO se va a generar un MOSAICO, SOLO SE PROCESARA EL PRIMER ARCHIVO\n'
            print '# Si quiere generar un mosaico ingrese el parametro \'-m\''
            print '# .....'+bcolors.ENDC

        rr = rainbow_radars[0]

        rrp = RainbowRadarProcessor(rr,radar_variable)

        if args['img']:
            rrp.saveImageToFile(elevation=sweep,pathOutput=out_path,fileOutput=out_file_name,imageType=imgType)
        if args['gtif']:
            rrp.saveToGTiff(sweep,out_path,out_file_name)
        if args['grid']:
            rrp.saveToNETCDF(sweep,out_path,out_file_name)

    print bcolors.OKGREEN+'Procesamiento finalizado!!!'+bcolors.ENDC

except Exception:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
    printException(exc_value.args[0])

