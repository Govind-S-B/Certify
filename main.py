from pymongo import MongoClient
import curses
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client.certify

def init(stdscr):
    curses.curs_set(False)
    stdscr.keypad(True)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE) # highlight
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # selectable fields
    main_screen(stdscr)

def main_screen(win): # View Events

    selected_row_idx = 0 # initially select index

    events_list = list(db.events.find({},{"_id":1,"name":1,"issueDt":1}))

    while True:

        win.clear()
        x , y = 0,0
        win.addstr(y,x,"======= Certify CLI v1.0 =======", curses.color_pair(1))
        y+=1
        win.addstr(y, x,"Register New Event [+] | Quit [q]",curses.color_pair(1))
        y+=2

        if events_list == []:
            win.addstr(y,x,"No events registered")
            y+=1
        else:
            for idx, item in enumerate(events_list):
                if idx == selected_row_idx:
                    win.addstr(y, x, f"{item['_id']} {item['name']}", curses.color_pair(2))
                else:
                    if item["issueDt"] == None: # check finalized
                        win.addstr(y, x, f"{item['_id']} {item['name']}", curses.color_pair(3))
                    else:
                        win.addstr(y, x, f"{item['_id']} {item['name']}")
                y += 1

        key = win.getch()
        if key == 81 or key == 113: # Quit
            break
        elif key == 43: # Register
            reg_event(win)
            events_list = list(db.events.find({},{"_id":1,"name":1,"issueDt":1}))
        elif key == curses.KEY_UP and selected_row_idx > 0:
            selected_row_idx -= 1
        elif key == curses.KEY_DOWN and selected_row_idx < len(events_list)-1:
            selected_row_idx += 1
        elif key in [curses.KEY_ENTER, 10, 13]: # View Event
            view_event(win,events_list[selected_row_idx]["_id"])
            events_list = list(db.events.find({},{"_id":1,"name":1,"issueDt":1}))

def reg_event(win):
    curses.curs_set(True)
    curses.echo()
    win.clear()
    x,y = 0,0

    item = {"name":None,"desc":None,"issueDt":None,"fields":[]}

    win.addstr(y,x,"Event Name : ",curses.color_pair(1))
    item["name"] = win.getstr().decode("utf-8") 
    y+=1
    win.addstr(y,x,"Description : ",curses.color_pair(1))
    item["desc"] = win.getstr().decode("utf-8")
    y+=1

    win.addstr(y,x,"Fields : ",curses.color_pair(1))
    item["fields"].extend(win.getstr().decode("utf-8").split())
    y+=1

    db.events.insert_one(item)

    curses.noecho()
    curses.curs_set(False)

def view_event(win, event_id):
    # View Event Details with edit functionality 
    # Show Participant List option below

    db_result = db.events.find_one({"_id":event_id})
    
    selected_index = 0

    # Field_Content , Selectable or Not , field name (used for editing and updating)
    menu_items = [  [f"ID : {db_result['_id']}", False],
                    [f"Event Name : {db_result['name']}", True, 'name'],
                    [f"Description : {db_result['desc']}", True, 'desc'],
                    [f"Issue Date : {db_result['issueDt']}", False],
                    [f"Participant Fields : {db_result['fields']}", True, 'fields'],]
    
    finalized = False if (db_result['issueDt'] == None) else True
    
    while True:
        win.clear()
        x,y = 0,0

        if not finalized:
            win.addstr(y, x, f"[MODIFIABLE] [F to Finalize]", curses.color_pair(1))
            y+=2

            for idx, item in enumerate(menu_items):
                if idx == selected_index  :
                    win.addstr(y, x, item[0], curses.color_pair(2))
                else:
                    if item[1]: # check if editable field
                        win.addstr(y, x, item[0], curses.color_pair(3))
                    else:
                        win.addstr(y, x, item[0])
                y += 1
            y+=1
        else:
            win.addstr(y, x, f"[FINALIZED]", curses.color_pair(1))
            y+=2

            for item in menu_items:
                win.addstr(y, x, item[0])
                y += 1
            y+=1

        win.addstr(y,x,f"Show Participants [S]", curses.color_pair(3))
        y+=1

        key = win.getch()

        if key == 81 or key == 113: # Quit
            break
        elif key == 70 or key == 102: # Finalise
            db.events.update_one({"_id":event_id},{ "$set": { "issueDt": datetime.now() } } )
            finalized = True
            db_result = db.events.find_one({"_id":event_id})  # possibility of this being executed before update
            menu_items = [  [f"ID : {db_result['_id']}",False],
                            [f"Event Name : {db_result['name']}",True],
                            [f"Description : {db_result['desc']}",True],
                            [f"Issue Date : {db_result['issueDt']}",False],
                            [f"Participant Fields : {db_result['fields']}",True],]

        elif key == 83 or key == 115: # View Participants
            viewParticipants(win, event_id, finalized)
        elif key == curses.KEY_UP and selected_index > 0:
            selected_index -= 1
        elif key == curses.KEY_DOWN and selected_index < len(menu_items)-1:
            selected_index += 1
        elif key in [curses.KEY_ENTER, 10, 13]: # Edit Field
            if not finalized:
                if menu_items[selected_index][1]: # if editable
                    # enter new field value and update
                    y+=2
                    win.addstr(y,x,"Enter New Value : ", curses.color_pair(2))
                    curses.echo()
                    val = win.getstr().decode("utf-8")
                    curses.noecho()
                    db.events.update_one({"_id":event_id},{ "$set": { menu_items[selected_index][2] : val } } )
                    db_result = db.events.find_one({"_id":event_id})  # possibility of this being executed before update
                    menu_items = [  [f"ID : {db_result['_id']}",False],
                                    [f"Event Name : {db_result['name']}",True],
                                    [f"Description : {db_result['desc']}",True],
                                    [f"Issue Date : {db_result['issueDt']}",False],
                                    [f"Participant Fields : {db_result['fields']}",True],]



