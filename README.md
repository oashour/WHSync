# WHSync
A python script to synchronize Wunderlist -> Habitica

WHSync is a simple python script that synchronizes tasks from Wunderlist to Habitica (one-way sync). It currently supports:

1. Selection of which lists to sync on running the script for the first time. If a new list is added, it is detected and the asks you if you want to also sync it. Currently, there's no way of changing the lists you sync, but this will be fixed. 

2. Syncing Wunderlist tasks with their due dates as Habitica to-dos.

3. Syncing Wunderlist recurring to-dos as Habitica dailies. It only supports repeat every X days and X weeks at the moment (not monthly/yearly). If a new daily is added, the start date on Habitica is the first due date on Wunderlist.

4. Setting difficulties using tags in Wunderlist. E.g. #M anywhere in the name makes a task "medium" difficulty.

5. Syncing of Wunderlist subtasks as Habitica checklists. This includes adding, completing and deleting checks.

6. Syncing habitica stats to Wunderlist in a custom list. Top item shows the last synchronization time.

![alt tag](http://i.imgur.com/rc5CLNY.png)

Two important things to notice:

1. The version of wunderpy2 used is slightly different from the one on pip. You can clone my own fork and install it, this had a bug fix to support python3.

2. The version of habitica (the python library) used is also different. It has been updated to include extra features, can also be cloned and installed from my own fork.

You can run the script as:
`python3 whsync.py`

or to have it run every 30 seconds, for example:
`python3 whsync.py 30`

The latter puts it in non-interactive mode where it won't check for new lists (and consequently won't ask you if you want to sync them).

Currently the best way to use the script is to deploy is to run it on a remote shell such as xshellz.com. You will need to clone this repo and my forks of wunderpy2 and habitica, install the latter two in a virtual env and then run the script as:
`nohhup python3 -u whsync.py 30 &`
Afterwards you can just `exit` the shell and it will keep running. 

Note that task names in Habitica are formed by the list name + task name in Wunderlist. For example, if a task is called "Solve assignment 1" in a list "PHYS-401", the resultant Habitica task is "PHYS-401: Solve assignment 1".

I am a pretty lousy programmer and could really use help with this, especially figuring out a way to deploy it on a webserver or as a web app or something, I don't know.
