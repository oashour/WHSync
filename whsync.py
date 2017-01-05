import wunderpy2
import os 
import api as habiticaAPI
from time import sleep

AUTH_CONF = 'auth.txt'
WL_AUTH = 'wlAuth.txt'
SYNC_LIST = 'syncList.txt'
HABITICA_REQUEST_WAIT_TIME = 0.5  # time to pause between concurrent requests

def sync(hbt, syncTasks):
    todosC = syncTasks[0]; todosA = syncTasks[1];
    dailysD = syncTasks[2]; dailysA = syncTasks[3]; dailysC = syncTasks[4];
    # Add tasks. Simply add them by name
    for task in todosA:
        diff = calcDiff(task['title'])
        hbt.user.tasks(type='todo', text=task['title'], priority=diff, _method='post')
        print('Added task"', task['title'], '" to Habitica.')
    
    # Complete tasks, find the hid of this task and mark it as complete.
    for task in todosC:
        hbt.user.tasks(_id=task['id'], _direction='up', _method='post')
        print('Completed task"', task['text'], '" on Habitica.')   

    # Add dailys. Simply add them by name
    for task in dailysA:
        diff = calcDiff(task['title'])
        hbt.user.tasks(type='daily', text=task['title'], notes=task['id'], 
                       priority=diff, everyX=task['recurrence_count'], _method='post')
        print('Added daily"', task['title'], '" to Habitica.')
 
    # Delete dailys, find the hid of this task and mark it as complete.
    for task in dailysD:
        hbt.user.tasks(_id=task['_id'], _method='delete')
        print('Deleted daily"', task['text'], '" from Habitica.')   
    
    # Completing dailies involves setting them to complete THEN 
    # Changing the note of the daily to the Wunderlist ID of the
    # Next day's iteration
    for task in dailysC:
        hbt.user.tasks(_id=task['id'],
                               _direction='up', _method='post')
        hbt.user.tasks(_id=task['id'],notes=task['notes'], _method='put')
        print('Completed daily"', task['text'], '"on Habitica.')



def printSync(syncTasks):
    todosC = syncTasks[0]; todosA = syncTasks[1];
    dailysD = syncTasks[2]; dailysA = syncTasks[3]; dailysC = syncTasks[4];
    
    print('------------------')
    print('Tasks to Complete:\n', '\n'.join([d['text'] for d \
                                in todosC if 'text' in d]))
    print('------------------')
    print('Tasks to Add:\n', '\n'.join([d['title'] for d \
                                in todosA if 'title' in d]))
    print('------------------')
    print('Dailys to Delete:\n', '\n'.join([d['text'] for d \
                                in dailysD if 'text' in d]))
    print('------------------')
    print('Dailys to Add:\n', '\n'.join([d['title'] for d \
                                in dailysA if 'title' in d]))
    print('------------------')
    print('Dailies to Complete:\n', '\n'.join([d['text'] for d \
                                in dailysC if 'text' in d]))
    print('------------------')

def getHbtTasks(wlTasks, hbtTasks):
    # Work on Todos
    x = hbtTasks[1]; y = wlTasks[1]    
    todosC = [item for item in x
                       if item['text'] not in [d['title'] for d in y]]
    todosA = [item for item in y
                  if item['title'] not in [d['text'] for d in x]]
    
    # Work on Dailies
    x = hbtTasks[0]; y = wlTasks[0];
    # Dailys in Habitica but not in WL are to be deleted
    dailysD = [item for item in x
                   if item['text'] not in [d['title'] for d in y]]
    # Dailys in WL but not in Habitica are to be added
    dailysA = [item for item in y
                  if item['title'] not in [d['text'] for d in x]]
    
    # Dailies in both but whose note is different from the WL ID
    # are to be completed. Then change their note to the new WL ID.
    dailysC = []
    for hT in x:
        for wlT in y:
            if (hT['text'] == wlT['title'] and hT['notes'] != str(wlT['id'])):
                hT['notes'] = wlT['id']
                dailysC.append(hT)
                break
    
    return (todosC, todosA, dailysD, dailysA, dailysC)
       
def getWLTasks(client):
    # Fetch IDs of lists to sync
    with open(SYNC_LIST) as f:
        syncId = f.readlines()
    syncId = map(str.strip, syncId) # Strip new line characters
    
    # Fetch all active tasks from these lists
    # Append list name and create huge task list
    tasks = [] # List of wl tasks
    todos = [] 
    dailys = [] # List of wl dailies
    key = 'recurrence_type'; cKey = 'recurrence_count'
    
    for id in syncId:
        tasks.extend(client.get_tasks(id))
        
    for task in tasks:       
        task['title'] = client.get_list(task['list_id'])['title']+': '+task['title']       
        if key in task:
            if task[key] == 'week':
                task[cKey] = task[cKey]*7    
            # Task has daily recurrence with count 1 = every day
            dailys.append(task) # Add it to daily list
        else: # else, to do list 
            todos.append(task)
    
    return (dailys, todos)

