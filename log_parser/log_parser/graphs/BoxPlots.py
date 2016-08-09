from collections import OrderedDict
from itertools import izip_longest

import matplotlib.pyplot as plt

import utils.utils as utils
import os
import numpy as np

from log_parser import config

__author__ = 'Pace Francesco'


class BoxPlots:
    def __init__(self):
        pass

    @staticmethod
    def resource(plot_title, scenario, dataset, plot_dir):
        colors = {}
        color = None

        res = OrderedDict({})
        resource = dataset['resource']
        if resource is not None:
            if 'SWI' in scenario:
                res['CPU W'] = resource['Worker']['CPU']
                res['CPU S'] = resource['Swift']['CPU']
                res['Disk W'] = resource['Worker']['Disk_Busy']
                res['Disk S'] = resource['Swift']['Disk_Busy']
                res['Net W'] = resource['Worker']['Network']
                res['Net S'] = resource['Swift']['Network']
            elif 'GC' in scenario:
                res['CPU'] = resource['Worker']['CPU']
                res['Disk'] = resource['Worker']['Disk_Busy']
                res['Net'] = resource['Worker']['Network']
            else:
                res['CPU W'] = resource['Worker']['CPU']
                res['CPU D'] = resource['DataNode']['CPU']
                res['Disk W'] = resource['Worker']['Disk_Busy']
                res['Disk D'] = resource['DataNode']['Disk_Busy']
                res['Net W'] = resource['Worker']['Network']
                res['Net D'] = resource['DataNode']['Network']

        offset = 1
        if len(res) > 0:
            medianprops = dict(linewidth=5, color='k')
            for (i, r) in enumerate(res):
                if r not in colors:
                    color = utils.getNewColor(color)
                    colors[r] = color
                x = np.array(res[r])
                x = x.transpose()
                if len(x) == 0:
                    continue
                x_mav = utils.moving_average_exp(x, 5)
                plt.boxplot(x_mav, positions=[i + offset], widths=0.8, patch_artist=True,
                            boxprops={'edgecolor': "k", "facecolor": colors[r]["bar_color"]},
                            whiskerprops={'color': 'k'}, flierprops={'color': 'k'},
                            medianprops=medianprops, showfliers=False)

            x_ticks = np.arange(offset, len(res) + offset, offset).tolist()
            x_lim = [0, len(res) + offset]
            plt.xticks(x_ticks, res.keys(), rotation=70)
            plt.xlim(x_lim)
            plt.ylim([0, 100])
            plt.grid()
            title = plt.title(plot_title)

            plot_filename = utils.mkdir_p(os.path.join(plot_dir, 'resources.' + config.PLOT_FORMAT))
            plt.savefig(plot_filename, bbox_extra_artists=(title,), bbox_inches='tight')
            plt.close()

    @staticmethod
    def disk_throughput_multi_figure(dataset, filename):
        workloads = []
        colors = {}
        color = None
        for s in dataset:
            for w in dataset[s]:
                if w not in workloads:
                    workloads.append(w)
        for w in workloads:
            res = OrderedDict({})
            for s in dataset:
                try:
                    resource = dataset[s][w]['resource']
                    if resource is not None:
                        if 'SWI' in s:
                            res[s] = [x + y for x, y in izip_longest(
                                resource['Swift']['Disk_Bytes'],
                                resource['Worker']['Disk_Bytes'], fillvalue=0)]
                        else:
                            res[s] = [x + y for x, y in izip_longest(
                                resource['DataNode']['Disk_Bytes'],
                                resource['Worker']['Disk_Bytes'], fillvalue=0)]
                except KeyError:
                    pass
            offset = 1
            if len(res) > 0:
                for (i, r) in enumerate(res):
                    if r not in colors:
                        color = utils.getNewColor(color)
                        colors[r] = color
                    x = np.array(res[r])
                    x /= (1024 * 1024)
                    x = x.transpose()
                    if len(x) == 0:
                        continue
                    plt.boxplot(x, positions=[i + offset], widths=0.8, patch_artist=True,
                                boxprops={'edgecolor': "k", "facecolor": colors[r]["bar_color"]},
                                whiskerprops={'color': 'k'}, flierprops={'color': 'k'},
                                medianprops={'color': 'k'})

                x_ticks = np.arange(offset, len(res) + offset, offset).tolist()
                x_lim = [0, len(res) + offset]
                plt.xticks(x_ticks, res.keys(), rotation=70)
                plt.xlim(x_lim)
                plt.ylabel('MB/s')
                title = plt.title(w)
                plot_filename = utils.mkdir_p(os.path.join(filename, w, 'disk_throughput.' + config.PLOT_FORMAT))
                plt.savefig(plot_filename, bbox_extra_artists=(title,), bbox_inches='tight')
            plt.close()
