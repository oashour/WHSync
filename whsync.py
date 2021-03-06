from habitica import api as habiticaAPI
import wunderpy2
import whlib
import sys
import os
from time import sleep
from datetime import datetime, timedelta 

AUTH_CONF = os.path.expanduser('~') + '/.config/whsync/auth.cfg'

def main(nonInt):
    # Load Configuration
    auth = whlib.loadAuth(AUTH_CONF)
    now = datetime.utcnow() + timedelta(hours=int(auth['time_zone']))
    print('Welcome to WHSync. Current time:'+now.strftime('%I:%M %p %Y-%m-%d '))
    
    print('Connecting to APIs.')
    # Connect to Habitica
    try:
        hbt = habiticaAPI.Habitica(auth=auth)   # instantiate api service
    except:
        print('Unable to connect to Habitica.')
        exit(1)

    # Connect to Wunderlist
    api = wunderpy2.WunderApi()	
    try:
        client = api.get_client(auth['access_token'], auth['client_id'])
    except:
        print("Can't connect to Wunderlist.")
        exit(1)
    
    if nonInt:
        lists = client.get_lists() # Get lists
        print("Program run in non-interactive mode. Won't check new lists.")
    else:
        lists = whlib.getNewLists(client)     
    
    print('Fetching Wunderlist and Habitica tasks.')
    wlTasks = whlib.getWLTasks(client);
    hbtTodos = hbt.user.tasks(type='todos')
    hbtDailys = hbt.user.tasks(type='dailys')
    
    print('Determining what tasks to add, delete or complete.')
    syncTasks = whlib.getHbtTasks(wlTasks, (hbtDailys, hbtTodos), client, hbt)
    print('Synchronizing tasks.')
    whlib.printSync(syncTasks)
    whlib.sync(hbt, syncTasks) 
    
    print('Synchronizing subtasks.')
    whlib.syncSubs(wlTasks, (hbtDailys, hbtTodos), client, hbt)

    print('Pushing Habitica stats to Wunderlist.')
    user = whlib.updateStats(hbt, client, lists, auth['time_zone'])
    
    return syncTasks+ (user,)
    
if __name__ == '__main__':
    if len(sys.argv) == 1:
        nonInt = False
        main(nonInt)
    elif len(sys.argv) == 2:
        while True:
            try:
                nonInt = True
                main(nonInt)
                print('==================================')
                sleep(int(sys.argv[1]))           
            except:
                print('Something failed. Sleeping again.')
                sleep(int(sys.argv[1]))
    
