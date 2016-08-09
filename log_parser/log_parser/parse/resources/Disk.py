from collections import namedtuple
import CPU
import numpy

__author__ = 'Pace Francesco'

sdiskio = namedtuple('sdiskio', ['read_count', 'write_count',
                                 'read_bytes', 'write_bytes',
                                 'read_time', 'write_time',
                                 'busy_time'])
pio = namedtuple('pio', ['read_count', 'write_count',
                         'read_bytes', 'write_bytes'])


def system(csv_row, disk):
    if disk:
        try:
            fields = [
                float(csv_row['sio_' + disk + '_read_count']),
                float(csv_row['sio_' + disk + '_write_count']),
                float(csv_row['sio_' + disk + '_read_bytes']),
                float(csv_row['sio_' + disk + '_write_bytes']),
                float(csv_row['sio_' + disk + '_read_time']),
                float(csv_row['sio_' + disk + '_write_time']),
                float(csv_row['sio_' + disk + '_busy_time'])
            ]
        except KeyError:
            # This part is necessary for retro compatibility with custom version of psutil
            fields = [
                float(csv_row['sio_' + disk + '_read_count']),
                float(csv_row['sio_' + disk + '_write_count']),
                float(csv_row['sio_' + disk + '_read_bytes']),
                float(csv_row['sio_' + disk + '_write_bytes']),
                float(csv_row['sio_' + disk + '_read_time']),
                float(csv_row['sio_' + disk + '_write_time']),
                float(csv_row['sio_' + disk + '_iotime'])
            ]
        return sdiskio(*fields)
    return None


def process(csv_row, disk):
    if disk:
        fields = [
            float(csv_row['pio_read_count']),
            float(csv_row['pio_write_count']),
            float(csv_row['pio_read_bytes']),
            float(csv_row['pio_write_bytes'])
        ]
        return pio(*fields)
    return None


def prepare_data_throughput(original_data):
    # Aggregate data per worker and per disk
    dataset_tmp = {}
    for worker in original_data:
        if worker not in dataset_tmp:
            dataset_tmp[worker] = {}
        for disk in original_data[worker]:
            if disk not in dataset_tmp[worker]:
                dataset_tmp[worker][disk] = []
            for value in original_data[worker][disk]:
                avg = sum(original_data[worker][disk][value]) / float(len(original_data[worker][disk][value]))
                try:
                    dataset_tmp[worker][disk][value].append(avg)
                except IndexError:
                    dataset_tmp[worker][disk].append([avg])
    dataset = []
    labels = []
    dataset_total = []
    tmp = []
    for worker in dataset_tmp:
        for disk in dataset_tmp[worker]:
            label_string = worker + '_!_' + disk
            if label_string not in labels:
                labels.append(label_string)
            for (index, value) in enumerate(dataset_tmp[worker][disk]):
                avg = sum(dataset_tmp[worker][disk][index]) / float(len(dataset_tmp[worker][disk][index]))
                try:
                    dataset[index].append(avg)
                    tmp[index].append(avg)
                except IndexError:
                    dataset.append([avg])
                    tmp.append([avg])
        for (index, value) in enumerate(tmp):
            # avg = sum(value) / float(len(value))
            total = sum(value)
            try:
                dataset_total[index].append(total)
            except IndexError:
                dataset_total.append([total])

    # Fill bucket with less then number of workers element with 0
    for bucket in dataset_total:
        if len(bucket) < len(original_data):
            for i in range(len(original_data) - len(bucket)):
                bucket.append(0)
    for bucket in dataset:
        if len(bucket) < len(label_string):
            for i in range(len(label_string) - len(bucket)):
                bucket.append(0)
    return \
        {'dataset': dataset, 'labels': labels}, \
        numpy.mean(numpy.array(dataset_total), axis=1).tolist()


def prepare_data(original_data):
    # Aggregate data per worker and per disk
    dataset_tmp = {}
    for worker in original_data:
        if worker not in dataset_tmp:
            dataset_tmp[worker] = {}
        for disk in original_data[worker]:
            if disk not in dataset_tmp[worker]:
                dataset_tmp[worker][disk] = []
            for value in original_data[worker][disk]:
                avg = sum(original_data[worker][disk][value]) / float(len(original_data[worker][disk][value]))
                try:
                    dataset_tmp[worker][disk][value].append(avg)
                except IndexError:
                    dataset_tmp[worker][disk].append([avg])
    dataset = []
    labels = []
    dataset_total = []
    tmp = []
    for worker in dataset_tmp:
        for disk in dataset_tmp[worker]:
            label_string = worker + '_!_' + disk
            if label_string not in labels:
                labels.append(label_string)
            for (index, value) in enumerate(dataset_tmp[worker][disk]):
                avg = sum(dataset_tmp[worker][disk][index]) / float(len(dataset_tmp[worker][disk][index]))
                try:
                    dataset[index].append(avg)
                    tmp[index].append(avg)
                except IndexError:
                    dataset.append([avg])
                    tmp.append([avg])
        for (index, value) in enumerate(tmp):
            avg = sum(value) / float(len(value))
            # maximum = max(value)
            try:
                dataset_total[index].append(avg)
            except IndexError:
                dataset_total.append([avg])

    # Fill bucket with less then number of workers element with 0
    for bucket in dataset_total:
        if len(bucket) < len(original_data):
            for i in range(len(original_data) - len(bucket)):
                bucket.append(0)
    for bucket in dataset:
        if len(bucket) < len(label_string):
            for i in range(len(label_string) - len(bucket)):
                bucket.append(0)
    return \
        {'dataset': dataset, 'labels': labels}, \
        numpy.mean(numpy.array(dataset_total), axis=1).tolist()


class System:
    def __init__(self):
        self._last_times_await = None
        self._last_times_busy = None
        self._last_cpu_times_busy = None
        self._last_bytes = None
        pass

    def byte(self, csv_row, disk):
        byte = self._last_bytes
        self._last_bytes = system(csv_row=csv_row, disk=disk)
        if not byte:
            return 0.0

        return (self._last_bytes.read_bytes + self._last_bytes.write_bytes) - (byte.read_bytes + byte.write_bytes)

    def busy(self, csv_row, disk):
        prev_times = self._last_times_busy
        prev_cpu_times = self._last_cpu_times_busy
        self._last_times_busy = system(csv_row=csv_row, disk=disk)
        self._last_cpu_times_busy = CPU.system_no_guest(csv_row=csv_row)

        if not prev_times and not prev_cpu_times:
            return 0.0
        num_cpu = float(csv_row['cpu_count'])
        result = 100 * (self._last_times_busy.busy_time - prev_times.busy_time) / (
            (sum(self._last_cpu_times_busy) - sum(prev_cpu_times)) / num_cpu * 1000.0)
        if result > 100:
            result = 100
        return result

    def await(self, csv_row, disk):
        prev_times = self._last_times_await
        self._last_times_await = system(csv_row=csv_row, disk=disk)

        if not prev_times:
            return 0.0

        prev_nr_ios = prev_times.read_count + prev_times.write_count
        cur_nr_ios = self._last_times_await.read_count + self._last_times_await.write_count
        delta_nr_ios = cur_nr_ios - prev_nr_ios
        if delta_nr_ios <= 0:
            return 0.0
        else:
            return ((self._last_times_await.read_time - prev_times.read_time) + (
                self._last_times_await.write_time - prev_times.write_time)) / float(delta_nr_ios)


class Process:
    def __init__(self):
        self._last_sys_cpu_times = None
        self._last_proc_cpu_times = None
