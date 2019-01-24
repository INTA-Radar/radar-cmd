#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Andres Giordano"
__version__ = "3.0.0"
__maintainer__ = "Andres Giordano"
__email__ = "andresgiordano.unlu@gmail.com"
__status__ = "Produccion"

import argparse
from os.path import basename,dirname, join
import os
import matplotlib.cbook
import warnings

os.environ['PYART_QUIET'] = 'True'
warnings.filterwarnings("ignore", category=FutureWarning)

import Procesador.RainbowRadarProcessor
from Procesador.Precipitation import Precipitation
from Procesador.RainbowRadar import RainbowRadar
from Procesador.RainbowRadarProcessor import RainbowRadarProcessor
from Procesador.MosaicGenerator import MosaicGenerator
from argparse import RawTextHelpFormatter
import re
import yaml

auto_var_re = re.compile(r'\d+(\w+)[\.vol|\.azi]', re.IGNORECASE | re.UNICODE)

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

parser = argparse.ArgumentParser(description='Procesamiento de radares.', formatter_class=RawTextHelpFormatter)

parser.add_argument('-f', type=str,
                    help='Archivos de radar a procesar. Pueden ingresarse varios archivos separados por coma, esto es necesario para la'
                         ' generacion del mosaico.\n'
                         'Ej:\n'
                         '\t-m radar1.vol,radar2.vol,radar3.vol,radarN.vol.\n\n')

parser.add_argument('-pf', type=str,
                    help='Archivo yml con parametros para la generacion del producto. Es una alternativa a pasar los '
                         'parametros por linea de comandos. Los parametros que se indiquen en el archivo sobreescriben '
                         'a los establecidos por linea de comandos')

parser.add_argument('-d', type=str,
                    help='Directorio de archivos a procesar. Se procesa cada archivo de forma individual.')

parser.add_argument('-R', action='store_true',
                    help='Recorre el directorio de forma recursiva')

parser.add_argument('-do', type=str,
                    help='Carpeta donde se almacenarán los resultados. Por defecto será la misma carpeta del archivo')

parser.add_argument('-o', type=str,
                    help='Sufijo del nombre del archivo de salida.')

parser.add_argument('-var', choices=['dBZ', 'ZDR','RhoHV','uPhiDP','auto'], type=str, default='auto',
                    help='Variable del radar a procesar. Posibles valores: dBZ, ZDR, RhoHV y uPhiDP. Si utiliza \'auto\' '
                         'será detectado automaticamente para cada archivo')

parser.add_argument('-m', action='store_true',
                    help='Generar mosaico. Se toman los archivos indicados en el parametro -f. \n'                         
                         'Los resultados seran guardados en la carpeta especificada por -do, en caso que -do no sea ingresado se almacenarán en la carpeta del primer archivo (radar1.vol)\n')

parser.add_argument('-netCDF', action='store_true',
                    help='Guardar la grilla cartesiana en un archivo .netCDF')

parser.add_argument('-gtif', action='store_true',
                    help='Generar un archivo georeferenciado .tif')

parser.add_argument('-img', action='store_true',
                    help='Guardar la salida como imagen')

parser.add_argument('-img_type', type=str, choices=['JPEG','PNG'], default='PNG',
                    help='Tipo de imagen de salida. JPEG y PNG son los parametros posibles')

parser.add_argument('-img_method', type=str, choices=['grid','simple'], default='grid',
                    help='Método por el cual se genera la imagen de salida (solo para los graficos individuales, NO '
                         'APLICA cuando se genera la imagen de un mosaico). \n'
                         'Valores posibles: \n'
                         '\'grid\' --> a partir de la grilla cartesiana generada con todas las elevaciones.\n'
                         '\'simple\' --> datos de una sola elevacion.\n')

parser.add_argument('-ele', type=int,
                    help='Numero de elevación (sweep). Requerido solo en caso de -img_method=simple')

parser.add_argument('-level', type=int,
                    help='Nivel de la grilla. Requerido solo en caso de -img_method=grid')

parser.add_argument('-ib', action='store_false',
                    help='Si se indica el parametro se ignora la generacion de mapas de fondo. Para mosaico '
                         'NO tiene efecto')

parser.add_argument('-rain', action='store_true',
                    help='Computar el indice de precipitaciones para los volumenes con dBZ disponible.')

parser.add_argument('-img_dpi', type=int, default=200,
                    help='Indica la calidad de imagen a generar. Por defecto es 200.')

parser.add_argument('-mask', type=str,
                    help='Aplicar mascara. La mascara ingresada debe respetar el formato de numpy.ma.masked_where.\n'
                         ' La variable a utilizar debe ser siempre \'a\'. Ej.: "(15 <= a) & (a <= 50)"')

parser.add_argument('-v', action='store_true',
                    help='Verbose')

args = vars(parser.parse_args())

