from collections import namedtuple
import numpy

__author__ = 'Pace Francesco'

smem = namedtuple('smem',
                  ['total', 'available', 'percent', 'used', 'free', 'active', 'inactive', 'buffers', 'cached'])


def system(csv_row):
    fields = [
        float(0),
        float(0),
        float(csv_row['smem_percent']),
        float(0),
        float(0),
        float(0),
        float(0),
        float(0),
        float(0),
    ]
    return smem(*fields)


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
        {'dataset': dataset, 'labels': [worker for worker in original_data]}, \
        numpy.mean(numpy.array(dataset), axis=1).tolist()


class System:
    def __init__(self):
        pass

    def percent(self, csv_row):
        return system(csv_row=csv_row).percent
