# from pymongo import MongoClient
# from bson import ObjectId
import curses
import csv
import requests
import json
from collections import Counter
# from time import sleep

# client = MongoClient("mongodb://admin:certifydb@localhost:50420/")
# db = client.certify

# putting auth key headers like this is bad
# fix later
headers = {
    "API-Auth-Key": "random_key"
    }

url = "http://localhost:8000"

def init(stdscr):
    # Hide the cursor
    curses.curs_set(False)

    # Enable keypad mode for special keys
    stdscr.keypad(True)

    # Initialize color pairs
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Default color scheme
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Highlighted color scheme
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Selectable fields color scheme

    # Call the main_screen function
    main_screen(stdscr)

def check_response(response, win, x=0, y=0, message=None):
    """
    Check the response status code and display a message in the given window.

    Parameters:
    - response: the response object from the server
    - win: the window object to display the message
    - x: the x-coordinate of the message position (default is 0)
    - y: the y-coordinate of the message position (default is 0)
    - message: a custom error message to display (default is None)

    Returns:
    - 0 if unable to connect to the server
    - 1 if connected successfully
    """
    if response.status_code != 200:
        win.clear()
        if message:
            error_message = message
        else:
            error_message = f"Unable to connect to the server. [Error: {response.status_code}] | Press any to continue..."
        win.addstr(y, x, error_message, curses.color_pair(3))
        win.getch()
        return 0
    else:
        return 1
    
def print_loading_screen(win, x=0, y=0, clear=True):
    # Clear the window if the 'clear' parameter is True
    if clear:
        win.clear()

    # Add the loading message to the window at the specified position
    win.addstr(y, x, "Loading... Please wait...", curses.color_pair(3))

    # Refresh the window to display the changes
    win.refresh()

    # Pause the execution for 0.3 seconds to simulate a loading delay
    # sleep(0.3)

def calc_x(string, total_width=20, offset=25):
    return offset + abs(total_width - len(string)) // 2

def main_screen(win): # View Events
    print_loading_screen(win)
    response = requests.get(f'{url}/event/list', headers=headers)
    if check_response(response, win) == 1: # if connected successfully
        events_list = response.json()
        selected_row_idx = 0 # initially select index

        while True: # loop for main page navigation
            win.clear()
            x , y = 0,0
            win.addstr(y,x,"================= Certify CLI v1.0 ==========================", curses.color_pair(1))
            y+=1
            win.addstr(y, x,"Navigate [up/down arrows] | Register New Event [+] | Quit [q]", curses.color_pair(1))
            y+=2

            if events_list == []:
                win.addstr(y,x,"No events registered")
                y+=1
            else:
                win.addstr(y,x+8,"Event Id")
                win.addstr(y,x+25,"|")
                win.addstr(y,x+32,"Event Name")
                y+=1
                win.addstr(y,x,"=========================|=====================")
                y+=1
                for idx, item in enumerate(events_list):
                    if idx == selected_row_idx:
                        win.addstr(y, x, f"{item['_id']}", curses.color_pair(2))
                        win.addstr(y, x+25, "|", curses.color_pair(0))
                        win.addstr(y, calc_x(item['name'], offset=27), f"{item['name']}", curses.color_pair(2))
                    else:
                        if item["issueDt"] == None: # check if finalized
                            win.addstr(y, x, f"{item['_id']}", curses.color_pair(3))
                            win.addstr(y, x+25, "|", curses.color_pair(0))
                            win.addstr(y, calc_x(item['name'], offset=27), f"{item['name']}", curses.color_pair(3))
                        else:
                            win.addstr(y, x, f"{item['_id']}")
                            win.addstr(y, x+25, f"|")
                            win.addstr(y, calc_x(item['name'], offset=27), f"{item['name']}")
                    y += 1

            key = win.getch() # keyboard input
            if key in [8, 81, 113]: # Quit
                break
            elif key == 43: # Register New Event
                reg_event(win)
                print_loading_screen(win)
                response = requests.get(f'{url}/event/list', headers = headers)
                if check_response(response, win) == 1:
                    events_list = response.json()

            elif key == curses.KEY_UP and selected_row_idx > 0: # navigate up
                selected_row_idx -= 1
            elif key == curses.KEY_DOWN and selected_row_idx < len(events_list)-1: # navigate down
                selected_row_idx += 1

            elif (key in [curses.KEY_ENTER, 10, 13]) and (len(events_list)>0): # View Event
                if view_event(win,events_list[selected_row_idx]["_id"]) == 1: # if there is any changes, update the events list
                    print_loading_screen(win)
                    response = requests.get(f'{url}/event/list', headers = headers)
                    if check_response(response, win) == 1:
                        events_list = response.json()
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
    if val == "":
        # fields_list = []
        y+=1
        win.addstr(y, x, "Atleast one field is required!", curses.color_pair(3))
        while True:
            val = win.getstr(y-1, 34).decode("utf-8")
            if val != "":
                break
    fields_list = [item.strip() for item in val.split(',')]
    data["fields"] = fields_list
    y+=2
    curses.noecho()
    curses.curs_set(False)

    print_loading_screen(win)
    response = requests.post(f'{url}/event/add', params = data, headers = headers)
    win.clear()
    if check_response(response, win) == 1:
        win.addstr(0, 0, "Added Event Successfully | Press any key to continue...", curses.color_pair(3))
        win.getch()


