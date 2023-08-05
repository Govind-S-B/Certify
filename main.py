from pymongo import MongoClient
import curses
from datetime import datetime
import csv
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

def main_screen(win): # View Events

    selected_row_idx = 0 # initially select index
    events_list = list(db.events.find({},{"_id":1,"name":1,"issueDt":1}))

    while True:
        win.clear()
        x , y = 0,0
        win.addstr(y,x,"======= Certify CLI v1.0 =======", curses.color_pair(1))
        y+=1
        win.addstr(y, x,"Navigate [up/down arrows] | Register New Event [+] | Quit [q]", curses.color_pair(1))
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
            if selected_row_idx >= len(events_list):
                selected_row_idx -= 1 # to move the highlight up by one row after deletion

def reg_event(win):
    curses.curs_set(True)
    curses.echo()
    win.clear()
    x,y = 0,0

    data = {}
    win.addstr(y, x, "Event Name : ", curses.color_pair(1))
    data["name"] = win.getstr().decode("utf-8") 
    y+=1
    win.addstr(y, x, "Description : ", curses.color_pair(1))
    data["desc"] = win.getstr().decode("utf-8")
    y+=1

    win.addstr(y, x, "Fields - seperated by commas(,) : ", curses.color_pair(1))
    val = win.getstr().decode("utf-8")
    fields_list = [item.strip() for item in val.split(',')]
    data["fields"] = fields_list
    y+=1

    response = requests.post('http://localhost:6969/admin/add/event', params=data)
    # print(response.text)

    curses.noecho()
    curses.curs_set(False)

def view_event(win, event_id):
    # View Event Details with edit functionality 
    # Show Participant List option below

    db_result = db.events.find_one({"_id" : event_id})
    
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
                if idx == selected_index:
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

        win.addstr(y,x,f"Show Participants [S]", curses.color_pair(1))
        y+=1
        if not finalized:
            win.addstr(y,x,f"Delete Event [D]", curses.color_pair(1))
            y+=1

        key = win.getch()
        if key == 81 or key == 113: # Quit
            break
        elif key == 70 or key == 102: # Finalise
            if not finalized:
                y+=1
                win.addstr(y,x,"Are you sure? [y/n] : ", curses.color_pair(2))
                curses.echo()
                val = win.getstr().decode("utf-8")
                curses.noecho()
                if val.lower() == "y":
                    t = datetime.now()
                    db.events.update_one({"_id":event_id},{ "$set": { "issueDt": t } } )
                    finalized = True
                    menu_items[3][0] = f"Issue Date : {t}"

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
                    if selected_index == 4:
                        # for updating fields
                        y+=2
                        win.addstr(y,x,"## 'name' and 'event_id' are present as default fields and cannot be deleted ##", curses.color_pair(3))
                        y+=1
                        win.addstr(y,x,"Enter required fields seperated by commas(,) : ", curses.color_pair(2))
                        curses.curs_set(True)
                        curses.echo()
                        val = win.getstr().decode("utf-8")
                        curses.noecho()
                        curses.curs_set(False)
                        if val == "":
                            fields_list = []
                        else:
                            fields_list = [item.strip() for item in val.split(',')]
                        db.events.update_one({"_id":event_id},{ "$set": { menu_items[selected_index][2] : fields_list } } )
                    else:
                        y+=2
                        win.addstr(y,x,"Enter New Value : ", curses.color_pair(2))
                        curses.curs_set(True)
                        curses.echo()
                        val = win.getstr().decode("utf-8")
                        curses.noecho()
                        curses.curs_set(False)
                        db.events.update_one({"_id":event_id},{ "$set": { menu_items[selected_index][2] : val } } )

                    db_result = db.events.find_one({"_id":event_id})  # possibility of this being executed before update
                    menu_items = [  [f"ID : {db_result['_id']}",False],
                                    [f"Event Name : {db_result['name']}",True,'name'],
                                    [f"Description : {db_result['desc']}",True,'desc'],
                                    [f"Issue Date : {db_result['issueDt']}",False],
                                    [f"Participant Fields : {db_result['fields']}",True,'fields']]
        elif key in [100, 68]:
            if not finalized:
                y+=1
                win.addstr(y,x,"Are you sure? [y/n] : ", curses.color_pair(2))
                curses.echo()
                val = win.getstr().decode("utf-8")
                curses.noecho()
                if val.lower() == "y":
                    db.events.delete_one({"_id" : event_id})
                    db.participants.delete_many({"event_id" : event_id})
                    break



