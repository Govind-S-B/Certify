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

def main_screen(win):

    win.clear()
    x,y = 0,0
    win.addstr(y,x,"== Certify CLI V1 | Validation  ==")
    y+=2

    win.addstr(y,x,"Enter Event ID : ")
    event_id = win.getstr().decode("utf-8")
    y+=1
    win.addstr(y,x,"Enter Participant ID : ")
    participant_id = win.getstr().decode("utf-8")
    y+=1

    win.clear()
    x,y = 0,0
    
    if participant_id == "":
        info = db.events.find({"_id":event_id})
        win.addstr(y,x,"Valid Event")
        y+=1
    else:
        info = db.events.find({"_id":participant_id,"event_id":event_id})

    # if event id only , print valid event and event details
    # if both , print valid participant id , show details of the user and link to event if requested