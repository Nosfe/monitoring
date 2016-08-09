import os

import matplotlib.pyplot as plt
import numpy as np

import config
import utils.utils as utils

__author__ = 'Pace Francesco'


class CDFs:
    def __init__(self):
        pass

    @staticmethod
    def tasks_multi_figure(dataset, filename):
        workloads = []
        scenarios = []
        colors = {}
        color = None
        for scenario in dataset:
            color = utils.getNewColor(color)
            colors[scenario] = color
            scenarios.append(scenario)
            for workload in dataset[scenario]:
                if workload not in workloads:
                    workloads.append(workload)
        figures = ['total']
        for workload in workloads:
            print "# --- Workload {} ---".format(workload)
            for scenario in scenarios:
                print "# Scenario {}".format(scenario)
                try:
                    tasks_runtimes = dataset[scenario][workload]['app']['tasks']['runtimes']
                    total_tasks_runtimes = []
                    for task_type in tasks_runtimes:
                        if tasks_runtimes[task_type] is not None and len(tasks_runtimes[task_type]) > 0 and sum(
                                tasks_runtimes[task_type]) > 0:

                            if task_type not in figures:
                                figures.append(task_type)

                            total_tasks_runtimes += tasks_runtimes[task_type]
                            tasks_runtimes[task_type].sort()
                            print "#     Task type {} composed by {} tasks".format(task_type,
                                                                                   len(tasks_runtimes[task_type]))
                            cdf = []
                            for i, value in enumerate(tasks_runtimes[task_type]):
                                cdf.append(i / float(len(tasks_runtimes[task_type])))

                            x = np.array(tasks_runtimes[task_type])
                            cy = np.array(cdf)
                            markevery = cy.size / 5
                            plt.figure(figures.index(task_type))
                            plt.grid(True, which='both')
                            plt.plot(x, cy, color=colors[scenario]["line_color"], dashes=colors[scenario]["dash"],
                                     marker=colors[scenario]["marker"], markersize=colors[scenario]["markerSize"],
                                     markevery=markevery)
                    total_tasks_runtimes.sort()
                    print "#     Total Tasks number is {}".format(len(total_tasks_runtimes))
                    cdf = []
                    for i, value in enumerate(total_tasks_runtimes):
                        cdf.append(i / float(len(total_tasks_runtimes)))

                    x = np.array(total_tasks_runtimes)
                    cy = np.array(cdf)
                    markevery = cy.size / 5
                    plt.figure(figures.index('total'))
                    plt.grid(True)  # , which='both')
                    plt.plot(x, cy, color=colors[scenario]["line_color"], dashes=colors[scenario]["dash"],
                             marker=colors[scenario]["marker"], markersize=colors[scenario]["markerSize"],
                             markeredgewidth=colors[scenario]["markeredgewidth"],
                             markeredgecolor=colors[scenario]["line_color"],
                             linewidth=3.0, markevery=markevery)
                except KeyError:
                    pass
            for task_type in figures:
                plt.figure(figures.index(task_type))
                plt.ylim((0, 1.05))
                plt.xscale('log')
                xlabel = plt.xlabel('Seconds')
                # title = plt.title('CDF')
                # title = plt.title(workload)
                plot_filename = utils.mkdir_p(os.path.join(filename,
                                                           'cdf_task_' + task_type + '_' + workload + '.' + config.PLOT_FORMAT))
                if task_type == "total":
                    plt.savefig(plot_filename, bbox_inches='tight')
                    plot_filename = utils.mkdir_p(os.path.join(filename,
                                                               'cdf_task_' + task_type + '_' + workload + '_legend.' + config.PLOT_FORMAT))
                # lgd = plt.legend(scenarios, loc='upper right',
                #                  bbox_to_anchor=(1.02, -0.1000), ncol=3)
                lgd = plt.legend(scenarios, loc=2,
                                 bbox_to_anchor=(1.01, 1), ncol=1, borderaxespad=0.)
                # plt.savefig(plot_filename, bbox_extra_artists=(lgd, xlabel, title), bbox_inches='tight')
                plt.savefig(plot_filename, bbox_extra_artists=(lgd, xlabel), bbox_inches='tight')
                plt.close()
        print "# ------------------------------------"