def view_event(win, event_id):
    print_loading_screen(win)
    response = requests.get(f'{url}/event/info', params = {"event_id" : event_id}, headers = headers)
    event_edited = False

    if check_response(response, win) == 1:
        db_result = response.json()
        finalized = False if (db_result['issueDt'] == None) else True
        selected_index = 0

        # Field_Content , Selectable or Not , field name (used for editing and updating)
        menu_items = [  [f"Event ID : {db_result['_id']}", False],
                        [f"Event Name : {db_result['name']}", True, 'name'],
                        [f"Description : {db_result['desc']}", True, 'desc'],
                        [f"Issue Date : {db_result['issueDt']}", False],
                        [f"Participant Fields : {', '.join(db_result['fields'])}", True, 'fields'],]

        while True:
            win.clear()
            x,y = 0,0

            # List event details
            if not finalized:
                win.addstr(y, x, f"*MODIFIABLE*", curses.color_pair(3))
                win.addstr(y, x+14, f"Finalize Event [F] | Delete Event [D] | Show Participants [S]", curses.color_pair(1))
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
                win.addstr(y, x, f"*FINALIZED*  Show Participants [S]", curses.color_pair(1))
                y+=2
                for item in menu_items:
                    win.addstr(y, x, item[0])
                    y += 1
                y+=1

            key = win.getch()
            if key in [8, 81, 113]: # Quit
                break
            elif key == 70 or key == 102: # Finalise
                if not finalized:
                    y+=1
                    win.addstr(y,x,"Are you sure? [Y/n] : ", curses.color_pair(2))
                    curses.echo()
                    val = win.getstr().decode("utf-8")
                    curses.noecho()
                    if val.lower() == "y":
                        response = requests.post(f'{url}/event/finalize', params = {"event_id" : event_id}, headers = headers)
                        if check_response(response, win) == 1:
                            finalized = True
                            menu_items[3][0] = f"Issue Date : {response.json()['issueDt']}"

            elif key == curses.KEY_UP and selected_index > 0: # move up
                selected_index -= 1
            elif key == curses.KEY_DOWN and selected_index < len(menu_items)-1: # move down
                selected_index += 1
            elif key in [curses.KEY_ENTER, 10, 13]: # Edit Field
                if not finalized:
                    if menu_items[selected_index][1]: # if editable
                        # enter new field value and update
                        if selected_index == 4:
                            # for updating fields
                            y+=1
                            win.addstr(y,x,"## 'event_id' is present as a default field and cannot be deleted ##", curses.color_pair(3))
                            y+=1
                            win.addstr(y,x,"Enter required fields seperated by commas(,) : ", curses.color_pair(2))
                            curses.curs_set(True)
                            curses.echo()
                            val = win.getstr().decode("utf-8")
                            if val == "":
                                y+=1
                                win.addstr(y, x, "Atleast one field is required!", curses.color_pair(3))
                                while True:
                                    val = win.getstr(y-1, 48).decode("utf-8")
                                    if val != "":
                                        break
                            fields_list = [item.strip() for item in val.split(',')]
                            curses.noecho()
                            curses.curs_set(False)
                            # db.events.update_one({"_id" : ObjectId(event_id)},{ "$set": { menu_items[selected_index][2] : fields_list } } )
                            response = requests.post(f'{url}/event/update', params = {"event_id" : event_id, "field" : menu_items[selected_index][2], "value" : val}, headers = headers)
                        else:
                            win.addstr(y,x,"Enter New Value : ", curses.color_pair(2))
                            curses.curs_set(True)
                            curses.echo()
                            val = win.getstr().decode("utf-8")
                            curses.noecho()
                            curses.curs_set(False)
                            # db.events.update_one({"_id" : ObjectId(event_id)},{ "$set": { menu_items[selected_index][2] : val } } )
                            response = requests.post(f'{url}/event/update', params = {"event_id" : event_id, "field" : menu_items[selected_index][2], "value" : val}, headers = headers)
                        if check_response(response, win) == 1:
                            event_edited = True #left to implement
                            y-=1
                            # for i in range(4):
                            win.move(y, x)  # Move the cursor to the beginning of the line
                            win.clrtoeol()  # Clear the entire line
                            win.move(y+1, x)
                            win.clrtoeol()
                            win.addstr(y,x,f"Event {menu_items[selected_index][2]} updated successfully | Press any key to continue...", curses.color_pair(3))
                            win.getch()
                            # db_result = db.events.find_one({"_id" : ObjectId(event_id)})  # possibility of this being executed before update
                            response = requests.get(f'{url}/event/info', params = {"event_id" : event_id}, headers = headers)
                            if check_response(response, win) == 1:
                                db_result = response.json()
                                menu_items = [  [f"Event ID : {db_result['_id']}",False],
                                                [f"Event Name : {db_result['name']}",True,'name'],
                                                [f"Description : {db_result['desc']}",True,'desc'],
                                                [f"Issue Date : {db_result['issueDt']}",False],
                                                [f"Participant Fields : {', '.join(db_result['fields'])}",True,'fields']]
                            
            elif key in [100, 68]:
                if not finalized:
                    y+=1
                    win.addstr(y,x,"Are you sure? [Y/n] : ", curses.color_pair(2))
                    curses.echo()
                    val = win.getstr().decode("utf-8")
                    curses.noecho()
                    if val.lower() == "y":
                        # db.events.delete_one({"_id" : ObjectId(event_id)})
                        # db.participants.delete_many({"event_id" : event_id})
                        print_loading_screen(win)
                        response = requests.delete(f'{url}/event/delete', params = {"event_id" : event_id}, headers = headers)
                        if check_response(response, win) == 1:
                            win.clear()
                            win.addstr(0, 0, "Event Deleted Successfully | Press any key to continue...", curses.color_pair(3))
                            win.getch()
                            break
            elif key == 83 or key == 115: # View Participants
                viewParticipants(win, event_id, finalized, db_result['fields'])
        return 1    # 1 indicates db is updated
    return 0 # passes 0 if unable to connect indicating no change in db

