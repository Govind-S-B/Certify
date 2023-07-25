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

        if key == 81 or key == 113: # for quit
            break
        elif key == 43: # for Register new event  # Call Register Function , Come Back to main with screen refreshhed with new List
            print("add")
        elif key == curses.KEY_UP and selected_row_idx > 0:
            selected_row_idx -= 1
        elif key == curses.KEY_DOWN and selected_row_idx < len(items)-1:
            selected_row_idx += 1
        elif key in [curses.KEY_ENTER, 10, 13]: # get the full event details ViewEvent
            print("go to next screen")

def regEvent(event_id):
    print()

def ViewEvent(event_id):
    # View Event Details with edit functionality 
    # Show Participant List option below
    print()

def ViewParticipants(event_id):
    # Add Participant [+]
    # Add Via CSV [~]
    # ... Participant List // View Participant with inline value edit functionality
    print()

def addParticipantCLI():
    print()

def addParticipantCSV():
    print()

def ViewParticipant(participant_id):
    print()

# Main Screen Function
curses.wrapper(init)

# In Line Edit Functionality
# Hover over the line to edit and Ctrl E to edit , allows editing only the editable parts