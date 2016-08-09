import numpy

import config

__author__ = 'Pace Francesco'


def prepare_data(original_data):
    net_throughput_mb = config.NET_TOTAL_THROUGHPUT * 1024 * 1024
    # Aggregate data per worker
    dataset = []
    for worker in original_data:
        previous_value = None
        for value in original_data[worker]:
            avg = sum(original_data[worker][value]) / float(len(original_data[worker][value]))
            avg_percent = 0
            if previous_value:
                avg_percent = ((avg - previous_value) / config.LOG_INTERVAL) * 100 / net_throughput_mb
            try:
                dataset[value].append(avg_percent)
            except IndexError:
                dataset.append([avg_percent])
            previous_value = avg

    # Fill bucket with less then number of workers element with 0
    for bucket in dataset:
        if len(bucket) < len(original_data):
            for i in range(len(original_data) - len(bucket)):
                bucket.append(0)
    return \
        {'dataset': dataset, 'labels': [worker for worker in original_data]},\
        numpy.mean(numpy.array(dataset), axis=1).tolist()