def viewParticipants(win, event_id, finalized, fields):
    # ... Participant List // View Participant with inline value edit functionality

    # participants_list = list(db.participants.find({"event_id" : event_id},{"_id" : 1, "name":1}))
    print_loading_screen(win)
    response = requests.get(f'{url}/participant/list', params = {"event_id" : event_id}, headers = headers)
    if check_response(response, win) == 1:
        participants_list = response.json()
        selected_row_idx = 0 # initially select index
        while True:
            win.clear()
            x,y = 0,0
            if not finalized:
                if participants_list == []:
                    win.addstr(y, x, f"*MODIFIABLE*", curses.color_pair(3))
                    win.addstr(y, x+14, f"Add Participant [+] | Add Via CSV [~] | Go Back [Q]", curses.color_pair(1))
                else:
                    win.addstr(y, x, f"*MODIFIABLE*", curses.color_pair(3))
                    win.addstr(y, x+14, "Add Participant [+] | Add Via CSV [~] | Delete All Participants [D] | Go Back [Q]",curses.color_pair(1))
                y+=2
            else:
                win.addstr(y, x,"*FINALIZED*  Go Back [Q]", curses.color_pair(1))
                y+=2

            if participants_list == []:
                win.addstr(y , x,"No participants added")
                y+=1
            else:
                win.addstr(y, x+6, "Participant Id")
                win.addstr(y, x+25, "|")
                win.addstr(y, calc_x(fields[0]), fields[0])
                y+=1
                win.addstr(y,x,"=========================|====================")
                y+=1
                for idx, item in enumerate(participants_list):
                    if idx == selected_row_idx:
                        # win.addstr(y, x, f"{item['_id']} {item[fields[0]]}", curses.color_pair(2))
                        win.addstr(y, x, f"{item['_id']}", curses.color_pair(2))
                        win.addstr(y, x+25, "|", curses.color_pair(0))
                        win.addstr(y, calc_x(item[fields[0]]), f"{item[fields[0]]}", curses.color_pair(2))
                    else:
                        if finalized == False: # check finalized
                            # win.addstr(y, x, f"{item['_id']} {item[fields[0]]}", curses.color_pair(3))
                            win.addstr(y, x, f"{item['_id']}", curses.color_pair(3))
                            win.addstr(y, x+25, "|", curses.color_pair(0))
                            win.addstr(y, calc_x(item[fields[0]]), f"{item[fields[0]]}", curses.color_pair(3))
                        else:
                            # win.addstr(y, x, f"{item['_id']} | {item[fields[0]]}")
                            win.addstr(y, x, f"{item['_id']}")
                            win.addstr(y, x+25, "|")
                            win.addstr(y, calc_x(item[fields[0]]), f"{item[fields[0]]}")
                    y += 1
            
            key = win.getch()
            if key in [8, 81, 113]: # Quit
                return
            elif key == curses.KEY_UP and selected_row_idx > 0: # navigate up
                selected_row_idx -= 1
            elif key == curses.KEY_DOWN and selected_row_idx < len(participants_list)-1: # navigate down
                selected_row_idx += 1

            elif key == 43: # Register CLI
                addParticipantCLI(win, event_id, fields)
                # participants_list = list(db.participants.find({"event_id" : event_id},{"_id" : 1, "name":1}))
                print_loading_screen(win)
                response = requests.get(f'{url}/participant/list', params = {"event_id" : event_id}, headers = headers)
                if check_response(response, win) == 1:
                    participants_list = response.json()

            elif key == 126 : # Register CSV
                addParticipantCSV(win, event_id, fields)
                # participants_list = list(db.participants.find({"event_id" : event_id},{"_id" : 1, "name":1}))
                print_loading_screen(win)
                response = requests.get(f'{url}/participant/list', params = {"event_id" : event_id}, headers = headers)
                if check_response(response, win) == 1:
                    participants_list = response.json()

            elif (key in [curses.KEY_ENTER, 10, 13]) and (len(participants_list)>0): # View Participant
                if viewParticipant(win, event_id, participants_list[selected_row_idx]["_id"], finalized) == 1: # if db updated, update the participants list
                    # participants_list = list(db.participants.find({"event_id" : event_id},{"_id" : 1, "name":1}))
                    print_loading_screen(win)
                    response = requests.get(f'{url}/participant/list', params = {"event_id" : event_id}, headers = headers)
                    if check_response(response, win) == 1:
                        participants_list = response.json()
                        if selected_row_idx >= len(participants_list):
                            selected_row_idx -= 1 # to move the highlight up by one row after deletion

            elif (key in [68, 100]) and (len(participants_list)>0):
                if not finalized:
                    win.clear()
                    x,y = 0,0
                    win.addstr(y,x,"Are you sure? [Y/n] : ", curses.color_pair(2))
                    curses.echo()
                    val = win.getstr().decode("utf-8")
                    curses.noecho()
                    if val.lower() == "y":
                        # db.participants.delete_many({"event_id" : event_id})
                        print_loading_screen(win)
                        response = requests.delete(f'{url}/participant/delete-batch', params = {"event_id" : event_id}, headers = headers)
                        if check_response(response, win) == 1:
                            win.clear()
                            win.addstr(0, 0, "Participants Deleted Successfully | Press any key to continue...", curses.color_pair(3))
                            win.getch()
                            participants_list = []
                            selected_row_idx = 0


