import csv
import glob
import json
import math
import os
import sys
from collections import OrderedDict

import matplotlib
import numpy

import config
import utils.utils as utils
from graphs.BarCharts import BarCharts
from graphs.BoxPlots import BoxPlots
from graphs.CDFs import CDFs
from graphs.TimeSeries import TimeSeries
from log_parser.parse.resources import Memory
from log_parser.utils.Logger import Logger
from parse.resources import CPU, Disk, Network
from parse.spark.event.spark_run import SparkRun
from parse.swift.log_file import parse_lines
from parse.spark.logs import parser as spark_logs_parser

__author__ = 'Pace Francesco'


def stage_task_breakdown(app_data):
    stages = []
    for i in app_data.jobs:
        for s in app_data.jobs[i].stages:
            stage = {
                "id": s.stage_id,
                "name": s.name.split()[0],
                "n_tasks": len(s.tasks),
                "runtimes": [t.finish_time - t.launch_time for t in s.tasks if t.end_reason == "Success"],
                "submission_time": s.submission_time,
                "completion_time": s.completion_time
            }
            stages.append(stage)
    return stages


def generate_time_series(dataset=None, stages=None, label="", plot_dir=""):
    if dataset is None:
        return

    time_series = TimeSeries()
    s_cpu = s_disk_busy = s_net = s_net_loop = None
    filename = os.path.join(plot_dir, label + '_' + os.path.basename(plot_dir))
    for role in dataset:
        # SYSTEM
        # Per Machine
        if len(dataset[role]['s_cpu']['multi']) != 0:
            time_series.cpu_multi(dataset[role]['s_cpu']['multi'], filename + "_" + role, stages)
        if len(dataset[role]['s_net']['multi']) != 0:
            time_series.net_multi(dataset[role]['s_net']['multi'], filename + "_" + role, stages)
        if len(dataset[role]['s_net_only_loop']['multi']) != 0:
            time_series.net_multi(dataset[role]['s_net_only_loop']['multi'], filename + "_" + role + "_only_loop",
                                  stages)
        if len(dataset[role]['s_disk_busy']['multi']) != 0:
            time_series.disk_busy_multi(dataset[role]['s_disk_busy']['multi'], filename + "_" + role, stages)
        if len(dataset[role]['s_mem']['multi']) != 0:
            time_series.mem_multi(dataset[role]['s_mem']['multi'], filename + "_" + role, stages)
        if config.PLOT_DISK_AWAIT:
            if len(dataset[role]['s_disk_await']['multi']) != 0:
                time_series.disk_await_multi(dataset[role]['s_disk_await']['multi'], filename + "_" + role, stages)
        if config.PLOT_DISK_BYTE:
            if len(dataset[role]['s_disk_byte']['multi']) != 0:
                time_series.disk_byte_multi(dataset[role]['s_disk_byte']['multi'], filename + "_" + role, stages)

        # Average
        if len(dataset[role]['s_cpu']['single']) != 0:
            s_cpu = time_series.cpu(dataset[role]['s_cpu']['single'], filename + "_" + role, stages)
        if len(dataset[role]['s_disk_busy']['single']) != 0:
            s_disk_busy = time_series.disk_busy(dataset[role]['s_disk_busy']['single'],
                                                filename + "_" + role, stages)
        if len(dataset[role]['s_mem']['single']) != 0:
            time_series.mem(dataset[role]['s_mem']['single'], filename + "_" + role, stages)
        if config.PLOT_DISK_AWAIT:
            if len(dataset[role]['s_disk_await']['single']) != 0:
                time_series.disk_await(dataset[role]['s_disk_await']['single'], filename + "_" + role, stages)
        if config.PLOT_DISK_BYTE:
            if len(dataset[role]['s_disk_byte']['single']) != 0:
                time_series.disk_byte(dataset[role]['s_disk_byte']['single'], filename + "_" + role, stages)
        if len(dataset[role]['s_net']['single']) != 0:
            s_net = time_series.net(dataset[role]['s_net']['single'], filename + "_" + role, stages)
        if len(dataset[role]['s_net_only_loop']['single']) != 0:
            s_net_loop = time_series.net(dataset[role]['s_net_only_loop']['single'],
                                         filename + "_" + role + "_only_loop", stages)

        if s_cpu and s_disk_busy and s_net and s_net_loop:
            if role == 'swift':
                time_series.resources_utilization([s_cpu, s_disk_busy, s_net], filename + "_" + role, stages)
            else:
                time_series.resources_utilization([s_cpu, s_disk_busy, s_net, s_net_loop], filename + "_" + role,
                                                  stages)


