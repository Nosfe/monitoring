Log Parser
==========

This tool parse the logs generated with the Monitoring Daemon for applications that uses Spark framework.
The configuration file is `log_parser/config.py` and contains all the variables that are used during the parsing.


Structure of logs folder
------------------------

The logs folder must be in the following structure:
 
     <base>
     |_<scenario_0>
       |_<workload_0>
         |_logs
           |_<iteration_0>
             |_<hostname>
               |_<monitoring daemon logs files>


Plots Supported
---------------

The plots that are currently supported are:

1. Time Series
    - CPU
        - Utilization
    - DISK
        -   Await time
        -  Throughput
        - Utilization
    - NET
        - Utilization
    - MEMORY
        - Utilization   
2. BoxPlots
    - Utilization (CPU-DISK-NET-MEMORY)
    - DISK Throughput
3. CDF
    - Tasks run time
    

    