def addParticipantCLI(win, event_id, fields):
    curses.curs_set(True)
    curses.echo()
    win.clear()
    x,y = 0,0
    item = {}
    item["event_id"] = event_id
    
    for field in fields:
        win.addstr(y, x, field+' : ' ,curses.color_pair(1))
        item[field] = win.getstr().decode("utf-8") 
        y+=1

    json_string = json.dumps([item])
    print_loading_screen(win)
    response = requests.post(f'{url}/participant/add', params = {"data": json_string}, headers = headers)
    if check_response(response, win) == 1:
        win.clear()
        win.addstr(0, 0, "Participant added successfully | Press any key to continue...", curses.color_pair(3))
        win.getch()

    curses.noecho()
    curses.curs_set(False)


def addParticipantCSV(win, event_id, fields):
    curses.curs_set(True)
    curses.echo()
    win.clear()
    x,y = 0,0
    win.addstr(y, x, f"The CSV file should have the following headers : {', '.join(fields)}", curses.color_pair(1))
    y+=2
    win.addstr(y, x, "Enter CSV File Name with extension (.csv) : ", curses.color_pair(1))
    csv_name = win.getstr().decode("utf-8") 
    y+=1

    curses.curs_set(False)
    curses.noecho()

    reader_list = []
    try:
        with open(csv_name, newline='') as csvfile: # possible error where header names dont match up , use value inside fields to cross check
            reader = csv.DictReader(csvfile)
            reader_list = list(reader)

            csv_headers = reader.fieldnames  # Get the headers from csv file(fields)
            if Counter(csv_headers) != Counter(fields):
                win.clear()
                win.addstr(0, 0, "Error:", curses.color_pair(3))
                win.addstr(0, 7, "CSV file headers don't match with the fields for the given event. Either correct the csv file headers or edit the fields in the Event details page.", curses.color_pair(1))
                win.addstr(2, 0, "Press any key to continue...", curses.color_pair(3))
                win.getch()
                return

            for row in reader_list:
                row["event_id"] = event_id
    except FileNotFoundError:
        win.clear()
        win.addstr(0, 0, "Error:", curses.color_pair(3))
        win.addstr(0, 7, "File not found! Check the file name and make sure that the file is present in the same directory.", curses.color_pair(1))
        win.addstr(2, 0, "Press any key to continue...", curses.color_pair(3))
        win.getch()
        return
    # db.participants.insert_many(reader)


    items = json.dumps(reader_list)
    print_loading_screen(win)
    response = requests.post(f'{url}/participant/add', params = {"data": items}, headers = headers)
    if check_response(response, win) == 1:
        win.clear()
        win.addstr(0,0,"Participants added successfully | Press any key to continue...", curses.color_pair(3))
        win.getch()

