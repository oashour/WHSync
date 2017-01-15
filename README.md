# WHSync

### A python script to synchronize Wunderlist -> Habitica

WHSync is a simple python script that synchronizes tasks from Wunderlist to Habitica (one-way sync). It currently supports:

## Features:
1. Selection of which lists to sync on running the script for the first time. If a new list is added, it is detected and the asks you if you want to also sync it. Currently, there's no way of changing the lists you sync, but this will be fixed. 

2. Syncing Wunderlist tasks with their due dates as Habitica to-dos.

3. Syncing Wunderlist recurring to-dos as Habitica dailies. It only supports repeat every X days and X weeks at the moment (not monthly/yearly). If a new daily is added, the start date on Habitica is the first due date on Wunderlist.

4. Setting difficulties using tags in Wunderlist. E.g. #M anywhere in the name makes a task "medium" difficulty.

5. Syncing of Wunderlist subtasks as Habitica checklists. This includes adding, completing and deleting checks.

6. Syncing habitica stats to Wunderlist in a custom list. Top item shows the last synchronization time.
  <p align="center">
  <img src="http://i.imgur.com/rc5CLNY.png"/>
  </p>

7. Task names in Habitica are formed by the list name + task name in Wunderlist. For example, if a task is called "Solve assignment 1" in a list "PHYS-401", the resultant Habitica task is "PHYS-401: Solve assignment 1".

## Notes on dependencies:

1. The version of wunderpy2 used is slightly different from the one on pip. I sent in a pull request, it will hopefully be merged some time soon.

2. The version of habitica CLI used is also different. WHSync relies on a modified version of their API wrapper, I will clean up the code and send in a pull request eventually.

## Getting the script up and running

1. Clone and install my fork of wunderpy2. This fixes some python3 related bugs.

  ```
  $ git clone https://github.com/oashour/wunderpy2.git
  $ cd wunderpy2
  $ sudo python3 setup.py install
  ```
  
2. Clone and install my fork of habitica. This adds functionality to their API wrapper.

  ```
  $ git clone https://github.com/oashour/habitica.git`
  $ cd habitica
  $ sudo python3 setup.py install
  ```

3. Go to http://developer.wunderlist.com and register an app. Give it whatever name and callback URLs you want since this won't really be used with OAuth2 until I implement that. Click generate an access token and save that and your clientID. Your access token is a password, don't put it anywhere public.

4. Go to https://habitica.com/#/options/settings/api, save your User ID and API Token.

5. Clone this repo:

  ```
  $ git clone https://github.com/oashour/WHSync.git
  ```

6. Inside the repo, you'll find the `auth.cfg.sample` file.  Modify it as follows:
  * `url`: leave this as is. (to ensure compatibility with the original habitica CLI)
  * `login`: your habitica user ID retrieved in step 4.
  * `password`: your habitica API token retrieved in step 4.
  * `checklists`: keep it as is.
  * `access_token`: Wunderlist access token retrieved in step 3.
  * `client_id`: Wunderlist client ID retrieved in step 3.
  * `time_zone`: how many hours you are ahead of or before UTC. For example, UTC-6 you'd enter `time_zone = -6`

7. Rename the sample file to `auth.cfg` and move it to `~/.config/whsync`. Assuming the directories exist:

  ```
  $ mv auth.cfg.sample ~/.config/whsync/auth.cfg
  ```

8. Run the script once as:
  ```
  $ python3 whsync.py
  ```
  
9. Follow the prompts. It will mainly ask you which lists you want to synchronize. You can enter:
  * Single lists, e.g.: `5 8 12`
  * All lists: `all`
  * Ranges: `1 9 10:15`
  * All except: `all except 1 6 22:30`

10. Run the script in continuous mode. It won't check if new lists have been added in this mode. To have it run every 30 seconds:

  ```
  $ python3 whsync.py 30
  ```

11. To run the script in the background even after you close the shell:

  ```
  $ nohhup python3 -u whsync.py 30 &
  ```
  
Currently the best way to use the script is to deploy is to run it on a remote shell such as `xshellz.com` or your own server. Note that you will get banned from the free tier of xshellz if you run this continuously, it takes around double the resource limit of free acounts (which is tiny).

I am a pretty lousy programmer and could really use help with this, especially figuring out a way to deploy it on a webserver or as a web app or something similar.