def getWLAuth():
    with open(WL_AUTH) as f:
        strings = f.readlines()
    text = [str.split(':')[1].strip() for str in strings]
    keys = {'accessToken': text[0], 'clientId': text[1], 'clientSecret': text[2]}
    return keys 

def calcDiff(task):
    diffKeys = ['T', 'E', 'M', 'H']
    tags = [task.strip("#") for task in task.split() 
                if task.startswith("#")]
    match = next((x for x in tags if x in diffKeys), False)
    
    diff = 0.1
    if match:
        diff = diffParse([match])
        
    return diff

def diffParse(diff):
    for k in diff:
        if k == 'T':
            return 0.1
        elif k == 'E':
            return 1
        elif k == 'M':
            return 1.5
        elif k == 'H':
            return 2
        else:
            print('Error. ', k, ' undefined')
            return

def cli():
    print('Welcome to WHSync, a sync utility for Habitica and Wunderlist.')
    print('Connecting to APIs.')
    # Set up Habitica
    auth = habiticaAPI.load_auth(AUTH_CONF) # Set up auth
    hbt = habiticaAPI.Habitica(auth=auth)   # instantiate api service
    
    # Set up Wunderlist
    # instantiate API servicd
    api = wunderpy2.WunderApi()	
    auth = getWLAuth()
    client = api.get_client(auth['accessToken'], auth['clientId'])

    # Some file names
    allListFN = 'allList.txt' # plain text list of all Wunderlists
    
    print('Fetching all Wunderlist lists.')
    # Get all lists
    lists = client.get_lists() # Get lists
    listsList = ''
    for i in range(0, len(lists)):
         listsList = listsList + '\n' + str(i) + ' ' + lists[i]['title']   
         
    # Check if file with list IDs to sync exists
    if os.path.isfile(SYNC_LIST): # File exists, proceed as usual
        # Print list to temp file for futurediffing
        # This stupid mechanism can be fixed
        tempF = open('temp.txt', 'w')  
        tempF.write("%s\n" % listsList)
        tempF.close()
        with open(allListFN) as f:
            listsListOld = f.readlines()
        with open('temp.txt') as f:
            listsListCurrent = f.readlines()   
        new = list(set(listsListCurrent) - set(listsListOld))
        
        newId=[]
        if new:
            for txt in new:
                newId.append(txt.split()[0])
            print(len(newId), 'new lists found:')
            for i in range(0,len(new)):
                print(new[i])
            listId = input('Please enter numbers of the new lists you want to sync:')
            listId = listId.split()
            listId = list(map(int,listId))
            # Should add exceptions here for invalid numbers
            
            # Obtain list of IDs to sync
            syncListId = []
            for i in listId:
                syncListId.append(lists[i]['id'])
            
            # Print IDs to file
            syncListFile = open(SYNC_LIST, 'a') # Append to file  
            for item in syncListId:
                syncListFile.write("%s\n" % item)
            syncListFile.close()  

            # Now overwrite the old allList.txt with the new one
            os.rename('temp.txt', 'allList.txt')
        else:
            print('No new lists added since last launch. Fetching tasks.')
            os.remove('temp.txt')
    else:
        # File doesn't exist, run configuration
        print('Running first time setup. Lists in your account: ')
        print(listsList) # Print names to user
        listId = input('Input the number of lists you need, spaces in between: ')
        listId = listId.split()
        listId = list(map(int, listId)) # convert list numbers to list of integers
        # These IDs should be checked for validity
        
        # Print all lists to a file for future diffing
        allListsFile = open('allList.txt', 'w')  
        allListsFile.write("%s\n" % listsList)
        allListsFile.close()
        
        # Obtain list of IDs to sync
        syncListId = []
        for i in listId:
            syncListId.append(lists[i]['id'])
        
        # Print IDs to file
        syncListFile = open(syncListFN, 'w')  
        for item in syncListId:
            syncListFile.write("%s\n" % item)
        syncListFile.close()       
    
    wlTasks = getWLTasks(client);
    hbtTodos = hbt.user.tasks(type='todos')
    hbtDailys = hbt.user.tasks(type='dailys')
    
    syncTasks = getHbtTasks(wlTasks, (hbtDailys, hbtTodos))
    printSync(syncTasks)
    sync(hbt, syncTasks)                  
    
# 6 30 44 46 47 48 49 50 51
if __name__ == '__main__':
    cli()
    