def parse_csvs(app_dir=None, spark_event=None, run_stages=None, run_jobs=None):
    def initialize_array(resource=None):
        if resource:
            if worker_name not in usages[process_type][resource]:
                usages[process_type][resource][worker_name] = OrderedDict({})
            if not disk:
                if bucket not in usages[process_type][resource][worker_name]:
                    usages[process_type][resource][worker_name][bucket] = []
            else:
                if disk not in usages[process_type][resource][worker_name]:
                    usages[process_type][resource][worker_name][disk] = OrderedDict({})
                if bucket not in usages[process_type][resource][worker_name][disk]:
                    usages[process_type][resource][worker_name][disk][bucket] = []
            return
        raise Exception('Could not initialize array for resource {}'.format(resource))

    if app_dir is None or spark_event is None or run_stages is None or run_jobs is None:
        return

    disk = None
    usages = OrderedDict({})
    stages = OrderedDict({
        "comp_times": OrderedDict({}),
        "sub_times": OrderedDict({}),
        "id_names": {}
    })

    jobs = {}
    for j in run_jobs:
        jobs[j] = {
            'submission_time': [],
            'end_time': []
        }

    for ROOT, SUBDIRS, FILES in os.walk(app_dir):
        for csvfilename in glob.iglob(os.path.join(ROOT, '*.csv')):
            # ['..', '<logs>', <scenario>, <workload>, 'logs', <app_iteration>, <hostname>, <processLabel>, <filename>]
            split_path = csvfilename.split(os.sep)
            path_length = len(split_path)

            # instead of using split_path[7], we use split_path[path_length-2] to make sure it the program can
            # work with the different length paths
            process_type = split_path[path_length - 2]

            if process_type not in usages:
                usages[process_type] = OrderedDict({
                    's_cpu': OrderedDict({}),
                    's_disk_busy': OrderedDict({}),
                    's_disk_await': OrderedDict({}),
                    's_disk_byte': OrderedDict({}),
                    's_net': OrderedDict({}),
                    's_net_only_loop': OrderedDict({}),
                    's_mem': OrderedDict({}),
                })

            worker_name = split_path[path_length - 3]

            with open(csvfilename) as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
                scpu = CPU.System()
                smem = Memory.System()
                # pcpu = CPU.Process()
                sdisk = {}
                if len(rows) > 20:
                    i = 0
                    for row in rows:
                        row_time = int(float(row['epoch(s)']))
                        if spark_event:
                            if row_time < int(int(spark_event.parsed_data['app_start_timestamp']) / 1000):
                                i = 0
                                continue
                            if row_time > int(int(spark_event.parsed_data['app_end_timestamp']) / 1000):
                                break

                        bucket = int(i)
                        if config.SHOW_STAGES and workload != 'tpcds':
                            for s in run_stages:
                                if s["id"] not in stages["id_names"]:
                                    stages["id_names"][s["id"]] = s["name"]
                                if s["submission_time"] is not None and s["completion_time"] is not None:
                                    sub_time = int(s["submission_time"] / 1000)
                                    comp_time = int(s["completion_time"] / 1000)
                                    if row_time == sub_time:
                                        if s["id"] not in stages["sub_times"]:
                                            stages["sub_times"][s["id"]] = []
                                        stages["sub_times"][s["id"]].append(bucket)

                                    if row_time == comp_time:
                                        if s["id"] not in stages["comp_times"]:
                                            stages["comp_times"][s["id"]] = []
                                        stages["comp_times"][s["id"]].append(bucket)

                        for j in run_jobs:
                            end_time = int(int(run_jobs[j].end_time) / 1000)
                            submission_time = int(int(run_jobs[j].submission_time) / 1000)
                            if row_time == end_time:
                                jobs[j]['end_time'].append(bucket)
                            if row_time == submission_time:
                                jobs[j]['submission_time'].append(bucket)

                        ##
                        # System Statistics
                        ##
                        # CPU
                        if 'scpu_guest_nice' in row and row['scpu_guest_nice']:
                            initialize_array('s_cpu')
                            usages[process_type]['s_cpu'][worker_name][bucket].append(scpu.percent(csv_row=row))
                        # DISK
                        for disk in config.DISKS:
                            disk_csv_old = 'sio_' + disk + '_iotime'
                            disk_csv = 'sio_' + disk + '_busy_time'
                            if worker_name in config.DISKS[disk] and (
                                        (disk_csv in row and row[disk_csv]) or (
                                                    disk_csv_old in row and row[disk_csv_old])):
                                if disk not in sdisk:
                                    sdisk[disk] = Disk.System()
                                initialize_array('s_disk_busy')
                                usages[process_type]['s_disk_busy'][worker_name][disk][bucket].append(
                                    sdisk[disk].busy(csv_row=row, disk=disk))
                                if config.PLOT_DISK_AWAIT:
                                    initialize_array('s_disk_await')
                                    usages[process_type]['s_disk_await'][worker_name][disk][bucket].append(
                                        sdisk[disk].await(csv_row=row, disk=disk))
                                if config.PLOT_DISK_BYTE:
                                    initialize_array('s_disk_byte')
                                    usages[process_type]['s_disk_byte'][worker_name][disk][bucket].append(
                                        sdisk[disk].byte(csv_row=row, disk=disk))
                        disk = None
                        # NET
                        if process_type == 'Swift':
                            if 'snetio_em2_bytes_sent' in row and row['snetio_em2_bytes_sent'] \
                                    and 'snetio_em2_bytes_recv' in row and row['snetio_em2_bytes_recv']:
                                initialize_array('s_net')
                                usages[process_type]['s_net'][worker_name][bucket].append(
                                    int(row['snetio_em2_bytes_sent']) + int(row['snetio_em2_bytes_recv']))
                        else:
                            if 'snetio_bytes_sent' in row and row['snetio_bytes_sent'] \
                                    and 'snetio_bytes_recv' in row and row['snetio_bytes_recv'] \
                                    and 'snetio_lo_bytes_sent' in row and row['snetio_lo_bytes_sent'] \
                                    and 'snetio_lo_bytes_recv' in row and row['snetio_lo_bytes_recv']:
                                initialize_array('s_net')
                                usages[process_type]['s_net'][worker_name][bucket].append(
                                    int(row['snetio_bytes_sent']) + int(row['snetio_bytes_recv']) -
                                    (int(row['snetio_lo_bytes_sent']) + int(row['snetio_lo_bytes_recv']))
                                )
                        # LOOPBACK
                        if 'snetio_lo_bytes_sent' in row and row['snetio_lo_bytes_sent'] \
                                and 'snetio_lo_bytes_recv' in row and row['snetio_lo_bytes_recv']:
                            initialize_array('s_net_only_loop')
                            usages[process_type]['s_net_only_loop'][worker_name][bucket].append(
                                int(row['snetio_lo_bytes_sent']) + int(row['snetio_lo_bytes_recv']))

                        # MEMORY
                        if 'smem_percent' in row and row['smem_percent']:
                            initialize_array('s_mem')
                            usages[process_type]['s_mem'][worker_name][bucket].append(smem.percent(csv_row=row))

                        i += 1
                else:
                    print "# Skipping the parsing of file {} because has not enough records in it!".format(csvfilename)

    if workload == 'tpcds' or workload == 'decision_tree' or not config.SHOW_STAGES:
        stages = None

    for j in jobs:
        if len(jobs[j]['submission_time']) == 0 or len(jobs[j]['end_time']) == 0:
            continue
        sub_time = int(sum(jobs[j]['submission_time']) / len(jobs[j]['submission_time']))
        end_time = int(sum(jobs[j]['end_time']) / len(jobs[j]['end_time']))
        jobs[j] = {
            'submission_time': sub_time,
            'end_time': end_time
        }

    return usages, stages, jobs


