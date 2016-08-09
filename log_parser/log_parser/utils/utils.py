import os
import errno
import warnings
import functools

import numpy as np

import config

__author__ = 'Pace Francesco'


def deprecated(func):
    """This is a decorator which can be used to mark functions
         as deprecated. It will result in a warning being emitted
         when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn_explicit(
            "Call to deprecated function {}.".format(func.__name__),
            category=DeprecationWarning,
            filename=func.func_code.co_filename,
            lineno=func.func_code.co_firstlineno + 1
        )
        return func(*args, **kwargs)

    return new_func


def mkdir_p(path):
    path = path.replace(" ", "_")
    dir_path = os.path.dirname(path)
    try:
        os.makedirs(dir_path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(dir_path):
            pass
        else:
            raise
    return path


def getNewColor(old):
    bw_map = {
        'b': {'marker': "D", 'dash': (None, None), 'hatch': ""},
        'g': {'marker': "v", 'dash': [10, 10], 'hatch': "-"},
        'r': {'marker': "x", 'dash': [5, 5, 2, 5], 'hatch': "\\"},
        'c': {'marker': "o", 'dash': [2, 5], 'hatch': "x"},
        'm': {'marker': None, 'dash': [5, 2, 5, 2, 5, 10], 'hatch': "+"},
        'y': {'marker': "*", 'dash': [5, 3, 1, 2, 1, 10], 'hatch': "."},
        'k': {'marker': None, 'dash': (None, None), 'hatch': "o"},  # [1,2,1,10]}
        'orange': {'marker': None, 'dash': (None, None), 'hatch': "O"},  # [1,2,1,10]}
        'navy': {'marker': None, 'dash': (None, None), 'hatch': "/"},  # [1,2,1,10]}
    }

    if old is None:
        new_color = 'r'
    elif old['color'] == 'r':
        new_color = 'b'
    elif old['color'] == 'b':
        new_color = 'y'
    elif old['color'] == 'y':
        new_color = 'g'
    elif old['color'] == 'g':
        new_color = 'c'
    elif old['color'] == 'c':
        new_color = 'm'
    elif old['color'] == 'm':
        new_color = 'orange'
    elif old['color'] == 'orange':
        new_color = 'navy'
    else:
        raise Exception("Old Color not recognized! {}".format(old['color']))

    if config.PLOT_BW:
        return {"color": new_color, "line_color": "k", "bar_color": "w", "marker": bw_map[new_color]["marker"],
                "dash": bw_map[new_color]["dash"], "markerSize": 10, "markeredgewidth": 5,
                'hatch': bw_map[new_color]["hatch"]}
    else:
        return {"color": new_color, "line_color": new_color, "bar_color": new_color,
                "marker": bw_map[new_color]["marker"], "dash": bw_map[new_color]["dash"], "markerSize": 5,
                "markeredgewidth": 2, 'hatch': ""}


def y_fmt(x, y):
    return '{:1.0e}'.format(x).replace('e', 'x10^')


def ticks_format(value, index):
    """
    get the value and returns the value as:
       integer: [0,99]
       1 digit float: [0.1, 0.99]
       n*10^m: otherwise
    To have all the number of the same size they are all returned as latex strings
    """
    exp = np.floor(np.log10(value))
    base = value / 10 ** exp
    if exp == 0 or exp == 1:
        return '${0:d}$'.format(int(value))
    if exp == -1:
        return '${0:.1f}$'.format(value)
    else:
        return '${0:d}\\times10^{{{1:d}}}$'.format(int(base), int(exp))


def moving_average(interval, window_size):
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'valid')


def moving_average_exp(interval, weight):
    N = int(weight)
    weights = np.exp(np.linspace(-1., 0., N))
    weights /= weights.sum()
    return np.convolve(weights, interval)[N-1:-N+1]