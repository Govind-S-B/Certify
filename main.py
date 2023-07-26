from pymongo import MongoClient
import curses

client = MongoClient("mongodb://localhost:27017/")
db = client.certify

def init(stdscr):
    curses.curs_set(False)
    stdscr.keypad(True)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    mainScreen(stdscr,0)

def mainScreen(win,selected_row_idx): # View Events

    items = list(db.events.find({},{"_id":1,"name":1}))

    while True:

        win.clear()
        x , y = 0,0
        win.addstr(y,x,"== Certify CLI V1 ==",curses.color_pair(1))
        y+=1
        win.addstr(y, x,"Quit [q] | Register New [+]",curses.color_pair(1))
        y+=2

        if items == None:
            win.addstr("No events registered")
        else:
            for idx, item in enumerate(items):
                if idx == selected_row_idx:
                    win.attron(curses.color_pair(2))
                    win.addstr(y, x, f"{item['_id']} {item['name']}")
                    win.attroff(curses.color_pair(2))
                else:
                    win.addstr(y, x, f"{item['_id']} {item['name']}")
                y += 1

        key = win.getch()

        if key == 81 or key == 113: # Quit
            break
        elif key == 43: # Register
            regEvent(win)
            items = list(db.events.find({},{"_id":1,"name":1}))
        elif key == curses.KEY_UP and selected_row_idx > 0:
            selected_row_idx -= 1
        elif key == curses.KEY_DOWN and selected_row_idx < len(items)-1:
            selected_row_idx += 1
        elif key in [curses.KEY_ENTER, 10, 13]:
            viewEvent(win,items[selected_row_idx]["_id"])

def regEvent(win):
    curses.curs_set(True)
    curses.echo()
    win.clear()
    x,y = 0,0

    item = {"_id":None,"name":None,"desc":None,"pCounter":0,"issueDt":None}

    win.addstr(y,x,"Event Name : ",curses.color_pair(1))
    item["name"] = win.getstr().decode("utf-8") 
    y+=1
    win.addstr(y,x,"Description : ",curses.color_pair(1))
    item["desc"] = win.getstr().decode("utf-8")
    
    # fetch id first and increment
    item["_id"] = db.counter.find_one_and_update(
          {"_id": "event"}, {"$inc":{"seq":1}}
        )["seq"]
    
    db.events.insert_one(item)

    curses.noecho()
    curses.curs_set(False)

def viewEvent(win,event_id):
    # View Event Details with edit functionality 
    # Show Participant List option below
    raise NotImplementedError

def viewParticipants(event_id):
    # Add Participant [+]
    # Add Via CSV [~]
    # ... Participant List // View Participant with inline value edit functionality
    raise NotImplementedError

def addParticipantCLI():
    raise NotImplementedError

def addParticipantCSV():
    raise NotImplementedError

def viewParticipant(participant_id):
    raise NotImplementedError

# Main Screen Function
curses.wrapper(init)

# In Line Edit Functionality
# Hover over the line to edit and Ctrl E to edit , allows editing only the editable parts