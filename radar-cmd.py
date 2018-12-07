#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Andres Giordano"
__version__ = "2.0"
__maintainer__ = "Andres Giordano"
__email__ = "andresgiordano.unlu@gmail.com"
__status__ = "Produccion"

import argparse
from os.path import basename,dirname, join
import matplotlib.cbook
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import Procesador.RainbowRadarProcessor
from Procesador.RainbowRadar import RainbowRadar
from Procesador.RainbowRadarProcessor import RainbowRadarProcessor
from Procesador.MosaicGenerator import MosaicGenerator

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)



class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def printException(e):
    print(bcolors.FAIL+e+bcolors.ENDC)

def printWarn(e):
    print(bcolors.WARNING+e+bcolors.ENDC)

parser = argparse.ArgumentParser(description='Procesamiento de radares.')

parser.add_argument('-f', metavar='--files', type=str,
                    help='Archivos de radar a procesar. Pueden ingresarse varios archivos separados por coma.')

parser.add_argument('-d', metavar='--directory', type=str,
                    help='Directorio de archivos a procesar. Se procesa cada archivo de forma individual.')

parser.add_argument('-R', action='store_true',
                    help='Recorre el directorio de forma recursiva')

parser.add_argument('-do', metavar='--dir-output', type=str,
                    help='Carpeta donde se almacenarán los resultados. Por defecto será la misma carpeta del archivo')

parser.add_argument('-o', metavar='--suffix', type=str,
                    help='Sufijo del nombre del archivo de salida.')

parser.add_argument('-ele', metavar='--elevation', type=int, required=True,
                    help='Numero de elevación (sweep)')

parser.add_argument('-var', metavar='--variable',choices=['dBZ', 'ZDR','RhoHV','uPhiDP','auto'], type=str, required=True,
                    help='Variable del radar a procesar. Posibles valores: dBZ, ZDR, RhoHV y uPhiDP. Si utiliza \'auto\' '
                         'será detectado automaticamente para cada archivo')

parser.add_argument('-m', metavar='--mosaic', type=str,
                    help='Generar mosaico. Se deberan indicar los archivos de entrada separados por \',\' (comas). Ej:'
                         '-m radar1.vol,radar2.vol,radar3.vol,radarN.vol. Los resultados seran guardados en la carpeta especificada'
                         ' por -do, en caso que -do no sea ingresado se almacenarán en la carpeta del primer archivo (radar1.vol)')

parser.add_argument('-grid', action='store_true',
                    help='Guardar la grilla cartesiana en un archivo .grib')

parser.add_argument('-gtif', action='store_true',
                    help='Generar un archivo georeferenciado .tif')

parser.add_argument('-img', action='store_true',
                    help='Guardar la salida como imagen')

parser.add_argument('-img_type', metavar='--imageType', type=str, choices=['JPEG','PNG'], default='PNG',
                    help='Tipo de imagen de salida. JPEG y PNG son los parametros posibles')

parser.add_argument('-img_method', metavar='--imageMethod', type=str, choices=['grid','simple'], default='grid',
                    help='Método por el cual se genera la imagen de salida (solo para los graficos individuales, NO '
                         'APLICA cuando se genera la imagen de un mosaico). Valores posibles: '
                         '\'grid\' --> a partir de la grilla cartesiana generada, '
                         '\'simple\' --> datos obtenidos directamente del radar (raw data)')

parser.add_argument('-mask', metavar='--masked-where', type=str,
                    help='Aplicar mascara. La mascara ingresada debe respetar el formato de numpy.ma.masked_where.'
                         ' La variable a utilizar debe ser siempre \'a\'. Ej.: "(15 <= a) & (a <= 50)"')

args = vars(parser.parse_args())

def getVar(file):
    '''
    Funcion para detectar la variable. Resuelve de forma automatica o en el caso de haber elegido una variable especifica
    devuelve la variable solo si coincide con la variable que contiene el archivo.

    :param file:
    :return:
    '''
    var = None
    if Procesador.RainbowRadar.dBZ[0].upper() in str(file).upper():
        var = Procesador.RainbowRadar.dBZ
    elif Procesador.RainbowRadar.RhoHV[0].upper() in str(file).upper():
        var = Procesador.RainbowRadar.RhoHV
    elif Procesador.RainbowRadar.ZDR[0].upper() in str(file).upper():
        var = Procesador.RainbowRadar.ZDR
    elif Procesador.RainbowRadar.uPhiDP[0].upper() in str(file).upper():
        var = Procesador.RainbowRadar.uPhiDP

    if str(args['var']).upper() == 'AUTO':
        if var is not None:
            return var
        else:
            printWarn('No se detecto ninguna variable procesable en el archivo '+file+'. El archivo será omitido....')
            return None

    else:
        if str(args['var']).upper() == Procesador.RainbowRadar.dBZ[0].upper() and var == Procesador.RainbowRadar.dBZ:
            return Procesador.RainbowRadar.dBZ
        elif str(args['var']).upper() == Procesador.RainbowRadar.RhoHV[0].upper() and var == Procesador.RainbowRadar.RhoHV:
            return Procesador.RainbowRadar.RhoHV
        elif str(args['var']).upper() == Procesador.RainbowRadar.ZDR[0].upper() and var == Procesador.RainbowRadar.ZDR:
            return Procesador.RainbowRadar.ZDR
        elif str(args['var']).upper() == Procesador.RainbowRadar.uPhiDP[0].upper() and var == Procesador.RainbowRadar.uPhiDP:
            return Procesador.RainbowRadar.uPhiDP
        else:
            printWarn(
                'La variable elegida no coincide con la contenida por el archivo ' + file + '. El archivo será omitido....')
            return None

