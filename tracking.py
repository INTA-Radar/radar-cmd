#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Andres Giordano"
__version__ = "0.1"
__maintainer__ = "Andres Giordano"
__email__ = "andresgiordano.unlu@gmail.com"
__status__ = "Produccion"

import os
os.environ['PYART_QUIET'] = 'True'

from tint.tracks import Cell_tracks
from tint.visualization import animate
from Procesador.RainbowRadar import RainbowRadar,dBZ

import Procesador.RainbowRadar
from os.path import basename,dirname
import codecs
import json
import argparse
from argparse import RawTextHelpFormatter
import re
import datetime

parser = argparse.ArgumentParser(description='Procesamiento de radares.', formatter_class=RawTextHelpFormatter)

parser.add_argument('-f', type=str, required=True,
                    help='Archivo que contiene una lista de volumenes a procesar. El tracking se generará en el orden'
                         ' indicado por la lista.')

parser.add_argument('-m', type=str, choices=['anim','table'],default='table',
                    help='Modo de salida:\n'
                         '      anim: guarda una animacion en formato mp4. No se permiten mas de 6 volumenes.\n'
                         '      table: guarda la tabla de tracking en un archivo csv. DEFAULT')

parser.add_argument('-ele', metavar='--elevation', type=int, required=True,
                    help='Numero de elevación (sweep)')

parser.add_argument('-tparams', type=json.loads, required=True,
                    help='Parametros para el tracking. Ver `Cell_tracks.params` en `tint.tracks`. '
                         'Se espera un diccionario con clave:valor.\n'
                         'Ejemplo:\n'
                         '      \'{"MIN_SIZE":50,"FIELD_THRESH":40}\' ')

parser.add_argument('-do', metavar='--dir-output', type=str,
                    help='Carpeta donde se almacenarán los resultados. Por defecto será la misma carpeta del primer archivo.')

parser.add_argument('-o', metavar='--suffix', type=str,
                    help='Sufijo del nombre del archivo de salida.')

parser.add_argument('-v', action='store_true',
                    help='Verbose')

args = vars(parser.parse_args())
auto_var_re = re.compile(r'\d+(\w+)[\.vol|\.azi]', re.IGNORECASE | re.UNICODE)

if __name__ == '__main__':


    filenames = []
    with codecs.open(args['f'], mode='r', encoding='utf-8') as in_f:
        for l in in_f.readlines():
            filenames.append(l.strip())

    dir_output = args['do']
    if dir_output is None:
        dir_output = dirname(filenames[0]) + '/'

    for ffile_name in filenames:

        file_name = basename(ffile_name)

        if file_name.endswith('.vol') or file_name.endswith('.azi'):

            finds = auto_var_re.findall(file_name)
            if Procesador.RainbowRadar.dBZ[0].upper() != finds[0].upper():
                raise Exception('dBZ es la unica variable permitida, usted esta usando ' + finds[0])
        else:
            raise Exception('Formato de archivo no permitido '+file_name)

    grid_gen = []
    for file in filenames:
        rr = RainbowRadar('', file, radarVariable=dBZ)
        grid_gen.append(rr.getCartesianGrid(args['ele']))

    # Instantiate tracks object and view parameter defaults
    tracks_obj = Cell_tracks()


    if args['tparams'] is not None:
        tracks_obj.params.update(args['tparams'])

    # Get tracks from grid generator
    tracks_obj.get_tracks((g for g in grid_gen))

    # Inspect tracks


    if args['m'] == 'table':
        if args['o'] is not None:
            file_out = 'tracking_table_' + args['o'] + '.csv'
        else:
            file_out = 'tracking_table.csv'

        tracks_obj.tracks.to_csv(file_out, sep=' ', decimal='.')
    else:
        if len(filenames) > 6:
            raise Exception('No se permiten mas de 6 archivos para generar la animacion.')
        else:

            file_out = 'tracking_animation_'+datetime.date.today().strftime('%Y-%m-%d_%H:%M:%S')
            if args['o'] is not None:
                file_out = 'tracking_animation_' + args['o']+'_'+datetime.date.today().strftime('%Y-%m-%d %H:%M:%S')

            animate(tracks_obj, grid_gen, file_out, style='full', alt=0, vmin=-30, vmax=70)



