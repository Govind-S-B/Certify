from pymongo import MongoClient
import curses

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
        win.addstr(y,x,"== Certify CLI V1 ==",curses.color_pair(1))
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
    
    win.clear()
    x,y = 0,0
    item = db.events.find_one({"_id":event_id})

    finalized = True if (item["issueDt"] == None) else False

    if finalized:
        win.attron(curses.color_pair(3))
        win.addstr(y, x, f"[MODIFIABLE] [F to Finalize]")
        win.attroff(curses.color_pair(3))
    else:
        win.addstr(y, x, f"[FINALIZED]")

    y+=2

    win.addstr(y,x,f"ID : {item['_id']}",curses.color_pair(1))
    y+=1
    win.addstr(y,x,f"Event Name : {item['name']}",curses.color_pair(1))
    y+=1
    win.addstr(y,x,f"Description : {item['desc']}",curses.color_pair(1))
    y+=1
    win.addstr(y,x,f"Issue Date : {item['issueDt']}",curses.color_pair(1))
    y+=1
    win.addstr(y,x,f"Participant Fields : {item['fields']}",curses.color_pair(1))
    y+=2

    win.addstr(y,x,f"Show Participants [S]",curses.color_pair(3))
    y+=1

    key = win.getch()
    if key == 81 or key == 113: # Quit
        return
    elif key in [curses.KEY_ENTER, 10, 13]:
        viewParticipant(win, event_id, finalized)
    
    # viewParticipants(event_id,finalized)

def viewParticipants(win, event_id, finalized):
    # Add Participant [+]
    # Add Via CSV [~]
    # ... Participant List // View Participant with inline value edit functionality

    # participants_list = list(db.participants.find({},{"_id":1,"name":1,"issueDt":1}))
    participants_list = []
    selected_row_idx = 0 # initially select index

    while True:
        win.clear()
        x , y = 0,0
        win.addstr(y, x,"Add Participant [+] | Add Via CSV [~]",curses.color_pair(1))
        y+=2
        if participants_list == []:
            win.addstr(y,x,"No participants added")
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
            # participants_list = list(db.events.find({},{"_id":1,"name":1,"issueDt":1}))
        # elif key == curses.KEY_UP and selected_row_idx > 0:
        #     selected_row_idx -= 1
        # elif key == curses.KEY_DOWN and selected_row_idx < len(events_list)-1:
        #     selected_row_idx += 1
        # elif key in [curses.KEY_ENTER, 10, 13]: # View Event
        #     view_event(win,events_list[selected_row_idx]["_id"])
        #     events_list = list(db.events.find({},{"_id":1,"name":1,"issueDt":1}))
        else:
            continue

    # raise NotImplementedError

def addParticipantCLI(win, event_id):
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

    db.participants.insert_one(item)

    curses.noecho()
    curses.curs_set(False)


def addParticipantCSV():
    # https://docs.python.org/3/library/csv.html#csv.DictReader
    raise NotImplementedError

def viewParticipant(participant_id):
    raise NotImplementedError

# Main Screen Function
curses.wrapper(init)

# In Line Edit Functionality
# Hover over the line to edit and Ctrl E to edit , allows editing only the editable parts