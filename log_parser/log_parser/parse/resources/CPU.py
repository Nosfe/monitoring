from collections import namedtuple
import numpy

__author__ = 'Pace Francesco'

scputimes = namedtuple('scputimes',
                       ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice'])
pcputimes = namedtuple('pcputimes', ['user', 'system'])


def system(csv_row):
    fields = [
        float(csv_row['scpu_user']),
        float(csv_row['scpu_nice']),
        float(csv_row['scpu_system']),
        float(csv_row['scpu_idle']),
        float(csv_row['scpu_iowait']),
        float(csv_row['scpu_irq']),
        float(csv_row['scpu_softirq']),
        float(csv_row['scpu_steal']),
        float(csv_row['scpu_guest']),
        float(csv_row['scpu_guest_nice']),
    ]
    return scputimes(*fields)


def system_no_guest(csv_row):
    fields = [
        float(csv_row['scpu_user']),
        float(csv_row['scpu_nice']),
        float(csv_row['scpu_system']),
        float(csv_row['scpu_idle']),
        float(csv_row['scpu_iowait']),
        float(csv_row['scpu_irq']),
        float(csv_row['scpu_softirq']),
        float(csv_row['scpu_steal']),
        float(0),
        float(0),
    ]
    return scputimes(*fields)


def process(csv_row):
    fields = [
        float(csv_row['pcpu_user']),
        float(csv_row['pcpu_system'])
    ]
    return pcputimes(*fields)


def prepare_data(original_data):
    # Aggregate data per worker and average value for buckets
    dataset = []
    for worker in original_data:
        for value in original_data[worker]:
            avg = sum(original_data[worker][value]) / float(len(original_data[worker][value]))
            try:
                dataset[value].append(avg)
            except IndexError:
                dataset.append([avg])

    # Fill bucket with less then number of workers element with 0
    for bucket in dataset:
        if len(bucket) < len(original_data):
            for i in range(len(original_data) - len(bucket)):
                bucket.append(0)
    return \
        {'dataset': dataset, 'labels': [worker for worker in original_data]},\
        numpy.mean(numpy.array(dataset), axis=1).tolist()


class System:
    def __init__(self):
        self._last_times = scputimes(*[0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        pass

    def percent(self, csv_row):
        previous_cpu_times = self._last_times
        self._last_times = system_no_guest(csv_row=csv_row)

        t1_all = sum(previous_cpu_times)
        t1_busy = t1_all - previous_cpu_times.idle - previous_cpu_times.iowait

        t2_all = sum(self._last_times)
        t2_busy = t2_all - self._last_times.idle - self._last_times.iowait

        # this usually indicates a float precision issue
        if t2_busy <= t1_busy:
            return 0.0

        busy_delta = t2_busy - t1_busy
        all_delta = t2_all - t1_all
        busy_perc = (busy_delta / all_delta) * 100
        return round(busy_perc, 1)


class Process:
    def __init__(self):
        self._prev_sys_times = None
        self._prev_proc_times = None
        pass

    def percent(self, csv_row):
        st1 = self._prev_sys_times
        pt1 = self._prev_proc_times
        st2 = sum(system(csv_row=csv_row))
        pt2 = process(csv_row=csv_row)
        if st1 is None or pt1 is None:
            self._prev_sys_times = st2
            self._prev_proc_times = pt2
            return 0.0

        delta_proc = (pt2.user - pt1.user) + (pt2.system - pt1.system)
        delta_time = st2 - st1
        # reset values for next call in case of interval == None
        self._prev_sys_times = st2
        self._prev_proc_times = pt2

        try:
            # The utilization split between all CPUs.
            # Note: a percentage > 100 is legitimate as it can result
            # from a process with multiple threads running on different
            # CPU cores, see:
            # http://stackoverflow.com/questions/1032357
            # https://github.com/giampaolo/psutil/issues/474
            overall_percent = ((delta_proc / delta_time) * 100)
        except ZeroDivisionError:
            # interval was too low
            return 0.0
        else:
            return round(overall_percent, 1)
