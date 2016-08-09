import csv
import logging
import os
import threading
import time
from collections import OrderedDict

import psutil

from monitoring_daemon import config
from monitoring_daemon.utils import Utils

__author__ = 'Pace Francesco'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def launch(event_listener=None, pid=None, folder_path=""):
    thread = None
    if pid is not None:
        logger.error("# Monitoring a specific process is not yet supported. Sorry :(")
        exit(-3)
        # import processEvents
        # nl_sock = processEvents.nl_connect()
        # if nl_sock <= 0:
        #     print("# Error connecting to the socket")
        #     exit(-1)
        # ret_value = processEvents.set_proc_ev_listen(nl_sock)
        # if ret_value != 0:
        #     print("# Error setting the socket to listen at Process Events")
        #     exit(-2)
        # processes = array('i')
        # print("# Monitoring Process Resources for PID: {}".format(pid))
        # print("#    Folder to Log is: {}".format(log_folder_name))
        # print("#    Process Filter is: {}".format(process_filter))
        # MonitorThread(event=event, process=psutil.Process(pid), log_folder_name=log_folder_name).start()
        # processes.append(pid)
        # while len(processes) != 0:
        #     new_pid = processEvents.handle_proc_ev(nl_sock, pid)
        #     if new_pid > 0:
        #         try:
        #             process = psutil.Process(new_pid)
        #             if new_pid not in processes:
        #                 if process_filter is not None:
        #                     cmdline = " ".join(process.cmdline())
        #                     if process_filter in cmdline:
        #                         MonitorThread(event=event, process=process, log_folder_name=log_folder_name,
        #                                       file_prefix='{}_fork_'.format(pid)).start()
        #                         processes.append(new_pid)
        #
        #         except psutil.NoSuchProcess:
        #             pass
        #     # processEvents.handle_proc_ev return a negative number (-pid)
        #     # if the process that we were listening no longer exist, therefore remove from the list
        #     elif new_pid < 0:
        #         try:
        #             processes.remove(new_pid)
        #         except ValueError:
        #             pass
    else:
        thread = MonitorThread(event=event_listener, log_folder_path=folder_path)
        thread.start()
        thread.join()
    return thread


class MonitorThread(threading.Thread):
    def __init__(self, event=None, process=None, log_folder_path="", file_prefix=""):
        threading.Thread.__init__(self)
        self.process = process
        self.event = event
        self.log_folder_path = log_folder_path
        self.file_prefix = file_prefix
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def run(self):
        Utils.mkdir_p(self.log_folder_path)
        if self.process is None:
            output_filename = os.path.join(self.log_folder_path, self.file_prefix + 'system.csv')
        else:
            output_filename = os.path.join(self.log_folder_path, self.file_prefix + '{!s}.csv'.format(self.process.pid))

        num_cpu = psutil.cpu_count()

        with open(output_filename, "w") as output_file:
            dict_writer = None
            try:
                while self.event.is_set():
                    to_csv = OrderedDict({
                        'epoch(s)': time.time()
                    })

                    # In this way epoch(s) in the first value in the cvs line, and cpu_count the second
                    to_csv['cpu_count'] = num_cpu
                    scputimes_dict = psutil.cpu_times().__dict__
                    for key in scputimes_dict:
                        to_csv['scpu_' + key] = scputimes_dict[key]
                    if self.process is not None:
                        pcputimes_dict = self.process.cpu_times().__dict__
                        for key in pcputimes_dict:
                            to_csv['pcpu_' + key] = pcputimes_dict[key]

                    sio_dict = psutil.disk_io_counters(True)
                    for key in sio_dict:
                        i = 0
                        for key1 in sio_dict[key].__dict__:
                            to_csv['sio_' + key + '_' + key1] = sio_dict[key][i]
                            i += 1
                    if self.process is not None:
                        pio_dict = self.process.io_counters().__dict__
                        for key in pio_dict:
                            to_csv['pio_' + key] = pio_dict[key]

                    snetio_dict = psutil.net_io_counters(True)
                    for key in snetio_dict:
                        i = 0
                        for key1 in snetio_dict[key].__dict__:
                            to_csv['snetio_' + key + '_' + key1] = snetio_dict[key][i]
                            i += 1
                    snetio_dict = psutil.net_io_counters().__dict__
                    for key in snetio_dict:
                        to_csv['snetio_' + key] = snetio_dict[key]

                    smem_dict = psutil.virtual_memory().__dict__
                    for key in smem_dict:
                        to_csv['smem_' + key] = smem_dict[key]

                    if dict_writer is None:
                        dict_writer = csv.DictWriter(output_file, to_csv.keys())
                        dict_writer.writeheader()
                    dict_writer.writerow(to_csv)

                    time.sleep(config.POLLING_INTERVAL)
            except psutil.NoSuchProcess:
                self.logger.error("# psutil.NoSuchProcess triggered")
                return 0
