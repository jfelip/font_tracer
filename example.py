#!/usr/bin/env python
"""
This is an executable example for the usage of the font2vertices package. Uses matplotlib to draw a set of lines
that are obtained from the vertices generated after tracing the printable characters with the desired font.

Font sources used for the examples below:
    - https://pcaro.es/p/hermit/
    - https://www.typewolf.com/assets/fonts/robotomono.zip
"""

import time
import matplotlib.pyplot as plt
import string
from font_tracer import FontTracer

__author__ = "Javier Felip Leon"
__copyright__ = "Copyright 2020, Javier Felip Leon"
__credits__ = ["Javier Felip Leon"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Javier Felip Leon"
__email__ = "javier.felip.leon@gmail.com"
__status__ = "Development"

if __name__ == "__main__":
    # font_path = "fonts/RobotoMono-Regular.ttf"  # Has only conic points
    font_path = "fonts/Hermit-Regular.otf"  # Has cubic points

    t_ini = time.time()
    tracer = FontTracer()
    tracer.load_font(font_path=font_path, n_segments=10)
    t_end = time.time()

    # Display information about the font, load time and number of generated lines
    print("Loaded font: " + font_path)
    print("Load time: %5.3f ms" % ((t_end-t_ini)*1000))
    nlines = 0
    for c in string.printable:
        nlines += tracer.get_char_n_vertices(c)
    print("Num Lines: %d" % nlines)

    # Select the characters to be displayed
    glyphs = string.digits + "\n" + string.ascii_lowercase + "\n" + string.ascii_uppercase + "\n" + string.punctuation

    fig = plt.figure()
    tracer.plot(glyphs, axis=plt.gca())
    # Make sure the aspect ratio is preserved to avoid distorting the characters
    plt.grid(True)
    plt.gca().set_aspect('equal', 'datalim')
    plt.show()