def parse_app(path, scenario, workload):
    best_iteration = {
        'runtime': sys.maxint,
        'spark_event': None,
        'root': None,
        'run_stages': None,
        'dataset': None,
        'stages': None
    }
    worst_iteration = {
        'runtime': 0,
        'spark_event': None,
        'root': None,
        'run_stages': None,
        'dataset': None,
        'stages': None
    }
    runtimes = []
    app_runs_stages = []
    cdfs = OrderedDict({})
    task_runtimes = OrderedDict({})
    swift_log = []

    for SUBDIR in os.listdir(path):
        total_requests_from_spark = 0
        ROOT = os.path.join(path, SUBDIR)
        for file_or_dir in os.listdir(os.path.join(ROOT, 'spark_logs')):
            if os.path.isfile(os.path.join(ROOT, 'spark_logs', file_or_dir)):
                filename = file_or_dir
                file_ext = os.path.splitext(filename)[-1]
                if '' == file_ext and filename != "empty":
                    try:
                        spark_event = SparkRun(os.path.join(ROOT, 'spark_logs', filename))
                    except ValueError:
                        continue
                    spark_event.correlate()

                    waves = 0
                    for job in spark_event.jobs:
                        for stage in spark_event.jobs[job].stages:
                            if stage.task_num == 0:
                                waves += 1
                            else:
                                waves += int(math.ceil(stage.task_num / 16))
                    for task in spark_event.tasks:
                        # We check if the task was not discarded (another task finished before)
                        #  because of speculative execution
                        if spark_event.tasks[task].finish_time is not None:
                            try:
                                task_runtimes[spark_event.tasks[task].type].append(
                                    (
                                        spark_event.tasks[task].finish_time - spark_event.tasks[
                                            task].launch_time) / 1000.0)
                            except KeyError:
                                task_runtimes[spark_event.tasks[task].type] = \
                                    [(spark_event.tasks[task].finish_time - spark_event.tasks[task].launch_time) / 1000.0]
                    runtime = spark_event.parsed_data["application_runtime"]
                    runtime_job = 0
                    for j in spark_event.jobs:
                        runtime_job += spark_event.jobs[j].end_time - spark_event.jobs[j].submission_time
                    runtimes.append(runtime)
                    run_stages = stage_task_breakdown(spark_event)
                    print "#     Number of job is {}".format(len(spark_event.jobs))
                    print "#     Number of task is {}".format(len(spark_event.tasks))
                    print "#     Number of waves is {}".format(waves)
                    print "#     Application's Runtime is {}s".format(runtime / 1000)
                    print "#     Jobs' Runtime {}s".format(runtime_job / 1000)

                    raw_data, stages, jobs = parse_csvs(app_dir=os.path.join(ROOT, 'logs'),
                                                        spark_event=spark_event, run_stages=run_stages,
                                                        run_jobs=spark_event.jobs)
                    dataset = OrderedDict({})
                    for role in raw_data:
                        dataset[role] = OrderedDict({
                            's_cpu': {
                                'single': None,
                                'multi': None
                            },
                            's_disk_busy': {
                                'single': None,
                                'multi': None
                            },
                            's_net': {
                                'single': None,
                                'multi': None
                            },
                            's_net_only_loop': {
                                'single': None,
                                'multi': None
                            },
                            's_disk_await': {
                                'single': None,
                                'multi': None
                            },
                            's_disk_byte': {
                                'single': None,
                                'multi': None
                            },
                            's_mem': {
                                'single': None,
                                'multi': None
                            }

                        })
                        dataset[role]['s_cpu']['multi'], dataset[role]['s_cpu']['single'] = CPU.prepare_data(
                            raw_data[role]['s_cpu'])
                        dataset[role]['s_disk_busy']['multi'], dataset[role]['s_disk_busy'][
                            'single'] = Disk.prepare_data(raw_data[role]['s_disk_busy'])
                        if config.PLOT_DISK_AWAIT:
                            dataset[role]['s_disk_await']['multi'], dataset[role]['s_disk_await'][
                                'single'] = Disk.prepare_data(raw_data[role]['s_disk_await'])
                        if config.PLOT_DISK_BYTE:
                            dataset[role]['s_disk_byte']['multi'], dataset[role]['s_disk_byte'][
                                'single'] = Disk.prepare_data_throughput(raw_data[role]['s_disk_byte'])
                        dataset[role]['s_net']['multi'], dataset[role]['s_net']['single'] = Network.prepare_data(
                            raw_data[role]['s_net'])
                        dataset[role]['s_net_only_loop']['multi'], dataset[role]['s_net_only_loop'][
                            'single'] = Network.prepare_data(raw_data[role]['s_net_only_loop'])
                        dataset[role]['s_mem']['multi'], dataset[role]['s_mem'][
                            'single'] = Memory.prepare_data(raw_data[role]['s_mem'])

                        if role not in cdfs:
                            cdfs[role] = OrderedDict({
                                's_cpu': [],
                                's_disk_busy': [],
                                's_net': [],
                                's_net_only_loop': [],
                                's_disk_bytes': []
                            })
                        cdfs[role]['s_cpu'] = dataset[role]['s_cpu']['single']
                        cdfs[role]['s_disk_busy'] = dataset[role]['s_disk_busy']['single']
                        cdfs[role]['s_disk_byte'] = dataset[role]['s_disk_byte']['single']
                        cdfs[role]['s_net'] = dataset[role]['s_net']['single']
                        cdfs[role]['s_net_only_loop'] = dataset[role]['s_net_only_loop']['single']

                    if runtime > worst_iteration['runtime']:
                        worst_iteration['runtime'] = runtime
                        worst_iteration['root'] = ROOT
                        # worst_iteration['spark_event'] = spark_event.parsed_data
                        worst_iteration['run_stages'] = run_stages
                        worst_iteration['dataset'] = dataset
                        worst_iteration['stages'] = stages
                    if runtime <= best_iteration['runtime']:
                        best_iteration['runtime'] = runtime
                        best_iteration['root'] = ROOT
                        # best_iteration['spark_event'] = spark_event.parsed_data
                        best_iteration['run_stages'] = run_stages
                        best_iteration['dataset'] = dataset
                        best_iteration['stages'] = stages

                    app_runs_stages.append(run_stages)

                    if "swift" in config.SCENARIOS.keys()[config.SCENARIOS.values().index(scenario)]:
                        swift_log.append(parse_swift_log(path=os.path.join(ROOT, 'logs'),
                                                         start_timestamp=spark_event.parsed_data["app_start_timestamp"],
                                                         end_timestamp=spark_event.parsed_data["app_end_timestamp"]))
            else:
                dir = file_or_dir
                for ROOT1, SUBDIRS, FILES in os.walk(os.path.join(path, SUBDIR, 'spark_logs', dir)):
                    for filename in FILES:
                        file_ext = os.path.splitext(filename)[-1]
                        if filename == 'stderr':
                            executor_lines = spark_logs_parser.parse_lines(os.path.join(ROOT1, filename))
                            result = spark_logs_parser.extract_http_requests(executor_lines)
                            print("#  Executor: " + str(result))
                            for method in result:
                                total_requests_from_spark += result[method]
                        elif file_ext == '.log':
                            driver_lines = spark_logs_parser.parse_lines(os.path.join(ROOT1, filename))
                            result = spark_logs_parser.extract_http_requests(driver_lines)
                            print("#  Driver: " + str(result))
                            for method in result:
                                total_requests_from_spark += result[method]
        print("#  Total Swift Requests done by Spark: {}".format(total_requests_from_spark))
        print "# -------------------------------------------------"

    if best_iteration['root'] == worst_iteration['root']:
        worst_iteration = None

    dataset_boxplot = {}
    for role in cdfs:
        if role != 'task':
            dataset_boxplot[role] = {
                'CPU': cdfs[role]['s_cpu'],
                'Disk_Busy': cdfs[role]['s_disk_busy'],
                'Disk_Bytes': cdfs[role]['s_disk_byte'],
                'Network': cdfs[role]['s_net'],
            }

    if len(runtimes) > 0:
        if runtimes < 5:
            print("# Warning: less than 5 samples for this measurement")

        stages_stats = []
        for idx in range(len(app_runs_stages[0])):
            tmp = [x[idx]["runtimes"] for x in app_runs_stages]
            tmp = numpy.concatenate(tmp)
            stage_stats = {
                "name": app_runs_stages[0][idx]["name"],
                "task_mean": numpy.mean(tmp) / 1000,
                "task_std": numpy.std(tmp) / 1000
            }
            stages_stats.append(stage_stats)
        runtimes = numpy.array(runtimes)

        aggregate_swift_log = None
        if len(swift_log) != 0:
            # We assume that all iteration trigger the same requests
            # With this assumption we can directly find the average per request
            num_iterations = len(swift_log)
            aggregate_swift_log = {}
            for entry in swift_log:
                for server in entry:
                    if server not in aggregate_swift_log:
                        aggregate_swift_log[server] = {
                            "Request": {}
                        }
                    requests = entry[server]["Request"]
                    aggregate_requests = aggregate_swift_log[server]["Request"]
                    for request in requests:
                        if request not in aggregate_requests:
                            aggregate_requests[request] = {
                                "code": {},
                                "total": 0
                            }
                        codes = requests[request]["code"]
                        aggregate_codes = aggregate_requests[request]["code"]
                        for code in codes:
                            # if code not in aggregate_codes:
                            #     aggregate_codes[code] = 0
                            aggregate_codes[code] = (codes[code] / num_iterations)
                        aggregate_requests[request]["total"] = (requests[request]["total"] / num_iterations)
        return {
            'scenario': scenario,
            'workload': workload,
            'app': {
                'runtime': {
                    'mean': numpy.mean(runtimes) / 1000,
                    'stddev': numpy.std(runtimes) / 1000
                },
                'tasks': {
                    'runtimes': task_runtimes
                },
                'stages': {
                    'stats': stages_stats
                }
            },
            'resource': dataset_boxplot,
            'best_iteration': best_iteration,
            'worst_iteration': worst_iteration,
            'swift': aggregate_swift_log
        }
    else:
        return None


