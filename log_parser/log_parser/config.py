__author__ = 'Pace Francesco'

# Target folder for plots
PLOT_DIR = '../plots'

# Absolute path for the logs generated with the monitoring daemon
# the folder structure must be the following:
#
#     <base>
#     |_<scenario_0>
#       |_<workload_0>
#         |_logs
#           |_<iteration_0>
#             |_<hostname>
#               |_<monitoring daemon logs files>
#
LOGS_PATH = 'D:\\Nosfe\\Documents\\Education\\Eurecom\\MasterVM\\Logs\\IBM\\first_set'

# A dictionary of the workloads to be parsed
#     key   = folder_name
#     value = label
WORKLOADS = {
    'wordcount': 'WordCount',
    'wordcount_logSwift': 'WordCount',
    'dfsio': 'DFSIO',
    'tpcds': 'TPC-DS',
    'decision_tree': 'Decision_Tree'
}

# A dictionary of the scenarios to be parsed
#     key   = folder_name
#     value = label
SCENARIOS = {
    'guest-coloc': "GC",
    'guest-coloc-volume-ceph': "GC-Vs",
    'guest-coloc-volume-both': "GC-Vb",
    'guest-coloc-volume-hdfs': "GC-Vh",
    'no-coloc': "NC",
    'swift': "SWI",
    'swift_ibm': "SWI-IBM",
}

# A dictionary of the disks to be considered during the parse
#     key   = disk_label
#     value = list of hostname
DISKS = {
    'vda1': [
        'guest-coloc-s-dn-001',
        'guest-coloc-s-dn-002',
        'guest-coloc-s-dn-003',
        'guest-coloc-s-dn-004',
        'guest-coloc-m-nn-001',

        'compute-s-001',
        'compute-s-002',
        'compute-s-003',
        'compute-s-004',
        'compute-m-001',

        'hdfs-dn-001',
        'hdfs-dn-002',
        'hdfs-dn-003',
        'hdfs-dn-004',
        'hdfs-nn-001',

        'guest-coloc-volume-s-dn-volume-001',
        'guest-coloc-volume-s-dn-volume-002',
        'guest-coloc-volume-s-dn-volume-003',
        'guest-coloc-volume-s-dn-volume-004',
        'guest-coloc-volume-m-nn-volume-001',

    ],
    'vdb': [
        'guest-coloc-volume-s-dn-volume-001',
        'guest-coloc-volume-s-dn-volume-002',
        'guest-coloc-volume-s-dn-volume-003',
        'guest-coloc-volume-s-dn-volume-004',
        'guest-coloc-volume-m-nn-volume-001',

    ],
    'sdb1': [
        'pace@bfeb'
    ],
    'sdc1': [
        'pace@bfeb'
    ],
    'sdd1': [
        'pace@bfeb'
    ],
    'sde1': [
        'pace@bfeb'
    ]

}

# A dictionary of the labels for the hosts
#     key   = hostname
#     value = label
LABELS = {
    'guest-coloc-s-dn-001': 'Worker 1',
    'guest-coloc-s-dn-002': 'Worker 2',
    'guest-coloc-s-dn-003': 'Worker 3',
    'guest-coloc-s-dn-004': 'Worker 4',
    'guest-coloc-m-nn-001': 'Master 1',

    'guest-coloc-volume-s-dn-volume-001': 'Worker 1',
    'guest-coloc-volume-s-dn-volume-002': 'Worker 2',
    'guest-coloc-volume-s-dn-volume-003': 'Worker 3',
    'guest-coloc-volume-s-dn-volume-004': 'Worker 4',
    'guest-coloc-volume-m-nn-volume-001': 'Master 1',

    'compute-s-001': 'Worker 1',
    'compute-s-002': 'Worker 2',
    'compute-s-003': 'Worker 3',
    'compute-s-004': 'Worker 4',
    'compute-m-001': 'Master 1',

    'hdfs-dn-001': 'DataNode 1',
    'hdfs-dn-002': 'DataNode 2',
    'hdfs-dn-003': 'DataNode 3',
    'hdfs-dn-004': 'DataNode 4',
    'hdfs-nn-001': 'NameNode 1',

    'pace@bfeb': 'Swift',
}

# Set the (supposedly) best scenario so that we can calculate the run time difference when using others
BEST_SCENARIO = 'GC'

# Set to True if you already have the parsed dataset and you want to generate just the plots
PLOTS_ONLY = False

# Set to True if you want to plot metrics for every single host
PLOT_PER_HOST = False
# Set to True if you want to plot disk metrics for every single disk (id = name of disk)
PLOT_PER_DISK = False
# Set to True if you want to plot different figure for each resource
PLOT_PER_RESOURCE = False

# Set to True if you want to plot disk await
PLOT_DISK_AWAIT = False
# Set to True if you want to plot disk throughput
PLOT_DISK_BYTE = False
# Set to True if you want to plot CDFs
PLOT_CDF = False
# Set to True if you want to plot TimeSeries
PLOT_TIMESERIES = False
# Set to True if you want to plot BoxPlots
PLOT_BOXPLOTS = False
# Set to True if you want to plot BarCharts
PLOT_BARCHARTS = True
# Set to True if you want to show stages' lines inside figures
SHOW_STAGES = False
# Set to True if you want to draw figure in black and white format
PLOT_BW = False

# File format of the generate plots
PLOT_FORMAT = 'pdf'
# Plot fond size
PLOT_FONT_SIZE = 17.5

# Monitoring Daemon resource polling interval
LOG_INTERVAL = 1

# Following 2 Values expressed in MB
DISK_TOTAL_THROUGHPUT = 100
NET_TOTAL_THROUGHPUT = 125