def viewParticipant(win, event_id, participant_id, finalized):
    print_loading_screen(win)
    response = requests.get(f'{url}/participant/info', params = {"participant_id" : participant_id, "event_id" : event_id}, headers = headers)
    if check_response(response, win) == 1:
        db_result = response.json()
        selected_index = 0
        participant_is_edited = False

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
                win.addstr(y, x, f"*MODIFIABLE*", curses.color_pair(3))
                win.addstr(y, x+14, f"Delete Participant [D] | Go Back [Q]", curses.color_pair(1))
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
                win.addstr(y, x, f"*FINALIZED*  Go Back [Q]", curses.color_pair(1))
                y+=2
                for item in menu_items:
                    win.addstr(y, x, item[0])
                    y += 1
                y+=1

            # key listeners and actions
            key = win.getch()
            if key in [8, 81, 113]: # Quit
                break

            elif key == curses.KEY_UP and selected_index > 0: # navigate up
                selected_index -= 1
            elif key == curses.KEY_DOWN and selected_index < len(menu_items)-1: # navigate down
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

                        # db.participants.update_one({"_id" : ObjectId(participant_id), "event_id" : event_id},{ "$set": { menu_items[selected_index][2] : val } } )
                        print_loading_screen(win)
                        response = requests.post(f'{url}/participant/update', params = {"participant_id" : participant_id, "event_id" : event_id, "field" : menu_items[selected_index][2], "value" : val}, headers = headers)
                        if check_response(response, win) == 1:
                            participant_is_edited = True
                            # db_result = db.participants.find_one({"_id" : ObjectId(participant_id), "event_id" : event_id})
                            response = requests.get(f'{url}/participant/info', params = {"participant_id" : participant_id, "event_id" : event_id}, headers = headers)
                            if check_response(response, win) == 1:
                                db_result = response.json()
                                menu_items = []
                                for field, value in db_result.items():
                                    if field in ["_id", "event_id"]:
                                        menu_items.append([f"{field} : {value}", False]) # IDs not editable
                                    else:
                                        menu_items.append([f"{field} : {value}", True, f"{field}"])

            elif key in [68,100]: # Delete participant
                if not finalized:
                    win.addstr(y,x,"Are you sure? [Y/n] : ", curses.color_pair(2))
                    curses.echo()
                    val = win.getstr().decode("utf-8")
                    curses.noecho()
                    if val.lower() == "y":
                        # db.participants.delete_one({"_id" : ObjectId(participant_id), "event_id" : event_id})
                        response = requests.delete(f'{url}/participant/delete', params = {"participant_id" : participant_id, "event_id" : event_id}, headers = headers)
                        if check_response(response, win) == 1:
                            participant_is_edited = True
                            break
    if participant_is_edited:
        return 1
    else:
        return 0


# Main Screen Function
curses.wrapper(init)