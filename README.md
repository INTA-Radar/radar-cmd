# radar-cmd
Aplicación de línea de comandos para procesamiento de volumenes utilizando Py-ART

## Dependencias

1. [Py-ART](https://github.com/ARM-DOE/pyart)
2. [Geopy](https://github.com/geopy/geopy)  
3. [Wradlib](https://github.com/wradlib/wradlib)
4. [HDF5](https://pypi.python.org/pypi/h5py)
 
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


## Instalación

Para la instalación se va a crear un virtualenv con el objetivo de manejar librerías especificas con versiones especificas sin crear conflictos con las ya instaladas.

    cd ~
    virtualenv --no-site-packages radar_wrap

Activamos el entorno 

    source radar_wrap/bin/activate

Actualizamos pip a la ultima versión

    pip install --upgrade pip

Instalamos algunas librerías básicas 

    pip install matplotlib==2.0.2
    pip install Image
    pip install Pillow
    pip install scipy
    pip install geopy
    pip install wradlib==0.9.0

#### GDAL

Para instalar la librería python GDAL es necesario primero instalar la librería del sistema operativo ```libgdal-dev```. Para ello ejecutamos:

    sudo apt-get install libgdal-dev

Luego exportamos las rutas a la librería GDAL de tal manera que la interfaz para python pueda vincularse correctamente al momento de la instalación:
 
    export CPLUS_INCLUDE_PATH=/usr/include/gdal
    export C_INCLUDE_PATH=/usr/include/gdal
 
Ahora necesitamos obtener la versión instalada de GDAL en el SO para instalar una versión compatible de python:   
 
    GDAL_VERSION="$(gdal-config --version)" 

Finalmente instalamos GDAL para python:
 
    pip install GDAL==$GDAL_VERSION
 
Si esto no funciona, debemos usar la versión inmediata anterior a ```$GDAL_VERSION``` disponible para python. Las versiones disponibles son avisadas por el error anterior.

Ahora clonamos la ultima versión disponible de PyART y la instalamos:

    cd ~/radar_wrap/
    git clone https://github.com/ARM-DOE/pyart.git
    cd pyart
    python setup.py build
    sudo python setup.py install

#### Basemap

Para instalar la versión de basemap (1.0.7) compatible con este proyecto es necesario descargar el paquete desde [Basemap 1.0.7](https://pypi.org/project/basemap/1.0.7/). Luego, descomprimir en la carpeta:

    ~/radar_wrap/basemap-1.0.7/
 
Se requieren las siguientes librerías instaladas en el SO previo a la instalación de la interfaz para Python:

    libgeos-3.4.2   - Geometry engine for Geographic Information Systems - C++ Library   
    libgeos-c1      - Geometry engine for Geographic Information Systems - C Library   
    libgeos-dev     - Geometry engine for GIS - Development files   

Los pasos para la instalación son los siguientes:

    cd ~/radar_wrap/basemap-1.0.7/geos-3.3.3/
    export GEOS_DIR=/usr/local
    ./configure --prefix=$GEOS_DIR
    make; make install 
  
Quizás en el ultimo comando sea necesario usar permisos de super-usuario (```sudo```). Luego, instalamos librerías necesarias de Python:

    pip install numpy
    pip install pyproj
    pip install pyshp

Finalmente, instalamos basemap:

    python setup.py install
    
### Estado final de librerias

Una vez hecha la instalación se pueden verificar las versiones de las librerias instaladas con ```pip freeze ```. Un estado valido sobre el cual esta herramienta funciona correctamente es el siguiente:

    arm-pyart==1.10.0
    basemap==1.0.7
    cycler==0.10.0
    deprecation==2.0.2
    functools32==3.2.3.post2
    GDAL==1.10.0
    geographiclib==1.49
    geopy==1.13.0
    h5py==2.7.1
    matplotlib==2.0.2
    netCDF4==1.3.1
    numpy==1.14.2
    packaging==17.1
    Pillow==5.1.0
    pyparsing==2.2.0
    pyproj==1.9.5.1
    pyshp==1.2.12
    python-dateutil==2.7.2
    pytz==2018.4
    scipy==1.0.1
    six==1.11.0
    subprocess32==3.2.7
    wradlib==0.9.0
    xmltodict==0.11.0
 

## Testing

Para ejecutar el script de testing:
1. Descomprimir el archivo dentro de la carpeta ```datos.tar.gz``` que se encuentra en la carpeta ```Testing```.
2. En linea de comandos, cambiar el directorio (```cd```) a la carpeta ```Testing```
3. Si la carpeta ```res``` no existe, crearla: ```mkdir res```
4. Teniendo el entorno virtual activado (```source ~/radar_wrap/bin/activate```) ejecutar el script ```Test.py```

Si la ejecución no arroja errores entonces la instalación del entorno fué exitosa.