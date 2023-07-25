from pymongo import MongoClient
import curses

client = MongoClient("mongodb://localhost:27017/")
db = client.certify

def mainScreen(): # View Events
    collection = db.events
    items = list(collection.find({},{"event":1,"name":1}))

    print("== Certify CLI v1 ==")
    print("Register New [+]") # Call Register Function , Come Back to main with screen refreshhed
    print()

    if items == None:
        print("No events registered")
    else:
        for i in items:
            print(f"{i['_id']} {i['name']}" ) # on click call ViewEvent function

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
mainScreen()

# In Line Edit Functionality
# Hover over the line to edit and Ctrl E to edit , allows editing only the editable parts