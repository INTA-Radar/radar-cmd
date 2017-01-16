# radar-cmd
Aplicación de línea de comandos para procesamiento de volumenes y utilizando Py-ART

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

