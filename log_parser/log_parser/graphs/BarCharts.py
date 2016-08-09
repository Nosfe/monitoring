from collections import OrderedDict
from itertools import izip_longest

import matplotlib.pyplot as plt

import utils.utils as utils
import os
import numpy as np

from log_parser import config

__author__ = 'Pace Francesco'


class BarCharts:
    def __init__(self):
        pass

    @staticmethod
    def swift_requests(plot_title, dataset, plot_dir):
        colors = {}
        color = None
        bars = {}
        figures = ['total', 'details']

        x_labels = []
        for server in dataset:
            requests = dataset[server]["Request"]
            for (i, request) in enumerate(requests):
                if request not in x_labels:
                    x_labels.append(request)

                plt.figure("total")
                plt.bar(i, requests[request]["total"], align='center')

                plt.figure("details")
                codes = requests[request]["code"]
                bottom = 0
                for code in codes:
                    if code not in colors:
                        color = utils.getNewColor(color)
                        colors[code] = color
                        bars[code] = None
                    bar = plt.bar(i, codes[code], align='center', color=colors[code]["bar_color"], bottom=bottom,
                                  label=code)
                    bottom += codes[code]
                    if bars[code] is None:
                        bars[code] = bar

            for figure_type in figures:
                plt.figure(figure_type)
                plt.xticks(np.arange(len(x_labels)), x_labels)
                plt.grid()
                plt.ylabel("# of Requests")
                title = plt.title(plot_title)
                # plt.yscale('log')
                lgd = None
                if figure_type is "details":
                    lgd = plt.legend(bars.values(), colors.keys(), loc='upper right',
                                     bbox_to_anchor=(1.02, -0.1000), ncol=3)
                ax = plt.axes()
                rects = ax.patches
                bottom = 0
                old_x = None
                for rect in rects:
                    if old_x != rect.get_x():
                        bottom = 0
                        old_x = rect.get_x()
                    height = rect.get_height()
                    ax.text(rect.get_x() + rect.get_width()/2., (bottom + (height / 2.0)) - config.PLOT_FONT_SIZE,
                            '%d' % int(height),
                            ha='center', va='bottom')
                    bottom += rect.get_height()

                plot_filename = utils.mkdir_p(
                    os.path.join(plot_dir, "swift-requests-" + server + '-' + figure_type + '.' + config.PLOT_FORMAT))
                if lgd is not None:
                    plt.savefig(plot_filename, bbox_extra_artists=(lgd, title), bbox_inches='tight')
                else:
                    plt.savefig(plot_filename, bbox_extra_artists=(title,), bbox_inches='tight')
                plt.close()
