FROM ubuntu:bionic
ARG DEBIAN_FRONTEND=noninteractive

LABEL maintainer="Andres Giordano <andresgiordano.unlu@gmail.com>"

# SO libraries
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y dialog apt-utils
RUN apt-get install -y libgdal-dev
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y git

# Python libraries
RUN pip3 install --upgrade pip
RUN pip install scipy
RUN pip install netcdf4
RUN pip install h5py
RUN pip install matplotlib
RUN pip install GDAL==$(gdal-config --version) --global-option=build_ext --global-option="-I/usr/include/gdal"
RUN pip install arm_pyart
RUN pip install xmltodict
RUN pip install wradlib==0.9.0
RUN pip install geopy
RUN pip install https://github.com/matplotlib/basemap/archive/v1.2.0rel.tar.gz
# Se comenta la siguiente linea, solo fue usada para pruebas.
#RUN pip install http://192.168.1.106:8000/basemap-1.2.0rel.tar.gz
RUN pip install Pillow

# Clone Radar-CMD
RUN git clone https://github.com/INTA-Radar/radar-cmd.git /root/radar-cmd
WORKDIR /root/radar-cmd