def getFiles(pre_files):
    files = []
    for file_dir, file_name in pre_files:
        if file_name.endswith('.vol') or file_name.endswith('.azi'):
            var = getVar(file_name)
            if var is not None:
                out_file_dir = file_dir
                if args['do'] is not None:
                    out_file_dir = args['do']

                out_file_name = file_name.split('.')[0]
                if args['o'] is not None:
                    out_file_name = out_file_name + '_' + args['o']

                files.append((join(file_dir, file_name), var, join(out_file_dir, out_file_name)))
    return files

#############################################################
## Obtengo los archivos a procesar

# Tuplas con archivo, variable a procesar y archivo salida: [(archivo,var_archivo, salida) , (archivo2,var_archivo2, salida2) , .... ]


pre_files = []
if args['f'] is not None:
    filenames = args['f'].split(',')
    for file_name in filenames:
        pre_files.append((dirname(file_name)+'/',
                      basename(file_name)
                      ))
elif args['d'] is not None:
    from os import listdir, walk
    from os.path import isfile, join
    if args['R']:
        for (dirpath, dirnames, filenames) in walk(args['d']):
            for file_name in filenames:
                full_path = join(dirpath, file_name)
                pre_files.append((dirname(full_path)+'/',basename(full_path)))
    else:
        pre_files = [(dirname(args['d'])+'/',f) for f in listdir(args['d']) if isfile(join(args['d'], f))]

files = getFiles(pre_files)
print(files)
#########################################################################
## Obtengo la elevacion a procesar

sweep = args['ele']

#########################################################################
## Obtengo el tipo de imagen a generar

imgType = None
if (args['img_type'].upper() == 'PNG'):
    imgType = Procesador.RainbowRadarProcessor.PNG
else:
    imgType = Procesador.RainbowRadarProcessor.JPEG


#########################################################################
## Obtengo la mascara

mascara = ''
if args['mask'] is not None:
    mascara = args['mask']

#########################################################################
## Genero los objetos RainbowRadar en base a los archivos
rainbow_radars = []
for file,radar_variable,file_out in files:
    rr = RainbowRadar()
    rr.readRadar(dirname(file) + "/",basename(file), radarVariable=radar_variable)
    rr.setMask(mascara)
    rainbow_radars.append(rr)
    rrp = RainbowRadarProcessor(rr)

    if args['img']:
        metodo = ''

        if args['img_method'] == 'grid':
            metodo = 'grid'
        elif args['img_method'] == 'simple':
            metodo = 'simple'

        rrp.saveImageToFile(elevation=sweep, pathOutput=dirname(file_out)+'/', fileOutput=basename(file_out), imageType=imgType,
                            method=metodo)
    if args['gtif']:
        rrp.saveToGTiff(sweep, dirname(file_out)+'/', basename(file_out))
    if args['grid']:
        rrp.saveToNETCDF(sweep, dirname(file_out)+'/', basename(file_out))



if args['m'] is not None:
    pre_files = []
    filenames = args['m'].split(',')
    for file_name in filenames:
        pre_files.append((dirname(file_name)+'/',
                      basename(file_name)
                      ))
    files = getFiles(pre_files)
    print(files)
    rainbow_radars = []
    for file, radar_variable, file_out in files:
        rr = RainbowRadar()
        rr.readRadar(dirname(file) + "/", basename(file), radarVariable=radar_variable)
        rr.setMask(mascara)
        rainbow_radars.append(rr)

    mg = MosaicGenerator(radars=rainbow_radars)

    out_path = dirname(files[0][2]) + '/'
    out_file_name = basename(files[0][2])

    if args['img']:
        mg.saveImageToFile(out_path, out_file_name, sweep, imgType)
    if args['gtif']:
        mg.saveToGTiff(sweep, out_path, out_file_name)
    if args['grid']:
        mg.saveToNETCDF(sweep, out_path, out_file_name)