def parse_swift_log(path, start_timestamp, end_timestamp):
    for ROOT, SUBDIRS, FILES in os.walk(path):
        for swift_log_filename in glob.iglob(os.path.join(ROOT, '*.log')):
            with open(swift_log_filename) as swift_log_file:
                result = parse_lines(swift_log_file.readlines(),
                                     start_timestamp=start_timestamp, end_timestamp=end_timestamp)
                print("#  Swift logs: " + str(result))
                total_request_received = 0
                for server in result:
                    for method in result[server]["Request"]:
                        total_request_received += result[server]["Request"][method]["total"]
                print("#  Total Swift Requests Received: {}".format(total_request_received))
                return result


if __name__ == '__main__':
    LOGS_PATH = os.path.normpath(config.LOGS_PATH)
    PLOT_DIR = os.path.join(os.path.normpath(config.PLOT_DIR), os.path.basename(LOGS_PATH))
    OUTPUT_FILE = utils.mkdir_p(os.path.join(PLOT_DIR, 'output.txt'))
    sys.stdout = Logger(OUTPUT_FILE)

    data = {}
    if not config.PLOTS_ONLY:
        for root, subdirs, files in os.walk(LOGS_PATH):
            scenario_alias = os.path.basename(os.path.dirname(root))
            if scenario_alias in config.SCENARIOS:
                scenario = config.SCENARIOS[scenario_alias]
                if scenario not in data:
                    data[scenario] = {}
                workload = os.path.basename(root)
                if workload in config.WORKLOADS:
                    print "# Parsing Workload {} for Scenario {}".format(config.WORKLOADS[workload], scenario_alias)
                    data[scenario][config.WORKLOADS[workload]] = parse_app(root, scenario, workload)
        with open(os.path.join(LOGS_PATH, "parsed_data.dat"), "w") as parsed_data_file:
            parsed_data_file.write(json.dumps(data))

    if len(data) == 0:
        with open(os.path.join(LOGS_PATH, "parsed_data.dat"), "r") as parsed_data_file:
            data = json.load(parsed_data_file)

    if len(data) != 0:
        # Order the Dict so that we have plots ordered
        data_tmp = OrderedDict({})
        for s in sorted(data):
            data_tmp[s] = data[s]
        data = data_tmp

        if config.PLOT_FONT_SIZE is not None:
            matplotlib.rcParams.update({'font.size': config.PLOT_FONT_SIZE})

        aggregate_plot_dir = os.path.join(PLOT_DIR, 'aggregate')
        if config.PLOT_CDF:
            print("# Plotting CDFs...")
            CDFs.tasks_multi_figure(dataset=data, filename=os.path.join(aggregate_plot_dir, 'cdfs'))
        if config.PLOT_DISK_BYTE:
            print("# Plotting BoxPlots for Throughput...")
            BoxPlots.disk_throughput_multi_figure(dataset=data, filename=os.path.join(aggregate_plot_dir, 'boxplots'))

        ranking = {}
        for scenario in data:
            for workload in data[scenario]:
                if workload not in ranking:
                    ranking[workload] = {}
                ranking[workload][scenario] = {
                    'mean': data[scenario][workload]['app']['runtime']['mean'],
                    'stddev': data[scenario][workload]['app']['runtime']['stddev']
                }
                plot_dir = os.path.join(PLOT_DIR, scenario, workload)

                if config.PLOT_BARCHARTS:
                    if data[scenario][workload]['swift'] is not None:
                        BarCharts.swift_requests(plot_title=scenario, dataset=data[scenario][workload]['swift'],
                                                 plot_dir=plot_dir)

                if config.PLOT_BOXPLOTS:
                    print("# Plotting BoxPlots for scenario: {} workload: {} ...".format(scenario, workload))
                    BoxPlots.resource(plot_title=scenario, scenario=scenario, dataset=data[scenario][workload],
                                      plot_dir=os.path.join(plot_dir, 'boxplots'))

                if config.PLOT_TIMESERIES:
                    best_iteration = data[scenario][workload]['best_iteration']
                    worst_iteration = data[scenario][workload]['worst_iteration']

                    print("# Plotting best TimeSeries for scenario: {} workload: {} ...".format(scenario, workload))
                    if best_iteration is not None:
                        generate_time_series(best_iteration['dataset'], best_iteration['stages'],
                                             'best', plot_dir=os.path.join(plot_dir, "time-series"))
                    print("# Plotting worst TimeSeries for scenario: {} workload: {} ...".format(scenario, workload))
                    if worst_iteration is not None:
                        generate_time_series(worst_iteration['dataset'], worst_iteration['stages'],
                                             'worst', plot_dir=os.path.join(plot_dir, "time-series"))

        for workload in ranking:
            print("# Workload {}".format(workload))
            sorted_x = sorted(ranking[workload].iteritems(), key=lambda (x, y): y['mean'])
            best_scenario_runtime = 1
            try:
                best_scenario_runtime = data[config.BEST_SCENARIO][workload][0]
            except KeyError:
                pass

            for scenario in sorted_x:
                norm = ((scenario[1]['mean'] - best_scenario_runtime) / best_scenario_runtime) + 1
                print("-> Scenario {}".format(scenario[0]))
                print(" -> Mean: %.2f" % scenario[1]['mean'])
                print(" -> Stddev: %.2f" % scenario[1]['stddev'])
                # print(" -> Norm: %.2f %%" % norm)

                # print("%s\t&$ %.2f\t\\pm %.2f\t$\t&$ %.2f $\\\\" % (
                #     scenario[0], scenario[1]['mean'], scenario[1]['stddev'], norm))
