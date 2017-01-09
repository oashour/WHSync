import api as habiticaAPI
import wunderpy2
import whlib
import sys
from time import sleep

AUTH_CONF = 'auth.txt'
WL_AUTH = 'wlAuth.txt'

def main(nonInt):
    print('Welcome to WHSync, a sync utility for Habitica and Wunderlist.')
    print('Connecting to APIs.')
    # Set up Habitica
    auth = habiticaAPI.load_auth(AUTH_CONF) # Set up auth
    hbt = habiticaAPI.Habitica(auth=auth)   # instantiate api service

    # Set up Wunderlist
    # instantiate API servicd
    api = wunderpy2.WunderApi()	
    auth = whlib.getWLAuth()
    client = api.get_client(auth['accessToken'], auth['clientId'])
    
    if nonInt:
        print("Program run in non-interactive mode. Won't fetch lists.")
    else:
        lists = whlib.getNewLists(client)     
    
    print('Fetching Wunderlist and Habitica tasks.')
    wlTasks = whlib.getWLTasks(client);
    hbtTodos = hbt.user.tasks(type='todos')
    hbtDailys = hbt.user.tasks(type='dailys')
    
    print('Determining what tasks to add, delete or complete.')
    syncTasks = whlib.getHbtTasks(wlTasks, (hbtDailys, hbtTodos), client)
    whlib.printSync(syncTasks)
    whlib.sync(hbt, syncTasks) 

    print('Pushing Habitica stats to Wunderlist.')
    whlib.updateStats(hbt, client, lists)
    
# 6 30 41 44 46 47 48 49 50 51
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
                sleep(int(sys.argv[1]))
    
