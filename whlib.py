import os 
from time import sleep

try:
    import ConfigParser as configparser
except:
    import configparser

SYNC_LIST = os.path.expanduser('~') + '/.config/whsync/syncId.txt'
LIST_CACHE = os.path.expanduser('~') + '/.config/whsync/listCache.txt'
 
def updateStats(hbt, client, lists):
    user = hbt.user()
    stats = user['stats']
    level = 'Level '+str(stats['lvl'])
    exp = ' \U0001F31F '+str(stats['exp'])+'/'+str(stats['toNextLevel'])
    hp = '\U00002764 '+str(round(stats['hp']))+'/'+str(stats['maxHealth'])
    mp = ' \U0001F52E '+str(round(stats['mp']))+'/'+str(stats['maxMP'])
    gold = int(stats['gp'])
    silver = int((stats['gp'] - int(gold))*100)
    gems = user['balance']

    gp = u'\U0001F48E %s \U0001F534 %s \U000026AA %s' % (str(gems), 
                                                         str(gold),
                                                         str(silver))

    firstTime = 1
    for list in lists:
        if list['title'] == 'Habitica '+u'\U00002694':
            firstTime = 0
            lid = list['id']
            break
     
    if not firstTime:
        tasks = client.get_tasks(lid)
        for task in tasks:
            if task['title'].split()[0] == 'Level':
                rev = task['revision']
                tid=task['id']
                client.update_task(task_id=tid,revision=rev,title=level+exp)
            elif task['title'].split()[0] == u'\U0001F48E':
                rev = task['revision']
                tid=task['id']
                client.update_task(task_id=tid,revision=rev,title=gp)
            elif task['title'].split()[0] == u'\U00002764':
                rev = task['revision']
                tid=task['id']
                client.update_task(task_id=tid,revision=rev,title=hp+mp) 
    elif firstTime:
        print("Stats don't exist. Creating list and tasks.")
        lid = client.create_list(title='Habitica '+u'\U00002694')['id']
        client.create_task(list_id=lid,title=level+exp)
        client.create_task(list_id=lid,title=hp+mp)
        client.create_task(list_id=lid,title=gp)
        
    return user

def getNewLists(client):
    """ Get all the new Wunderlist lists not in cache and refresh cache
    
    Keyword Arguments:
    client: wunderlist client object
    """
    print('Fetching all Wunderlist lists.')  
    lists = client.get_lists() # Get lists
    listsList = [l['id'] for l in lists]
    try:
        with open(LIST_CACHE) as f:
            listsCache = f.readlines()
            listsCache = [str.strip('\n') for str in listsCache]
    except IOError:
        listsCache = []
        try:
            os.remove(SYNC_LIST) # In case it's still there delete it too
        except:
            pass
               
    new = [l for l in lists if str(l['id']) not in listsCache]
    
    if not new:
        print('No new lists found.')
    else:
        print('New Uncached lists found:')
        print('--------------------------')
        for l in new:
            print(lists.index(l)+1, l['title'])
        # Get ID of lists user wants to sync
        if not listsCache: # no lists in cache, first time setup
            print('First time setup. Please follow prompts.')
        getSyncLists(lists)
    
    # If cache is empty then this is the 'first' time running the programs 
    if new: # And new lists exist, only now do we need to print a cache file
        allListsFile = open(LIST_CACHE, 'w')  
        for l in lists:
            allListsFile.write("%s\n" % l['id'])
        allListsFile.close() 

    return lists

def getSyncLists(lists):
    """ Get the IDs of the lists the user wants to sync
    
    Keyword Arguments:
    lists: a list of dictionaries returned by the Wunderlist API.
    """
    # Attempt to get the numbers of the lists to sync from user
    while True:
        try:
            listId = input('Input the number of lists you need: ').split()
            if not listId:
                raise ValueError('No input. Please try again. q to exit.')
            elif listId[0] == 'q':
                print('No lists to sync.')
                return
            break
        except ValueError as e:
            print(e)
    
    # Expand ranges entered by user, e.g. 5:8 -> [5, 6, 7, 8] 
    strExp=[]
    i = 0
    while i < len(listId):
        string = listId[i]
        if ':' not in string:
            i += 1
            continue
        else:
            a = string.split(':') # Find start and end of range
            b = range(int(a[0]), int(a[1])+1) # List of integers in the range
            listId.remove(string) # Remove that specific range
            strExp.extend(list(map(str, b))) # Convert to string
    listId.extend(strExp) # Extend the original list    
    
    # See if keyword 'all' and 'except' are used
    if listId[0] == 'all':
        a = list(range(0, len(lists))) # All lists
        b = list(map(int, listId[2:])) # Ones to exclude
        listId = [x for x in a if x not in b] # Remove excludes
    else:
        listId = list(map(int, listId))
    listId = list(set(listId)) # Remove duplicates
    listId = [k for k in listId if k <= len(lists)] # Remove incorrect ones
    listId = [k-1 for k in listId] # Change to 0 indexing
    
    print('Lists chosen for synchronization:')
    for id in listId:
        print(lists[id]['title'])
    
    # Extract actual IDs based on number
    listId = [lists[id]['id'] for id in listId]
    
    # Print IDs to file for future extraction
    syncListFile = open(SYNC_LIST, 'a') 
    for item in listId:
        syncListFile.write("%s\n" % item)
    syncListFile.close() 
    
    return listId

