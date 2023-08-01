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

    items = list(db.events.find({},{"_id":1,"name":1,"issueDt":1}))

    while True:

        win.clear()
        x , y = 0,0
        win.addstr(y,x,"== Certify CLI V1 ==",curses.color_pair(1))
        y+=1
        win.addstr(y, x,"Quit [Q] | Register New [+]",curses.color_pair(1))
        y+=2

        if items == []:
            win.addstr(y,x,"No events registered")
            y+=1
        else:
            for idx, item in enumerate(items):
                if idx == selected_row_idx:
                    win.attron(curses.color_pair(2))
                    win.addstr(y, x, f"{item['_id']} {item['name']}")
                    win.attroff(curses.color_pair(2))
                else:
                    if item["issueDt"] == None: # check finalized
                        win.attron(curses.color_pair(3))
                        win.addstr(y, x, f"{item['_id']} {item['name']}")
                        win.attroff(curses.color_pair(3))
                    else:
                        win.addstr(y, x, f"{item['_id']} {item['name']}")
                y += 1

        key = win.getch()

        if key == 81 or key == 113: # Quit
            break
        elif key == 43: # Register
            reg_event(win)
            items = list(db.events.find({},{"_id":1,"name":1,"issueDt":1}))
        elif key == curses.KEY_UP and selected_row_idx > 0:
            selected_row_idx -= 1
        elif key == curses.KEY_DOWN and selected_row_idx < len(items)-1:
            selected_row_idx += 1
        elif key in [curses.KEY_ENTER, 10, 13]: # View Event
            view_event(win,items[selected_row_idx]["_id"])
            items = list(db.events.find({},{"_id":1,"name":1,"issueDt":1}))

def reg_event(win):
    curses.curs_set(True)
    curses.echo()
    win.clear()
    x,y = 0,0

    item = {"name":None,"desc":None,"issueDt":None,"fields":["_id","name"]}

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

def view_event(win,event_id):
    # View Event Details with edit functionality 
    # Show Participant List option below

    db_result = db.events.find_one({"_id":event_id})
    
    selected_index = 0

    # Field_Content , Selectable or Not , field name (used for editing and updationg)
    menu_items = [  [f"ID : {db_result['_id']}",False],
                    [f"Event Name : {db_result['name']}",True,'name'],
                    [f"Description : {db_result['desc']}",True,'desc'],
                    [f"Issue Date : {db_result['issueDt']}",False],
                    [f"Participant Fields : {db_result['fields']}",True,'fields'],]
    
    finalized = False if (db_result['issueDt'] == None) else True
    
    while True:
        win.clear()
        x,y = 0,0

        if not finalized:
            win.addstr(y, x, f"[MODIFIABLE] [F to Finalize]",curses.color_pair(3))
            y+=2

            for idx, item in enumerate(menu_items):
                if idx == selected_index  :
                    win.addstr(y, x, item[0],curses.color_pair(2))
                else:
                    if item[1]: #check if editable field
                        win.addstr(y, x, item[0],curses.color_pair(3))
                    else:
                        win.addstr(y, x, item[0])
                y += 1
            y+=1
        else:
            win.addstr(y, x, f"[FINALIZED]")
            y+=2

            for item in menu_items:
                win.addstr(y, x, item[0])
                y += 1
            y+=1

        win.addstr(y,x,f"Show Participants [S] ")
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
            viewParticipants(event_id,finalized)
        elif key == curses.KEY_UP and selected_index > 0:
            selected_index -= 1
        elif key == curses.KEY_DOWN and selected_index < len(menu_items)-1:
            selected_index += 1
        elif key in [curses.KEY_ENTER, 10, 13]: # Edit Field
            if not finalized:
                if menu_items[selected_index][1]: # if editable
                    # enter new field value and update
                    y+=2
                    win.addstr(y,x,"Enter New Value : ",curses.color_pair(2))
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



def viewParticipants(event_id,finalized):
    # Add Participant [+]
    # Add Via CSV [~]
    # ... Participant List // View Participant with inline value edit functionality
    raise NotImplementedError

def addParticipantCLI():
    raise NotImplementedError

def addParticipantCSV():
    # https://docs.python.org/3/library/csv.html#csv.DictReader
    raise NotImplementedError

def viewParticipant(participant_id):
    raise NotImplementedError

# Main Screen Function
curses.wrapper(init)

# In Line Edit Functionality
# Hover over the line to edit and Ctrl E to edit , allows editing only the editable parts