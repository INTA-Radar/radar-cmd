#!/usr/bin/env bash

# Se deja comentado a modo de documentacion: esta es la forma de evitar que Py-Art imprima en pantalla el mensaje de bienvenida.
#export PYART_QUIET=True


# Forma mas simple de usar la herramienta. El resultado va a la misma carpeta del archivo de entrada. Con -v indico que
# imprima informacion acerca de archivos a procesar y productos a generar.
# La imagen a generar es un CAPPI y el nivel se indica con el parametro 'level'
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -f datos/240/2009112306100500dBZ.vol -img -var auto -level 0 -v

# Se indica carpeta de salida con -do y sufijo del archivo con -o
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -f datos/240/2009112306100500dBZ.vol -do res_from_bash -o 240_dBZ -img -var auto -level 0

# Como procesar el nivel 4..
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -f datos/240/2009112306100500dBZ.vol -do res_from_bash -o 240_dBZ_e_4 -img -var auto -level 4

# Se genera la imagen de un PPI con -img_method simple y la elevacion se indica en -ele, en este caso es la primera elevacion del radar
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -f datos/240/2009112306100500dBZ.vol -img -var auto -do res_from_bash -o img_simple -ele 0 -img_method simple

# Aqui agregamos que se ignore el uso de basemap con -ib
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -f datos/240/2009112306100500dBZ.vol -img -var auto -do res_from_bash -o img_simple_ib -ele 0 -img_method simple -ib
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -f datos/240/2009112306100500dBZ.vol -img -var auto -do res_from_bash -o ib -level 0 -ib

# Se enmascaran datos, comparar con 240_dBZ level 0
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -f datos/240/2009112306100500dBZ.vol -do res_from_bash -o 240_dBZ_masked -img -var auto -level 0 -mask "(15 <= a) & (a <= 50)"

# Se procesan varios archivos en una sola linea
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -f datos/240/2009112306100500dBZ.vol,datos/240/2009112306100500RhoHV.vol,datos/120/2009112306135000dBZ.vol,datos/120/2009112306135000ZDR.vol -do res_from_bash -o multiples -img -img_dpi 50 -var auto -level 0

# Se indica directorio a procesar
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -d datos/120/ -do res_from_bash -o directorio_120 -img -img_dpi 50 -var auto -level 0

# Se indica calidad de la imagen de salida con -dpi, se prueban valores muy bajos y muy altos para ver la diferencia
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -f datos/240/2009112306100500dBZ.vol -do res_from_bash -o 240_dBZ_dpi_20 -img -var auto -level 0 -img_dpi 20
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -f datos/240/2009112306100500dBZ.vol -do res_from_bash -o 240_dBZ_dpi_200 -img -var auto -level 0 -img_dpi 200

# Mosaico de tres radares, level 0
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -m -f datos/Mosaico/240/PER/2016122616204500dBZ.vol,datos/Mosaico/240/PAR/2016122616200500dBZ.vol,datos/Mosaico/240/ANG/2016122616200300dBZ.vol -do res_from_bash -o 240_dBZ_mosaico_ANG-PAR-PER -img -var auto -level 0 -img_dpi 50

# Mosaico de dos radares, level 4
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -m -f datos/Mosaico/240/PER/2016122616204500dBZ.vol,datos/Mosaico/240/PAR/2016122616200500dBZ.vol -do res_from_bash -o 240_dBZ_mosaico_ANG-PAR -img -var auto -level 4 -img_dpi 50

# Mosaico de dos radares, level 0 con y sin mascara para comparar
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -m -f datos/Mosaico/240/PER/2016122616204500dBZ.vol,datos/Mosaico/240/PAR/2016122616200500dBZ.vol -do res_from_bash -o 240_dBZ_mosaico_ANG-PAR_not_masked -img -var auto -level 0
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -m -f datos/Mosaico/240/PER/2016122616204500dBZ.vol,datos/Mosaico/240/PAR/2016122616200500dBZ.vol -do res_from_bash -o 240_dBZ_mosaico_ANG-PAR_masked -img -var auto -level 0 -mask "(15 <= a) & (a <= 50)"

# Se procesan datos con variable dBZ y se calcula indice de precipitacion
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -f datos/240/2009112306100500dBZ.vol -do res_from_bash -o 240_dBZ_dpi_100_rain -img -var auto -img_method simple -ele 0 -img_dpi 100 -rain
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -f datos/480/2016122000073000dBZ.azi -do res_from_bash -o 480_dBZ_dpi_100_rain -img -var auto -img_method simple -ele 0 -img_dpi 100 -rain

# Te genera salida en formato tiff y netcdf
coverage run --rcfile=".coveragec" -a ../radar-cmd.py -f datos/240/2009112306100500dBZ.vol -do res_from_bash -o 240_dBZ -netCDF -gtif -var auto -level 0