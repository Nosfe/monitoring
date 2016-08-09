import os
import os.path

import matplotlib.pyplot as plt
import numpy

import config
import utils.utils as utils

__author__ = 'Pace Francesco'


class TimeSeries:
    def __init__(self, stages_color='y'):
        self.stages_color = stages_color
        self.modules = {}

    def cpu(self, dataset, filename, stages):
        if len(dataset) > 0:
            x = numpy.arange(0, len(dataset) * config.LOG_INTERVAL, config.LOG_INTERVAL)
            y = numpy.array(dataset)
            if config.PLOT_PER_RESOURCE:
                plt.plot(x, y)
                # Add Stages Lines
                self.draw_stage(stages)
                plt.ylabel('Utilization (%)')
                plt.xlabel('Seconds')
                plt.title('Total CPU Utilization')
                plt.suptitle(os.path.basename(filename))
                plt.gca().yaxis.grid(True)
                plot_filename = utils.mkdir_p(filename + '_cpu_total.' + config.PLOT_FORMAT)
                plt.savefig(plot_filename)
                plt.close()
            return y.tolist()

    def cpu_multi(self, dataset, filename, stages):
        data = dataset['dataset']
        if len(data) > 0:
            # Plotting 1 line per worker
            x = numpy.arange(0, len(data) * config.LOG_INTERVAL, config.LOG_INTERVAL)
            y = numpy.array(data)
            plt.plot(x, y)
            # Add Stages Lines
            self.draw_stage(stages)

            plt.ylabel('Utilization (%)')
            plt.xlabel('Seconds')
            plt.legend([config.LABELS[worker] for worker in dataset['labels']], loc='lower left')
            plt.title('CPU Utilization per Machine')
            plt.gca().yaxis.grid(True)
            plt.suptitle(os.path.basename(filename))
            plot_filename = utils.mkdir_p(filename + '_cpu_machines.' + config.PLOT_FORMAT)
            plt.savefig(plot_filename)
            plt.close()

    def mem(self, dataset, filename, stages):
        if len(dataset) > 0:
            x = numpy.arange(0, len(dataset) * config.LOG_INTERVAL, config.LOG_INTERVAL)
            y = numpy.array(dataset)
            if config.PLOT_PER_RESOURCE:
                plt.plot(x, y)
                # Add Stages Lines
                self.draw_stage(stages)
                plt.ylabel('Utilization (%)')
                plt.xlabel('Seconds')
                plt.title('Total Memory Utilization')
                plt.suptitle(os.path.basename(filename))
                plt.gca().yaxis.grid(True)
                plot_filename = utils.mkdir_p(filename + '_memory_total.' + config.PLOT_FORMAT)
                plt.savefig(plot_filename)
                plt.close()
            return y.tolist()

    def mem_multi(self, dataset, filename, stages):
        data = dataset['dataset']
        if len(data) > 0:
            # Plotting 1 line per worker
            x = numpy.arange(0, len(data) * config.LOG_INTERVAL, config.LOG_INTERVAL)
            y = numpy.array(data)
            plt.plot(x, y)
            # Add Stages Lines
            self.draw_stage(stages)

            plt.ylabel('Utilization (%)')
            plt.xlabel('Seconds')
            plt.legend([config.LABELS[worker] for worker in dataset['labels']], loc='lower left')
            plt.title('Memory Utilization per Machine')
            plt.gca().yaxis.grid(True)
            plt.suptitle(os.path.basename(filename))
            plot_filename = utils.mkdir_p(filename + '_memory_machines.' + config.PLOT_FORMAT)
            plt.savefig(plot_filename)
            plt.close()

    def net(self, dataset, filename, stages):
        if len(dataset) > 0:
            x = numpy.arange(0, len(dataset) * config.LOG_INTERVAL, config.LOG_INTERVAL)
            y = numpy.array(dataset)
            if config.PLOT_PER_RESOURCE:
                plt.plot(x, y)
                # Add Stages Lines
                self.draw_stage(stages)
                plt.ylabel('Utilization (%)')
                plt.xlabel('Seconds')
                plt.title('Total Network Utilization')
                plt.suptitle(os.path.basename(filename))
                plt.ylim((0, 105))
                plt.gca().yaxis.grid(True)
                plot_filename = utils.mkdir_p(filename + '_net_total.' + config.PLOT_FORMAT)
                plt.savefig(plot_filename)
                plt.close()
            return y.tolist()

    def net_multi(self, dataset, filename, stages):
        data = dataset['dataset']
        if len(data) > 0:
            # Plotting 1 line per worker
            x = numpy.arange(0, len(data) * config.LOG_INTERVAL, config.LOG_INTERVAL)
            y = numpy.array(data)
            plt.plot(x, y)
            # Add Stages Lines
            self.draw_stage(stages)

            plt.ylabel('Utilization (%)')
            plt.xlabel('Seconds')
            plt.legend([config.LABELS[worker] for worker in dataset['labels']], loc='lower left')
            plt.title('Network Utilization per Machine')
            plt.ylim((0, 105))
            plt.gca().yaxis.grid(True)
            plt.suptitle(os.path.basename(filename))
            plot_filename = utils.mkdir_p(filename + '_net_machines.' + config.PLOT_FORMAT)
            plt.savefig(plot_filename)
            plt.close()

    def disk_busy(self, dataset, filename, stages):
        if len(dataset) > 0:
            x = numpy.arange(0, len(dataset) * config.LOG_INTERVAL, config.LOG_INTERVAL)
            y = numpy.array(dataset)
            if config.PLOT_PER_RESOURCE:
                plt.plot(x, y)
                # Add Stages Lines
                self.draw_stage(stages)
                plt.ylabel('Utilization (%)')
                plt.xlabel('Seconds')
                plt.ylim((0, 105))
                plt.title('Total Disk Utilization')
                plt.suptitle(os.path.basename(filename))
                plt.gca().yaxis.grid(True)
                plot_filename = utils.mkdir_p(filename + '_disk_busy_total.' + config.PLOT_FORMAT)
                plt.savefig(plot_filename)
                plt.close()

            return y.tolist()

    def disk_busy_multi(self, dataset, filename, stages):
        data = dataset['dataset']
        if len(data) > 0:
            # Plotting 1 line per worker
            x = numpy.arange(0, len(data) * config.LOG_INTERVAL, config.LOG_INTERVAL)
            y = numpy.array(data)
            plt.plot(x, y)
            # Add Stages Lines
            self.draw_stage(stages)

            plt.ylabel('Utilization (%)')
            plt.xlabel('Seconds')
            plt.ylim((0, 105))
            legend = []
            for worker in dataset['labels']:
                str_split = worker.split('_!_')
                legend.append(config.LABELS[str_split[0]] + ' ' + str_split[1])
            plt.legend(legend, loc='lower left')
            plt.title('Disk Utilization per Machine')
            plt.gca().yaxis.grid(True)
            plt.suptitle(os.path.basename(filename))
            plot_filename = utils.mkdir_p(filename + '_disk_busy_machines.' + config.PLOT_FORMAT)
            plt.savefig(plot_filename)
            plt.close()

    def disk_byte(self, dataset, filename, stages):
        if len(dataset) > 0:
            x = numpy.arange(0, len(dataset) * config.LOG_INTERVAL, config.LOG_INTERVAL)
            y = numpy.array(dataset)
            # Transform bytes to MBytes
            y /= (1024 * 1024)
            plt.plot(x, y)
            # Add Stages Lines
            self.draw_stage(stages)
            plt.ylabel('MBytes')
            plt.xlabel('Seconds')
            plt.title('Total Disk Byte Transfer')
            plt.suptitle(os.path.basename(filename))
            plt.gca().yaxis.grid(True)
            # plt.axes().set_yscale('log')
            plot_filename = utils.mkdir_p(filename + '_disk_byte_total.' + config.PLOT_FORMAT)
            plt.savefig(plot_filename)
            plt.close()

            return y.tolist()

    def disk_byte_multi(self, dataset, filename, stages):
        data = dataset['dataset']
        if len(data) > 0:
            # Plotting 1 line per worker
            x = numpy.arange(0, len(data) * config.LOG_INTERVAL, config.LOG_INTERVAL)
            y = numpy.array(data)
            # Transform bytes to MBytes
            y /= (1024 * 1024)
            plt.plot(x, y)
            # Add Stages Lines
            self.draw_stage(stages)

            plt.ylabel('MBytes')
            plt.xlabel('Seconds')
            legend = []
            for worker in dataset['labels']:
                str_split = worker.split('_!_')
                legend.append(config.LABELS[str_split[0]] + ' ' + str_split[1])
            plt.legend(legend, loc='lower left')
            plt.title('Disk Byte Transfer per Machine')
            plt.suptitle(os.path.basename(filename))
            plt.gca().yaxis.grid(True)
            plot_filename = utils.mkdir_p(filename + '_disk_byte_machines.' + config.PLOT_FORMAT)
            plt.savefig(plot_filename)
            plt.close()

    def disk_await(self, dataset, filename, stages):
        if len(dataset) > 0:
            x = numpy.arange(0, len(dataset) * config.LOG_INTERVAL, config.LOG_INTERVAL)
            y = numpy.array(dataset)
            plt.plot(x, y)
            # Add Stages Lines
            self.draw_stage(stages)
            plt.ylabel('Await Time (ms)')
            plt.xlabel('Seconds')
            plt.title('Total Disk Await Time')
            plt.suptitle(os.path.basename(filename))
            plt.gca().yaxis.grid(True)
            plt.axes().set_yscale('log')
            plot_filename = utils.mkdir_p(filename + '_disk_await_total.' + config.PLOT_FORMAT)
            plt.savefig(plot_filename)
            plt.close()

            return y.tolist()

    def disk_await_multi(self, dataset, filename, stages):
        data = dataset['dataset']
        if len(data) > 0:
            # Plotting 1 line per worker
            x = numpy.arange(0, len(data) * config.LOG_INTERVAL, config.LOG_INTERVAL)
            y = numpy.array(data)
            plt.plot(x, y)
            # Add Stages Lines
            self.draw_stage(stages)

            plt.ylabel('Await Time (ms)')
            plt.xlabel('Seconds')
            legend = []
            for worker in dataset['labels']:
                str_split = worker.split('_!_')
                legend.append(config.LABELS[str_split[0]] + ' ' + str_split[1])
            plt.legend(legend, loc='lower left')
            plt.title('Disk Await Time per Machine')
            plt.suptitle(os.path.basename(filename))
            plt.gca().yaxis.grid(True)
            plt.axes().set_yscale('log')
            plot_filename = utils.mkdir_p(filename + '_disk_await_machines.' + config.PLOT_FORMAT)
            plt.savefig(plot_filename)
            plt.close()

    def resources_utilization(self, dataset, filename, stages):
        for resource in dataset:
            if resource and len(resource) > 0:
                x = numpy.arange(0, len(resource) * config.LOG_INTERVAL, config.LOG_INTERVAL)
                y = numpy.array(resource)
                plt.plot(x, y)

        # Add Stages Lines
        self.draw_stage(stages)

        plt.ylim((0, 105))
        ylabel = plt.ylabel('Utilization (%)')
        xlabel = plt.xlabel('Seconds')
        if len(dataset) > 3:
            lgd_labels = ['CPU', 'Disk', 'Net', 'Net-lo']
        else:
            lgd_labels = ['CPU', 'Disk', 'Net']
        lgd = plt.legend(lgd_labels, loc='upper right',
                         bbox_to_anchor=(1.02, -0.1000), ncol=3)
        title = plt.title('Resource Utilization')
        plt.gca().yaxis.grid(True)
        plot_filename = utils.mkdir_p(filename + '_resource_utilization.' + config.PLOT_FORMAT)

        plt.savefig(plot_filename, bbox_extra_artists=(lgd, title, ylabel, xlabel), bbox_inches='tight')
        plt.close()

    def draw_stage(self, stages):
        # Add Stages Lines
        if stages:
            for s_id in stages["comp_times"]:
                x_pt = 0
                for value in stages["comp_times"][s_id]:
                    x_pt += value
                x_pt = int(x_pt / len(stages["comp_times"][s_id])) * config.LOG_INTERVAL
                plt.axvline(x=x_pt, color=self.stages_color, label=stages["id_names"][s_id] + ' End')
            for s_id in stages["sub_times"]:
                x_pt = 0
                for value in stages["sub_times"][s_id]:
                    x_pt += value
                x_pt = int(x_pt / len(stages["sub_times"][s_id])) * config.LOG_INTERVAL
                plt.axvline(x=x_pt, color=self.stages_color, label=stages["id_names"][s_id] + ' Start')
