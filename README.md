Technical assignment for Veeam.

Requires python3

Main function of script is distriputed into two threads.
* 1. User input thread: Constant loop which checks for user input. Command are described at the start of the script or can be accesed with -h or help.
  2. Sync thread: periodicaly calculates and compares md5 hashes of files in source and replica folder. Adjusts replica based on source and logs the actions.
