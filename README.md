# WHSync
A python script to synchronize Wunderlist -> Habitica

WHSync is a simple python script that synchronizes tasks from Wunderlist to Habitica (one-way sync). It currently supports:

1. Selection of which lists to sync on running the script for the first time. If a new list is added, it is detected and asks you if you want to add it. Currently, there's no way of changing the lists you sync, but this will be fixed. 

2. Syncing Wunderlist tasks and their due dates as Habitica to-dos.

3. Syncing Wunderlist recurring to-dos as Habitica dailies. It only supports repeat every X days and X weeks at the moment. If X is not 1 day it gets a bit finicky. You will have to adjust the start date properly on Habitica itself, but this will be fixed soon.

4. Setting difficulties using tags in Wunderlist. E.g. #M anywhere in the name makes a task "medium" difficulty.

5. Syncing of Wunderlist subtasks as Habitica checklists. If it is complete on first time sync, the check list will be completed on Habitica as well. Currently it won't sync that a subtask has been completed, but this will be added soon.

6. Syncing habitica stats to Wunderlist in a custom list. 

![alt tag](http://i.imgur.com/sHwbIIQ.png)

Two important things to notice:
1. The version of wunderpy2 used is slightly different from the one on pip. You can clone my own fork and install it, this had a bug fix to support python3.
2. The version of habitica (the python library) used is also different. It has been updated to include extra features, can also be cloned and installed from my own fork.

You can run the script as:
`python3 whsync.py`

or to have it run every 30 seconds, for example:
`python3 whsync.py 30`

Note that task names in Habitica are formed by the list name + task name in Wunderlist. For example, if a task is called "Solve assignment 1" in a list "PHYS-401", the resultant Habitica task is "PHYS-401: Solve assignment 1".

The latter puts it in non-interactive mode where it won't check for new lists (and consequently won't ask you if you want to sync them).

I am a pretty lousy programmer and could really use help with this, especially figuring out a way to deploy it on a webserver or as a web app or something, I don't know.
