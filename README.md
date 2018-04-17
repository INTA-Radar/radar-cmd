# radar-cmd
Aplicación de línea de comandos para procesamiento de volumenes utilizando Py-ART

## Dependencias

1. [Py-ART] (https://github.com/ARM-DOE/pyart)
2. [Geopy] (https://github.com/geopy/geopy)  
3. [Wradlib] (https://github.com/wradlib/wradlib)
4. [HDF5] (https://pypi.python.org/pypi/h5py)
 
## Modo de uso

    radar-cmd.py -h
    usage: radar-cmd.py [-h] -f --files -o --output [-m] -ele --elevation -var
                    --variable [-grid] [-gtif] [-img] [-img_type --imageType]

    Procesamiento de radares.

    Parametros:
    -f --files            Archivos de radares .vol
    -o --output           Archivo de salida.
    -ele --elevation      Numero de elevación (o sweep)
    -var --variable       Variable del radar a procesar. Posible valores: dBZ,
                        ZDR,RhoHV y uPhiDP
    
    Parametros opcionales:                      
    -h, --help            show this help message and exit
    -m                    Indica que se requiere hacer un mosaico de los
                        archivos de entrada.En el parametro '-f' se deberan
                        indicar los archivos de entrada separados por ','
                        (comas). Ej:-f
                        radar1.vol,radar2.vol,radar3.vol,radarN.vol
    -grid                 Indica que se requiere guardar la grilla cartesiana en
                        un archivo .grib
    -gtif                 Indica que se requiere generar un archivo
                        georeferenciado .tif
    -img                  Indica que se requiere guardar la salida como imagen
    -img_type --imageType
                        Parámetro de formato de imagen de salida. JPEG y PNG son los
                        parametros posibles
    -img_method --imageMethod
                        Metodo por el cual se genera la imagen de salida (solo
                        para los graficos individuales, NO APLICA cuando se
                        genera la imagen de un mosaico). Valores posibles: 'grid' --> a
                        partir de la grilla cartesiana generada, 'simple' -->
                        datos obtenidos directamente del radar                      


## Instalacion

Para la instalacion se va a crear un virtualenv con el objetivo de manejar librerias especificas con versiones especificas sin crear conflictos con las ya instaladas.

    cd ~
    virtualenv --no-site-packages radar_wrap

Activamos el entorno 

    source radar_wrap/bin/activate

Actualizamos pip a la ultima version

    pip install --upgrade pip

Instalamos algunas librerias basicas 

    pip install matplotlib==2.0.2
    pip install Image
    pip install Pillow
    pip install scipy
    pip install geopy
    pip install wradlib==0.9.0

##### GDAL

Para instalar la libreria python GDAL es necesario primero instalar la libreria del sistema operativo ```libgdal-dev```. Para ello ejecutamos:
  
    sudo apt-get install libgdal-dev

Luego exportamos las rutas a la libreria GDAL de tal manera que la interfaz para python pueda vincularse correctamente al momento de la instalacion:
    
    export CPLUS_INCLUDE_PATH=/usr/include/gdal
    export C_INCLUDE_PATH=/usr/include/gdal
    
Ahora necesitamos obtener la version instalada de GDAL en el SO para instalar una version compatible de python:     
    
    GDAL_VERSION="$(gdal-config --version)" 

Finalmente instalamos GDAL para python:
    
    pip install GDAL==$GDAL_VERSION
    
Si esto no funciona, debemos usar la version inmediata anterior a ```$GDAL_VERSION``` disponible para python. Las versiones disponibles son avisadas por el error anterior.

Ahora clonamos la ultima version disponible de PyART y la instalamos:

    cd ~/radar_wrap/
    git clone https://github.com/ARM-DOE/pyart.git
    cd pyart
    python setup.py build
    sudo python setup.py install

##### Basemap

Para instalar la version de basemap (1.0.7) compatible con este proyecto es necesario descargar el paquete desde [Basemap 1.0.7](https://pypi.org/project/basemap/1.0.7/). Luego, descomprimir en la carpeta:

    ~/radar_wrap/basemap-1.0.7/
    
Se requieren las siguientes librerias instaladas en el SO previo a la instalacion de la interfaz para Python:

    libgeos-3.4.2                                              - Geometry engine for Geographic Information Systems - C++ Library     
    libgeos-c1                                                 - Geometry engine for Geographic Information Systems - C Library       
    libgeos-dev                                                - Geometry engine for GIS - Development files       

Los pasos para la instalacion son los siguientes:

    cd ~/radar_wrap/basemap-1.0.7/geos-3.3.3/
    export GEOS_DIR=/usr/local
    ./configure --prefix=$GEOS_DIR
    make; make install 
     
Quizas en el ultimo comando sea necesario usar permisos de super-usuario (```sudo```). Luego, instalamos librerias necesarias de Python:

    pip install numpy
    pip install pyproj
    pip install pyshp

Finalmente, instalamos basemap:

    python setup.py install
    
   