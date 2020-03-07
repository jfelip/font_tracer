"""
Module to convert fonts supported by freetype fonts into a set of lines represented by pairs of 2D points.

The characters can be accessed through a dictionary indexed by the actual character or by get_char(char). It also
provides vertical and horizontal advance values for each loaded char through the get_char_advance method.

TODO: Add support for per-vertex color format. Useful for OpenGL and shader line rendering.
TODO: Add support for 3D vertices. Just add 0s to the Z dimension.
TODO: Add support for triangulation of the font fill.
"""
import numpy as np
import string
import freetype
from font2vertices import glyph2vertices
from font2vertices import vertices2lines

__author__ = "Javier Felip Leon"
__copyright__ = "Copyright 2020, Javier Felip Leon"
__credits__ = ["Javier Felip Leon"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Javier Felip Leon"
__email__ = "javier.felip.leon@gmail.com"
__status__ = "Development"


class FontTracer(object):
    def __init__(self):
        self.font_path = ""
        self.face = None
        self.traced_vertices = dict()
        self.traced_lines = dict()
        self.glyphs_advances = dict()

    def load_font(self, font_path, n_segments=5):
        self.face = freetype.Face(font_path)
        self.face.set_char_size(self.face.units_per_EM)
        for char in string.printable:
            self.face.load_char(char)
            self.traced_vertices[char] = glyph2vertices(self.face.glyph, n_segments)
            self.traced_lines[char] = vertices2lines(self.traced_vertices[char])
            self.glyphs_advances[char] = (self.face.glyph.advance.x / self.face.glyph.metrics.vertAdvance, 1)

    def get_char_n_vertices(self, char):
        return len(self.get_char_vertices(char)) / 2

    def get_char_vertices(self, char):
        if char in self.traced_vertices.keys() and len(self.traced_vertices[char]) > 0:
            return np.concatenate(self.traced_vertices[char])
        else:
            return np.array([])

    def get_char_lines(self, char):
        if char in self.traced_lines.keys():
            return self.traced_lines[char]
        else:
            return np.array([])

    def get_char_advance(self, char):
        return self.glyphs_advances[char]

    def get_char_x_advance(self, char):
        return self.glyphs_advances[char][0]

    def get_char_y_advance(self, char):
        return self.glyphs_advances[char][1]

    def plot(self, glyphs, axis):
        """
        Plot the line segments that were traced for the sequence of glyphs, considering horizontal and vertical
        offsets.

        :param glyphs: String of characters to be plot using the already loaded font
        :param axis: Object used for plotting.
        """
        pos_x = 0
        pos_y = 0
        for c in glyphs:
            if c == "\n":
                pos_y -= self.get_char_y_advance(c)
                pos_x = 0
                continue
            lines = self.get_char_lines(c)
            for i in range(0, len(lines) - 3, 4):
                axis.plot([lines[i] + pos_x, lines[i + 2] + pos_x], [lines[i + 1] + pos_y, lines[i + 3] + pos_y])
            pos_x += self.get_char_x_advance(c)