def sync(hbt, syncTasks):
    """ Function to do the synchronization from Wunderlist to Habitica
    
    Keyword Arguments:
    hbt: Habitica API structure (?)
    syncTasks: a tuple of tasks (dailys and todos) that will be changed.
    """
    
    todosC = syncTasks[0]; todosA = syncTasks[1];
    dailysD = syncTasks[2]; dailysA = syncTasks[3]; dailysC = syncTasks[4];
    # Add tasks. Simply add them by name
    for task in todosA:
        diff = calcDiff(task['title'])
        if 'due_date' in task:
            newTask = hbt.user.tasks(type='todo', text=task['title'], 
                                    date = task['due_date'],
                                    priority=diff, _method='post')
        else:
            newTask = hbt.user.tasks(type='todo', text=task['title'],
                            priority=diff, _method='post')
        for sub in task['subs']:
            newTask = hbt.checklist.tasks(_id=newTask['id'], text=sub['title'], _method='post')
            if sub['completed']:
                cid = newTask['checklist'][-1]['id'] # Last added is last in list
                hbt.checklist.tasks(_id=newTask['id'], _id2=cid, _method='post') # score
        
        print('Added task "', task['title'], '" to Habitica.',sep='')
    
    # Complete tasks, find the hid of this task and mark it as complete.
    for task in todosC:
        hbt.user.tasks(_id=task['id'], _direction='up', _method='post')
        print('Completed task "', task['text'], '" on Habitica.',sep='')   

    # Add dailys. Simply add them by name
    for task in dailysA:
        diff = calcDiff(task['title'])
        newTask = hbt.user.tasks(type='daily', text=task['title'], notes=task['id'], 
                       priority=diff, everyX=task['recurrence_count'], _method='post')
        for sub in task['subs']:
            newTask = hbt.checklist.tasks(_id=newTask['id'], text=sub['title'], _method='post')
            if sub['completed']:
                cid = newTask['checklist'][-1]['id'] # Last added is last in list
                hbt.checklist.tasks(_id=newTask['id'], _id2=cid, _method='post') # score 
        print('Added daily "', task['title'], '" to Habitica.', sep='')
 
    # Delete dailys, find the hid of this task and mark it as complete.
    for task in dailysD:
        hbt.user.tasks(_id=task['_id'], _method='delete')
        print('Deleted daily "', task['text'], '" from Habitica.', sep='')   
    
    # Completing dailies involves setting them to complete THEN 
    # Changing the note of the daily to the Wunderlist ID of the
    # Next day's iteration
    for task in dailysC:
        hbt.user.tasks(_id=task['id'],
                               _direction='up', _method='post')
        hbt.user.tasks(_id=task['id'],notes=task['notes'], _method='put')
        print('Completed daily "', task['text'], '" on Habitica.', sep='')

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

def getHbtTasks(wlTasks, hbtTasks, client):
    # Work on Todos (second element in each tuple)
    x = hbtTasks[1]; y = wlTasks[1]    
    todosC = [item for item in x
                       if item['text'] not in [d['title'] for d in y]]
    todosA = [item for item in y
                  if item['title'] not in [d['text'] for d in x]]
    for item in todosA:
        item['subs'] = client.get_task_subtasks(item['id'], completed=True)
    #for task in todosA: # In case time zones are needed
    #    date = datetime.strptime(task['due_date'],'%Y-%m-%d') # Strip formatting
    #    zone = 2 # How to determine automatically?
    #    date = date - timedelta(days=1, hour=-zone)
    #    date = datetime.strftime(date, '%Y-%m-%dT%H:00:00.000Z')
    #    task['due_date'] = date
    
    # Work on Dailies
    x = hbtTasks[0]; y = wlTasks[0];
    # Dailys in Habitica but not in WL are to be deleted
    dailysD = [item for item in x
                   if item['text'] not in [d['title'] for d in y]]
    # Dailys in WL but not in Habitica are to be added
    dailysA = [item for item in y
                  if item['title'] not in [d['text'] for d in x]]
    for item in dailysA:
        item['subs'] = client.get_task_subtasks(item['id'], completed=True)
        
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
    
    for id in syncId: # This significantly slows down the program
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

def loadAuth(configfile):
    """Get authentication data from the AUTH_CONF file."""

    print('Loading habitica and Wunderlist auth data from "%s"' % configfile)

    try:
        cf = open(configfile)
    except IOError:
        print("Unable to find '%s'." % configfile)
        exit(1)

    config = configparser.SafeConfigParser()
    config.readfp(cf)

    cf.close()

    # Get data from config
    rv = {}
    try:
        rv = {'x-api-user': config.get('Habitica', 'login'),
              'x-api-key': config.get('Habitica', 'password'),
              'url': config.get('Habitica', 'url'),
              'checklists': config.get('Habitica', 'checklists'),
              'client_id': config.get('Wunderlist', 'client_id'),
              'access_token': config.get('Wunderlist', 'access_token')}

    except configparser.NoSectionError as e:
        print("Missing section in auth file '%s': %s"
                  % (configfile, e.message))
        exit(1)            
    except configparser.NoOptionError as e:
        print("Missing option in auth file '%s': %s"
                      % (configfile, e.message))
        exit(1)
        
    # Return auth data as a dictionnary
    return rv  
    
    
def calcDiff(task):
    diffKeys = ['T', 'E', 'M', 'H']
    tags = [task.strip("#") for task in task.split() 
                if task.startswith("#")]
    match = next((x for x in tags if x in diffKeys), False)
    
    diff = 1
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