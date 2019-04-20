# radar-cmd
[![codecov](https://codecov.io/gh/INTA-Radar/radar-cmd/branch/master/graph/badge.svg)](https://codecov.io/gh/INTA-Radar/radar-cmd)

Aplicación de línea de comandos para procesamiento de volumenes utilizando Py-ART

## Dependencias

1. [Py-ART](https://github.com/ARM-DOE/pyart)
2. [Geopy](https://github.com/geopy/geopy)  
3. [Wradlib](https://github.com/wradlib/wradlib)
4. [HDF5](https://pypi.python.org/pypi/h5py)
 
## Modo de uso

    usage: radar-cmd.py [-h] [-f F] [-pf PF] [-d D] [-R] [-do DO] [-o O]
                    [-var {dBZ,ZDR,RhoHV,uPhiDP,auto}] [-m] [-netCDF] [-gtif]
                    [-img] [-img_type {JPEG,PNG}] [-img_method {grid,simple}]
                    [-ele ELE] [-level LEVEL] [-ib] [-rain] [-img_dpi IMG_DPI]
                    [-mask MASK] [-v]

    Procesamiento de radares.
    
    optional arguments:
      -h, --help            show this help message and exit
      -f F                  Archivos de radar a procesar. Pueden ingresarse varios archivos separados por coma, esto es necesario para la generacion del mosaico.
                            Ej:
                                    -m radar1.vol,radar2.vol,radar3.vol,radarN.vol.
                            
      -pf PF                Archivo yml con parametros para la generacion del producto. Es una alternativa a pasar los parametros por linea de comandos. Los parametros que se indiquen en el archivo sobreescriben a los establecidos por linea de comandos
      -d D                  Directorio de archivos a procesar. Se procesa cada archivo de forma individual.
      -R                    Recorre el directorio de forma recursiva
      -do DO                Carpeta donde se almacenarán los resultados. Por defecto será la misma carpeta del archivo
      -o O                  Sufijo del nombre del archivo de salida.
      -var {dBZ,ZDR,RhoHV,uPhiDP,auto}
                            Variable del radar a procesar. Posibles valores: dBZ, ZDR, RhoHV y uPhiDP. Si utiliza 'auto' será detectado automaticamente para cada archivo
      -m                    Generar mosaico. Se toman los archivos indicados en el parametro -f. 
                            Los resultados seran guardados en la carpeta especificada por -do, en caso que -do no sea ingresado se almacenarán en la carpeta del primer archivo (radar1.vol)
      -netCDF               Guardar la grilla cartesiana en un archivo .netCDF
      -gtif                 Generar un archivo georeferenciado .tif
      -img                  Guardar la salida como imagen
      -img_type {JPEG,PNG}  Tipo de imagen de salida. JPEG y PNG son los parametros posibles
      -img_method {grid,simple}
                            Método por el cual se genera la imagen de salida (solo para los graficos individuales, NO APLICA cuando se genera la imagen de un mosaico). 
                            Valores posibles: 
                            'grid' --> a partir de la grilla cartesiana generada con todas las elevaciones.
                            'simple' --> datos de una sola elevacion.
      -ele ELE              Numero de elevación (sweep). Requerido solo en caso de -img_method=simple
      -level LEVEL          Nivel de la grilla. Requerido solo en caso de -img_method=grid
      -ib                   Si se indica el parametro se ignora la generacion de mapas de fondo. Para mosaico NO tiene efecto
      -rain                 Computar el indice de precipitaciones para los volumenes con dBZ disponible.
      -img_dpi IMG_DPI      Indica la calidad de imagen a generar. Por defecto es 200.
      -mask MASK            Aplicar mascara. La mascara ingresada debe respetar el formato de numpy.ma.masked_where.
                             La variable a utilizar debe ser siempre 'a'. Ej.: "(15 <= a) & (a <= 50)"
      -v                    Verbose
                
## Instalación

Para instalar esta herramienta ver páginas en la wiki:

1. [Ubuntu](https://github.com/INTA-Radar/radar-cmd/wiki/Instalaci%C3%B3n----Ubuntu)
2. [Debian Jessie](https://github.com/INTA-Radar/radar-cmd/wiki/Instalaci%C3%B3n---Debian-(jessie))

## Testing

Para ejecutar el script de testing:
1. Descomprimir el archivo dentro de la carpeta ```datos.tar.gz``` que se encuentra en la carpeta ```Testing```.
2. En linea de comandos, cambiar el directorio (```cd```) a la carpeta ```Testing```
3. Si la carpeta ```res``` no existe, crearla: ```mkdir res```
4. Teniendo el entorno virtual activado (```source ~/radar_wrap/bin/activate```)

   4.1 Ejecutar el script ```Test.py``` o bien
   
   4.2 Ejecutar el script bash `./test.sh`. En este script se encuentra documentado todas las formas de uso de la herramienta `radar-cmd.py`  

Si la ejecución no arroja errores entonces la instalación del entorno fué exitosa.