def getVar(file):
    """
    Funcion para detectar la variable. Resuelve de forma automatica o en el caso de haber elegido una variable especifica
    devuelve la variable solo si coincide con la variable que contiene el archivo.

    :param file:
    :return:
    """

    var = None
    finds = auto_var_re.findall(file)
    if len(finds)==1:
        if Procesador.RainbowRadar.dBZ[0].upper() == finds[0].upper():
            var = Procesador.RainbowRadar.dBZ
        elif Procesador.RainbowRadar.RhoHV[0].upper() == finds[0].upper():
            var = Procesador.RainbowRadar.RhoHV
        elif Procesador.RainbowRadar.ZDR[0].upper() == finds[0].upper():
            var = Procesador.RainbowRadar.ZDR
        elif Procesador.RainbowRadar.uPhiDP[0].upper() == finds[0].upper():
            var = Procesador.RainbowRadar.uPhiDP
        elif Procesador.RainbowRadar.V[0].upper() == finds[0].upper():
            var = Procesador.RainbowRadar.V

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
# Leo archivo de parametros

if args['pf'] is not None:
    with open(args['pf'], 'r') as stream:
        params = yaml.load(stream)
        args.update(params)

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

formato = '{0:<50}| {1:<20}| {2:<12}| {3:<50}'

if args['v']:
    print(formato.format('Entrada', 'Productos', 'Variable','Salida'))
    print('_'*150)
    for f in files:
        print(formato.format(f[0], ','.join(['img' if args['img'] else '',
                                             'netCDF' if args['netCDF'] else '',
                                             'gtif' if args['gtif'] else ''
                                             ]), f[1][0], f[2]))
        print('-' * 150)

#########################################################################
## Obtengo la elevacion o nivel a procesar

sweep = args['ele']
level = args['level']

#########################################################################
## Obtengo el tipo de imagen a generar

imgType = None
if args['img_type'].upper() == 'PNG':
    imgType = Procesador.RainbowRadarProcessor.PNG
else:
    imgType = Procesador.RainbowRadarProcessor.JPEG


#########################################################################
## Obtengo la mascara

mascara = args['mask']

#########################################################################
## Genero los objetos RainbowRadar en base a los archivos

if not args['m']:
    for file,radar_variable,file_out in files:
        rr = RainbowRadar(dirname(file) + "/",basename(file), radarVariable=radar_variable)

        if args['rain']:
            pp = Precipitation(rr)
            pp.computePrecipitations(sweep)
            rr = rainbowRadar=pp.genRainRainbowRadar()

        rrp = RainbowRadarProcessor(rr)

        if args['img']:
            metodo = ''

            img_params = {
                          'dpi':args['img_dpi'],
                          'basemapFlag':args['ib'],
                          'mask': mascara,
                          }

            if args['img_method'] == 'grid':

                if level is None:
                    raise Exception('El parametro \'level\' no fue especificado')

                metodo = 'grid'
                img_params.update({'level': level})

            elif args['img_method'] == 'simple':

                if sweep is None:
                    raise Exception('El parametro \'ele\' no fue especificado')

                metodo = 'simple'
                img_params.update({'elevation': sweep})

            rrp.saveImageToFile(pathOutput=dirname(file_out)+'/', fileOutput=basename(file_out), imageType=imgType,
                                method=metodo,image_method_params=img_params)
        if args['gtif']:
            rrp.saveToGTiff(level, dirname(file_out)+'/', basename(file_out))
        if args['netCDF']:
            rrp.saveToNETCDF(dirname(file_out)+'/', basename(file_out))

else:

    rainbow_radars = []
    for file, radar_variable, file_out in files:
        rr = RainbowRadar(dirname(file) + "/", basename(file), radarVariable=radar_variable)
        rainbow_radars.append(rr)

    mg = MosaicGenerator(radars=rainbow_radars)

    out_path = dirname(files[0][2]) + '/'
    out_file_name = basename(files[0][2])

    if args['v']:
        for x in range(len(files)-1):
            f = files[x]
            print(formato.format(f[0],
                                 '',
                                 f[1][0], ''))
        f = files[len(files)-1]
        print(formato.format(f[0],
                             ','.join(['img' if args['img'] else '',
                                       'netCDF' if args['netCDF'] else '',
                                       'gtif' if args['gtif'] else ''
                                       ]),
                             f[1][0],
                             join(out_path,out_file_name)))
        print('-' * 150)

    if args['img']:
        img_params = {'level': level,
                      'dpi': args['img_dpi'],
                      'mask': mascara,
                      }
        mg.saveImageToFile(out_path, out_file_name, imgType, image_params=img_params)
    if args['gtif']:
        mg.saveToGTiff(sweep,
                       out_path,
                       out_file_name)
    if args['netCDF']:
        mg.saveToNETCDF(out_path, out_file_name)
