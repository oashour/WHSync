import api as habiticaAPI
import wunderpy2
import whlib
import sys
from time import sleep
sys.stdout.flush() # Flush stdout

AUTH_CONF = 'auth.txt'
WL_AUTH = 'wlAuth.txt'

def main():
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
    
    noPrompt = 0
    
    print('Fetching all Wunderlist lists.')  
    lists = client.get_lists() # Get lists
 
    newLists = whlib.getNewLists(lists)
    
    if not newLists:
        print('No new lists found.')
    else:
        print('New Uncached lists found:')
        print('--------------------------')
        for list in newLists:
            print(list)
        # Get ID of lists user wants to sync
        if noPrompt:
            print("No prompt option selected. Won't add new lists.")
        else:
            listId = whlib.getSyncLists(lists) 
    
    print('Fetching Wunderlist and Habitica tasks.')
    wlTasks = whlib.getWLTasks(client);
    hbtTodos = hbt.user.tasks(type='todos')
    hbtDailys = hbt.user.tasks(type='dailys')
    
    print('Determining what tasks to add, delete or complete.')
    syncTasks = whlib.getHbtTasks(wlTasks, (hbtDailys, hbtTodos))
    whlib.printSync(syncTasks)
    whlib.sync(hbt, syncTasks)                  
    
# 6 30 41 44 46 47 48 49 50 51
if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    elif len(sys.argv) == 2:
        while True:
            try:
                main()
                print('==================================')
                sleep(int(sys.argv[1]))           
            except:
                sleep(int(sys.argv[1]))
    
