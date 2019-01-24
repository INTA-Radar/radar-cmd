# -*- coding: utf-8 -*-

from scipy.stats import linregress
import matplotlib.colors as colors
import numpy as np
from PIL import Image

PNG = 'png'
JPEG = 'jpeg'



def radar_colormap():
    nws_reflectivity_colors = [
        "#646464",  # ND
        "#ccffff",  # -30
        "#cc99cc",  # -25
        "#996699",  # -20
        "#663366",  # -15
        "#cccc99",  # -10
        "#999966",  # -5
        "#646464",  # 0
        "#04e9e7",  # 5
        "#019ff4",  # 10
        "#0300f4",  # 15
        "#02fd02",  # 20
        "#01c501",  # 25
        "#008e00",  # 30
        "#fdf802",  # 35
        "#e5bc00",  # 40
        "#fd9500",  # 45
        "#fd0000",  # 50
        "#d40000",  # 55
        "#bc0000",  # 60
        "#f800fd",  # 65
        "#9854c6",  # 70
        "#fdfdfd"  # 75
    ]

    cmap = colors.ListedColormap(nws_reflectivity_colors)
    return cmap

def fig2data(fig):
    """
    Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it

    :param fig: a matplotlib figure
    :return: a numpy 3D array of RGBA values
    """

    # draw the renderer
    fig.canvas.draw()

    # Get the RGBA buffer from the figure
    w, h = fig.canvas.get_width_height()
    buf = np.fromstring(fig.canvas.tostring_argb(), dtype=np.uint8)
    buf.shape = (w, h, 4)

    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = np.roll(buf, 3, axis=2)
    return buf


def fig2img(fig):
    """
    Convert a Matplotlib figure to a PIL Image in RGBA format and return it

    :param fig: a matplotlib figure
    :return: a Python Imaging Library ( PIL ) image
    """

    # put the figure pixmap into a numpy array
    buf = fig2data(fig)
    w, h, d = buf.shape
    return Image.frombytes("RGBA", (w, h), buf.tostring())

def gen_ticks(orig_coord, min_coord, max_coord, arange_step=1):

    """
    Genera un array de coordenadas en base a una coordenada de origen ``orig_coord`` y coordenadas
    limites ``min_coord`` y ``max_min_coord``.\n
    El array se genera de la siguiente manera:

        [ min_coord ... arrange_step ... orig_coord ... arrange_step ... max_coord ]

    :param orig_coord: coordenada de origen.
    :param min_coord: limite inferior.
    :param max_coord: limite superior.
    :param arange_step: tamaño de pasos a tomar desde origen hasta los limites.
    :return: lista de coordenadas
    :rtype: list[float]
    """

    a = list(np.arange(orig_coord, min_coord, -arange_step))
    b = list(np.arange(orig_coord, max_coord, arange_step))
    a.extend(b[1:])

    return a