from scipy.stats import linregress
import matplotlib.colors as colors
import numpy
from PIL import Image

# bsp = { 'stoprange': { 'degrees':'bsp'}}
bsp = {120: {0.5: 2,
             1.3: 1.3,
             2.3: 1.1,
             3.5: 1.05,
             5: 1.02,
             6.9: 1,
             9.1: 0.99,
             11.8: 0.9769,
             15.1: 0.9729,
             19.2: 0.97},
       240: {0.5: 2.56,
             0.9: 1.85,
             1.3: 1.58,
             1.9: 1.36,
             2.3: 1.285,
             3: 1.2,
             3.5: 1.165,
             5: 1.1,
             6.9: 1.06,
             9.1: 1.035,
             11.8: 1.015,
             15.1: 1.004,
             19.2: 1},
       480: {0.3: 6.3}
       }

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

def getBsp(stopRange, nb):
    if nb in bsp[stopRange]:
        return bsp[stopRange][nb]
    else:
        # Obtengo el bsp haciendo una regresion lineal entre X=nb e Y=(nb*bsp)
        print()
        print('Obteniendo bsp por regresion lineal. Stoprange =', stopRange, ' nb =', nb)

        Y = [y for y in bsp[stopRange].values()]
        X = [x for x in bsp[stopRange].keys()]

        i = 0
        for y in Y:
            print(y)
            print(X[i])
            Y[i] = y * X[i]
            i += 1

        print('nb =', X)
        print('nb*bsp =', Y)
        coeffs = linregress(X, Y)

        # Si el r-cuad da 0.0 quiere decir que no se pudo generar una regresion lineal.
        # Esto pasa cuando existe un unico punto.

        if coeffs[2] == 0.0:
            raise Exception('No se pudo crear una regresion lineal para ' + str(stopRange) + 'km')

        print('Funcion a usar = ' + str(coeffs[0]) + '*nb+' + str(coeffs[1]))
        print('Coeficiente de correlacion R-cuad = ', coeffs[2])
        print('Bsp = (' + str(coeffs[0]) + '*nb + ' + str(coeffs[1]) + ')/nb')
        bsp_val = (coeffs[0] * nb + coeffs[1]) / nb
        print('Bsp = ', bsp_val)
        print()
        return bsp_val


def fig2data(fig):
    """
    @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
    @param fig a matplotlib figure
    @return a numpy 3D array of RGBA values
    """
    # draw the renderer
    fig.canvas.draw()

    # Get the RGBA buffer from the figure
    w, h = fig.canvas.get_width_height()
    buf = numpy.fromstring(fig.canvas.tostring_argb(), dtype=numpy.uint8)
    buf.shape = (w, h, 4)

    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = numpy.roll(buf, 3, axis=2)
    return buf


def fig2img(fig):
    """
    @brief Convert a Matplotlib figure to a PIL Image in RGBA format and return it
    @param fig a matplotlib figure
    @return a Python Imaging Library ( PIL ) image
    """
    # put the figure pixmap into a numpy array
    buf = fig2data(fig)
    w, h, d = buf.shape
    return Image.frombytes("RGBA", (w, h), buf.tostring())