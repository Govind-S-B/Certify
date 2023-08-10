from bson import ObjectId
from pymongo import MongoClient
import curses
import requests

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

    selected_row = 0 # initially select index
    menu_items = ["Validate Event", "Validate Certificate"]

    while True:
        win.clear()
        x,y = 0,0
        win.addstr(y , x,"== Certify CLI v1.0 | Validation  ==", curses.color_pair(3))
        y+=1
        win.addstr(y, x,"Navigate [up/down arrows] | Quit [q]", curses.color_pair(1))
        y+=2

        for idx, item in enumerate(menu_items):
            if idx == selected_row:
                win.addstr(y, x, item, curses.color_pair(2))
            else:
                win.addstr(y, x, item)
            y += 1
        y+=1
        
        key = win.getch()
        if key == 81 or key == 113: # Quit
            break
        elif key == curses.KEY_UP and selected_row > 0:
            selected_row -= 1
        elif key == curses.KEY_DOWN and selected_row < len(menu_items)-1:
            selected_row += 1
        elif key in [curses.KEY_ENTER, 10, 13]:
            if selected_row == 0:
                win.clear()
                x,y = 0,0
                curses.curs_set(True)
                curses.echo()
                win.addstr(y, x, "Enter Event ID : ")
                event_id = win.getstr().decode("utf-8")
                curses.noecho()
                curses.curs_set(False)

                if (not ObjectId.is_valid(event_id)) or (len(event_id) != 24):
                    win.clear()
                    x,y = 0,0
                    win.addstr(y, x, "Invalid Event ID. Try again...")
                    y+=2
                else:
                    response = requests.get('http://localhost:6969/validate/geteventinfo', params = {"event_id" : event_id})
                    info = response.json()
                    
                    if info == None:
                        win.clear()
                        x,y = 0,0
                        win.addstr(y, x, "Sorry! no event was found with the provided Event ID")
                        y+=2
                    else:
                        win.clear()
                        x,y = 0,0
                        win.addstr(y, x, "Valid Event", curses.color_pair(3))
                        y+=2
                        win.addstr(y, x, f"Event ID : {info['_id']}")
                        y+=1
                        win.addstr(y, x, f"Event Name : {info['name']}")
                        y+=1
                        win.addstr(y, x, f"Description : {info['desc']}")
                        y+=1
                        win.addstr(y, x, f"Issue Date : {info['issueDt']}")
                        y+=1
                        win.addstr(y, x, f"Participant Fields : {info['fields']}")
                        y+=2

            elif selected_row == 1:
                win.clear()
                x,y = 0,0
                curses.curs_set(True)
                curses.echo()
                win.addstr(y, x, "Enter Event ID : ")
                event_id = win.getstr().decode("utf-8")
                y+=1
                win.addstr(y, x, "Enter Participant ID : ")
                participant_id = win.getstr().decode("utf-8")
                curses.noecho()
                curses.curs_set(False)

                if ((not ObjectId.is_valid(event_id)) or (len(event_id) != 24)) and ((not ObjectId.is_valid(participant_id)) or (len(participant_id) != 24)): # check if both Event _id and Participant _id are valid
                    win.clear()
                    x,y = 0,0
                    win.addstr(y, x, "Invalid Event ID and Participant ID. Try again...")
                    y+=2
                elif (not ObjectId.is_valid(event_id)) or (len(event_id) != 24): # check if Event _id is valid
                    win.clear()
                    x,y = 0,0
                    win.addstr(y, x, "Invalid Event ID. Try again...")
                    y+=2
                elif (not ObjectId.is_valid(participant_id)) or (len(participant_id) != 24): # check if Participant _id is valid
                    win.clear()
                    x,y = 0,0
                    win.addstr(y, x, "Invalid Participant ID. Try again...")
                    y+=2
                else:
                    response = requests.get('http://localhost:6969/validate/getparticipantinfo', params = {"event_id" : event_id , "participant_id" : participant_id})
                    info = response.json()
                    
                    # info = db.participants.find_one({"_id" : ObjectId(participant_id), "event_id" : ObjectId(event_id)})
                    if info == None:
                        win.clear()
                        x,y = 0,0
                        win.addstr(y, x, "Sorry! no certificate was found with the provided Participant ID for the given event.")
                        y+=2
                    else:
                        win.clear()
                        x,y = 0,0
                        win.addstr(y, x, "Valid Participant", curses.color_pair(3))
                        y+=2
                        for item in info:
                            if item == "_id":
                                win.addstr(y, x, f"Participant ID : {info[item]}")
                            elif item == "event_id":
                                win.addstr(y, x, f"Event ID : {info[item]}")
                            elif item == "name":
                                win.addstr(y, x, f"Name : {info[item]}")
                            else:
                                win.addstr(y, x, f"{item} : {info[item]}")
                            y+=1
                        y+=1

            win.addstr(y, x, "Press any key to continue ", curses.color_pair(3))
            win.getch()


curses.wrapper(init)

    # if event id only , print valid event and event details
    # if both , print valid participant id , show details of the user and link to event if requested