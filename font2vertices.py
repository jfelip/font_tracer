"""
Set of helper functions to trace cubic and conic arcs described by true type fonts outlines. Each glyph can be
converted to a list of vertex arrays, each one representing a closed contour of the glyph outline. Vertex arrays
can be further processed to obtain a list of line segments that can be drawn in a plot or using a GL_LINES draw
primitive.
"""
import freetype
import numpy as np
from bezier_sampling import bezier_curve

__author__ = "Javier Felip Leon"
__copyright__ = "Copyright 2020, Javier Felip Leon"
__credits__ = ["Javier Felip Leon"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Javier Felip Leon"
__email__ = "javier.felip.leon@gmail.com"
__status__ = "Development"


def trace_cubic_off_points(c_points, c_tags, idx, n_segments=5):
    """
    Traces the bezier cubic arc represented by the contour off point at idx into n_segments line segments. Details of
    font outline in: https://www.freetype.org/freetype2/docs/glyphs/glyphs-6.html

    Two successive conic off points force the creation of a virtual on point at the exact middle of the two off
    points to sample the conic curve. Cubic points must be in pairs and have to be surrounded by on points. To avoid
    line segment duplication this function only traces line segments if the c_points[idx] is the second of a pair of
    off cubic points.

    :param c_points: Contour points arranged in a (N,2) array.
    :param c_tags: N-sized array with a FreeType tag for each point in c_points.
    :param idx: Index of the contour point used to create the traced segments.
    :param n_segments: Number of segments used to trace the bezier arc. Defaults to 5.
    :return: Set of line segments (M, 2)
    """
    sampled_pts = np.array([])
    idx_prev = idx - 1
    idx_next = idx + 1
    # If it is the last point of the contour. Use the first as the pivot
    if idx == len(c_points) - 1:
        idx_next = 0

    # Only trace if the point is the second of a pair of off cubic points.
    if c_tags[idx_prev] == freetype.FT_Curve_Tag_Cubic and c_tags[idx] == freetype.FT_Curve_Tag_Cubic:
        sampled_pts = bezier_curve([c_points[idx_prev - 1],
                                    c_points[idx_prev],
                                    c_points[idx],
                                    c_points[idx_next]], n_segments)
    return sampled_pts.reshape(-1)


def trace_conic_off_points(c_points, c_tags, idx, n_segments=5):
    """
    Traces the bezier arc represented by the contour off point at idx into n_segments line segments. Details of font
    outline in: https://www.freetype.org/freetype2/docs/glyphs/glyphs-6.html

    Two successive conic off points force the creation of a virtual on point at the exact middle of the two off
    points to sample the conic curve. Cubic points must be in pairs and have to be surrounded by on points.

    :param c_points: Contour points arranged in a (N,2) array.
    :param c_tags: N-sized array with a FreeType tag for each point in c_points.
    :param idx: Index of the contour point used to create the traced segments.
    :param n_segments: Number of segments used to trace the bezier arc. Defaults to 5.
    :return: Set of line segments (M, 2)
    """
    # If it is the last point of the contour. Use the first as the pivot
    idx_prev = idx - 1
    idx_next = idx + 1
    if idx == len(c_points) - 1:
        idx_next = 0

    if c_tags[idx_prev] == freetype.FT_Curve_Tag_On:
        point_start = c_points[idx_prev]
    elif c_tags[idx_prev] == freetype.FT_Curve_Tag_Conic:
        point_start = (c_points[idx] + c_points[idx_prev]) / 2
    else:
        raise ValueError("While tracing point index %d. Previous point with unsupported type: " % idx
                         + str(c_tags[idx_prev]))

    if c_tags[idx_next] == freetype.FT_Curve_Tag_On:
        point_end = c_points[idx_next]
    elif c_tags[idx_next] == freetype.FT_Curve_Tag_Conic:
        point_end = (c_points[idx] + c_points[idx_next]) / 2
    else:
        raise ValueError("While tracing point index %d. Previous point with unsupported type: " % idx
                         + str(c_tags[idx_next]))

    sampled_pts = bezier_curve([point_start, c_points[idx], point_end], n_segments)
    return sampled_pts.reshape(-1)


def glyph2vertices(glyph, n_segments=5):
    """
    Sample glyph outline vertices checking points on the curve and control points for conic and cubic bezier arcs as 
    described in: https://www.freetype.org/freetype2/docs/glyphs/glyphs-6.html
    Vertex coordinates are scaled such that the vertical advance is 1 unit and the return is a list of arrays, 
    each list element represents a closed contour. Each closed contour is a numpy array of size Nx2 representing the 
    set of 2d vertices that form the contour outline.
    
    :param glyph: FreeFont glyph to be traced 
    :param n_segments: Number of segments used to sample each bezier arc. Defaults to 5.
    :return: A list of sampled contours. Each contour is a numpy array of Nx2 vertices representing a glyph contour.
    """
    # Get the points describing the outline
    points = np.array(glyph.outline.points, dtype=np.float32)

    # Get contour start indices
    contours = glyph.outline.contours

    # Obtain the point tags from the glyph outline description.
    tags = []
    for i, t in enumerate(glyph.outline.tags):
        tags.append(freetype.FT_CURVE_TAG(t))

    # Process each contour separately
    prev_c = -1
    c_draw_contours = []
    for c in contours:
        # Extract the points and tags for the current contour
        c_points = points[prev_c + 1:c + 1]
        c_draw_points = np.array([])
        c_tags = tags[prev_c + 1:c + 1]

        # Generate points depending on their tag
        for i in range(len(c_points)):
            # If the point is on, just add it
            if c_tags[i] == freetype.FT_Curve_Tag_On:
                c_draw_points = np.concatenate((c_draw_points, c_points[i]))

            # If the point is off conic
            elif c_tags[i] == freetype.FT_Curve_Tag_Conic:
                sampled_pts = trace_conic_off_points(c_points, c_tags, i, n_segments)
                c_draw_points = np.concatenate((c_draw_points, sampled_pts))

            # If the point is off cubic
            elif c_tags[i] == freetype.FT_Curve_Tag_Cubic:
                sampled_pts = trace_cubic_off_points(c_points, c_tags, i, n_segments)
                c_draw_points = np.concatenate((c_draw_points, sampled_pts))

        # Normalize vertices (scale to fit 1 unit height bbox)
        c_draw_points = c_draw_points / glyph.metrics.vertAdvance

        c_draw_contours.append(c_draw_points)
        prev_c = c

    # Return a list of contour vertices
    return c_draw_contours


def vertices2lines(contours):
    """
    Generate a set of 2d lines from a set of closed contours.
    :param contours: List of 2d closed contours. Each contour is an array of flattened 2d points.
    :return: Array of vertices representing lines.
    """
    lines = np.array([])

    for contour in contours:
        # Draw a line between each contour sampled sequential point
        for i in range(0, len(contour), 2):
            line = contour[i:i+4]
            lines = np.concatenate((lines, line))

        # Close the contour
        if len(contour) % 2 != 0:
            lines = np.concatenate((lines, contour[-2:2]))
        else:
            lines = np.concatenate((lines, contour[0:2]))

    return lines.flatten()