def viewParticipants(win, event_id, finalized):
    # ... Participant List // View Participant with inline value edit functionality

    participants_list = list(db.participants.find({"event_id" : event_id},{"_id" : 1, "name":1}))
    selected_row_idx = 0 # initially select index

    while True:
        win.clear()
        x,y = 0,0
        if not finalized:
            win.addstr(y, x,"Add Participant [+] | Add Via CSV [~] | Delete All Participants [D] | Go Back [Q]",curses.color_pair(1))
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
        elif key == 126 : # Register
            addParticipantCSV(win, event_id)
            participants_list = list(db.participants.find({"event_id" : event_id},{"_id" : 1, "name":1}))
        elif key == curses.KEY_UP and selected_row_idx > 0:
            selected_row_idx -= 1
        elif key == curses.KEY_DOWN and selected_row_idx < len(participants_list)-1:
            selected_row_idx += 1
        elif key in [curses.KEY_ENTER, 10, 13]: # View Event
            viewParticipant(win, participants_list[selected_row_idx]["_id"], finalized)
            participants_list = list(db.participants.find({"event_id" : event_id},{"_id" : 1, "name":1}))
            if selected_row_idx >= len(participants_list):
                selected_row_idx -= 1 # to move the highlight up by one row after deletion
        elif key in [68, 100]:
            if not finalized:
                win.clear()
                x,y = 0,0
                win.addstr(y,x,"Are you sure? [y/n] : ", curses.color_pair(2))
                curses.echo()
                val = win.getstr().decode("utf-8")
                curses.noecho()
                if val.lower() == "y":
                    db.participants.delete_many({"event_id" : event_id})
                participants_list = list(db.participants.find({"event_id" : event_id},{"_id" : 1, "name":1}))
                selected_row_idx = 0

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


def addParticipantCSV(win,event_id):
    curses.curs_set(True)
    curses.echo()
    win.clear()
    x,y = 0,0

    win.addstr(y,x,"Enter CSV Name : ",curses.color_pair(1))
    csv_name = win.getstr().decode("utf-8") 
    y+=1

    curses.curs_set(False)
    curses.noecho()

    reader = []

    with open(csv_name, newline='') as csvfile: # possible error where header names dont match up , use value inside fields to cross check
        reader = list(csv.DictReader(csvfile))
        for row in reader:
            row["event_id"] = event_id

    db.participants.insert_many(reader)
    win.addstr(y,x,"Added successfully | Press any key to continue ",curses.color_pair(1))
    win.getch()

def viewParticipant(win, participant_id, finalized):
    db_result = db.participants.find_one({"_id":participant_id})
    selected_index = 0

    menu_items = []
    for field, value in db_result.items():
        if field in ["_id", "event_id"]:
            menu_items.append([f"{field} : {value}", False]) # IDs are not editable
        else:
            menu_items.append([f"{field} : {value}", True, f"{field}"])

    while True:
        win.clear()
        x,y = 0,0

        if not finalized:
            win.addstr(y, x, f"[MODIFIABLE] | Delete Participant [D] | Go Back [Q]", curses.color_pair(1))
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
            win.addstr(y, x, f"[FINALIZED] | Go Back [Q]", curses.color_pair(1))
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
        elif key in [68,100]:
            if not finalized:
                win.clear()
                x,y = 0,0
                win.addstr(y,x,"Are you sure? [y/n] : ", curses.color_pair(2))
                curses.echo()
                val = win.getstr().decode("utf-8")
                curses.noecho()
                if val.lower() == "y":
                    db.participants.delete_one({"_id" : participant_id})
                    break

# Main Screen Function
curses.wrapper(init)