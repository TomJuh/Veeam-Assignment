Technical assignment for Veeam.

## Requires python3
Usage python3 Sync.py -[choosenFlag] [choosenValue]...

To display help message  run the program with flag -h

All variables must be set for program to run:
* Set interval with -i [interval in seconds]
* Set source folder path with -sf [path to source folder]
* Set replica folder path -rf [path to replica folder]
* Set log file path -lf [path to log file]
 ### Example command: 
 * ### python3 Sync.py -i 30 -sf /home/veeam/source -rf /home/veeam/replica -lf /home/veaam/log.txt
# Application can be exited only with keyboard interrupt! - CTRL+C
# Folders must exist!