def viewParticipants(win, event_id, finalized):
    # ... Participant List // View Participant with inline value edit functionality

    participants_list = list(db.participants.find({"event_id" : event_id},{"_id" : 1, "name":1}))
    # print(participants_list)
    selected_row_idx = 0 # initially select index

    while True:
        win.clear()
        x,y = 0,0
        if not finalized:
            win.addstr(y, x,"Add Participant [+] | Add Via CSV [~]",curses.color_pair(1))
            y+=2
        else:
            win.addstr(y, x,"[FINALIZED]", curses.color_pair(1))
            y+=2

        if participants_list == []:
            win.addstr(y , x,"No participants added")
            y+=1
        else:
            for idx, item in enumerate(participants_list):
                if idx == selected_row_idx:
                    win.addstr(y, x, f"{item['_id']} {item['name']}", curses.color_pair(2))
                else:
                    if finalized == False: # check finalized
                        win.addstr(y, x, f"{item['_id']} {item['name']}", curses.color_pair(3))
                    else:
                        win.addstr(y, x, f"{item['_id']} {item['name']}")
                y += 1
        

        key = win.getch()
        if key == 81 or key == 113: # Quit
            return
        elif key == 43: # Register
            addParticipantCLI(win, event_id)
            participants_list = list(db.participants.find({"event_id" : event_id},{"_id" : 1, "name":1}))
        elif key == curses.KEY_UP and selected_row_idx > 0:
            selected_row_idx -= 1
        elif key == curses.KEY_DOWN and selected_row_idx < len(participants_list)-1:
            selected_row_idx += 1
        elif key in [curses.KEY_ENTER, 10, 13]: # View Event
            viewParticipant(win, participants_list[selected_row_idx]["_id"], finalized)
            participants_list = list(db.participants.find({"event_id" : event_id},{"_id" : 1, "name":1}))
        else:
            continue

def addParticipantCLI(win, event_id):
    curses.curs_set(True)
    curses.echo()
    win.clear()
    x,y = 0,0

    item = {}
    fields = db.events.find({"_id":event_id},{"fields":1})

    win.addstr(y,x,"Name : ", curses.color_pair(1))
    item["name"] = win.getstr().decode("utf-8") 
    y+=1
    item["event_id"] = event_id
    for field in fields[0]["fields"]:
        win.addstr(y, x, field+' : ' ,curses.color_pair(1))
        item[field] = win.getstr().decode("utf-8") 
        y+=1
    db.participants.insert_one(item)

    curses.noecho()
    curses.curs_set(False)


def addParticipantCSV():
    # https://docs.python.org/3/library/csv.html#csv.DictReader
    raise NotImplementedError

def viewParticipant(win, participant_id, finalized):
    db_result = db.participants.find_one({"_id":participant_id})
    selected_index = 0

    menu_items = []
    for field, value in db_result.items():
        if field in ["_id", "event_id"]:
            menu_items.append([f"{field} : {value}", False]) # IDs are not editable
        else:
            menu_items.append([f"{field} : {value}", True, f"{field}"])
    # print(menu_items)

    while True:
        win.clear()
        x,y = 0,0

        if not finalized:
            win.addstr(y, x, f"[MODIFIABLE]", curses.color_pair(3))
            y+=2

            for idx, item in enumerate(menu_items):
                if idx == selected_index:
                    win.addstr(y, x, item[0],curses.color_pair(2))
                else:
                    if item[1]: # check if editable field
                        win.addstr(y, x, item[0],curses.color_pair(3))
                    else:
                        win.addstr(y, x, item[0])
                y += 1
            y+=1
        else:
            win.addstr(y, x, f"[FINALIZED]", curses.color_pair(1))
            y+=2

            for item in menu_items:
                win.addstr(y, x, item[0])
                y += 1
            y+=1

        key = win.getch()

        if key == 81 or key == 113: # Quit
            break
        elif key == curses.KEY_UP and selected_index > 0:
            selected_index -= 1
        elif key == curses.KEY_DOWN and selected_index < len(menu_items)-1:
            selected_index += 1
        elif key in [curses.KEY_ENTER, 10, 13]: # Edit Field
            if not finalized:
                if menu_items[selected_index][1]: # if editable
                    # enter new field value and update
                    y+=2
                    win.addstr(y,x,"Enter New Value : ", curses.color_pair(2))
                    curses.curs_set(True)
                    curses.echo()
                    val = win.getstr().decode("utf-8")
                    curses.noecho()
                    curses.curs_set(False)
                    db.participants.update_one({"_id":participant_id},{ "$set": { menu_items[selected_index][2] : val } } )
                    db_result = db.participants.find_one({"_id":participant_id})
                    menu_items = []
                    for field, value in db_result.items():
                        if field in ["_id", "event_id"]:
                            menu_items.append([f"{field} : {value}", False]) # IDs not editable
                        else:
                            menu_items.append([f"{field} : {value}", True, f"{field}"])



# Main Screen Function
curses.wrapper(init)

# In Line Edit Functionality
# Hover over the line to edit and Ctrl E to edit , allows editing only the editable parts