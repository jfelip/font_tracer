"""
This is a couple of helper functions to sample a bezier arc. This code is inspired by the following answer
in Stack Overflow and slightly modified to output points in the (x,y) format and use broadcasting to compute the
points in one operation:
https://stackoverflow.com/questions/12643079/b%C3%A9zier-curve-fitting-with-scipy
"""

import numpy as np
from scipy.special import comb


def bernstein_poly(i, n, t):
    """
     The Bernstein polynomial of n, i as a function of t
    """

    return comb(n, i) * (t**(n-i)) * (1 - t)**i


def bezier_curve(points, n_samples=5):
    """
    Given a set of control points defining a bezier curve, returns n_samples points equally spaced in the curve space.
    More details on bezier curves: See http://processingjs.nihongoresources.com/bezierinfo/
    :param points: Bezier curve control points. NxM numpy array.
    :param n_samples: Number of equidistant points to sample from the curve.
    :return: Sampled points. n_samples by M numpy array.
    """
    n_points = len(points)

    t = np.linspace(1.0, 0.0, n_samples)

    polynomial_array = np.array([bernstein_poly(i, n_points-1, t) for i in range(0, n_points)])

    return np.dot(np.transpose(polynomial_array), points)
