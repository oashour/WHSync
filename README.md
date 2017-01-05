# WHSync
A python script to synchronize Wunderlist -> Habitica

WHSync is a simple python script that synchronizes tasks from Wunderlist to Habitica (one-way sync). It currently supports:

1. Syncing to-dos 

2. Syncing recurring to-dos as dailies

3. Setting difficulties using tags in Wunderlist. E.g. #M anywhere in the name makes a task "medium" difficulty.

Note that task names in Habitica are formed by the list name + task name in Wunderlist. For example, if a task is called "Solve assignment 1" in a list "PHYS-401", the resultant Habitica task is "PHYS-401: Solve assignment 1".

The best option for using this script is to run it every X minutes on a webserver. It currently requires registering your own Wunderlist app until I get authentication working.

Note that this script is very early in development and is full of bugs and unhandled exceptions. I could use collaborators on this.
