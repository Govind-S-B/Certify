from flask import Flask, make_response, request
from bson import ObjectId
from pymongo import MongoClient
import json
from datetime import datetime
import os  # Import the os module to access environment variables

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return str(obj)
        return super().default(obj)

app = Flask(__name__)

# Use environment variables for MongoDB connection
mongo_username = os.environ.get("DB_USERNAME")
mongo_password = os.environ.get("DB_PASSWORD")
mongo_host = "mongodb"  # Since you're using Docker Compose, you can use the service name as the host
mongo_port = "27017"

# Connect to MongoDB using environment variables
client = MongoClient(f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/")
db = client.certify

api_auth_key = os.environ.get("API_AUTH_KEY")


## for Status Check

@app.route('/active', methods=['GET'])
def get_active_status():
    response = {'active': True}
    
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r



## for Validate Page

@app.route('/validate/getparticipantinfo', methods=['GET'])
def get_participant_info():
    event_id = ObjectId(request.args.get('event_id'))
    participant_id = ObjectId(request.args.get('participant_id'))

    # make queries
    query_result = db.participants.find_one({"event_id":event_id,"_id" : participant_id})

    response = query_result

    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

@app.route('/validate/geteventinfo', methods=['GET'])
def get_event_info():
    event_id = ObjectId(request.args.get('event_id'))
    # make queries
    query_result = db.events.find_one({"_id":event_id})
    response = query_result
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r



## for Admin Page

# Add Event
@app.route('/admin/add/event', methods=['POST'])
def add_event():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)
    
    item = {}
    item["name"] = str(request.args.get('name'))
    item['desc'] = str(request.args.get('desc'))
    item['fields'] = request.args.getlist('fields')
    item['issueDt'] = None
    db.events.insert_one(item)

    response = {"db entry status":True}
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# Finalize Event
@app.route('/admin/update/finalize/event', methods=['POST'])
def finalize_event():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)

    event_id = ObjectId(request.args.get('event_id'))
    issueDt = datetime.now()
    db.events.update_one({"_id":event_id},{ "$set": { "issueDt": issueDt } } )

    response = {"db entry status":True, "issueDt":issueDt}
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# Update Event
@app.route('/admin/update/event', methods=['POST'])
def update_event():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)

    event_id = ObjectId(request.args.get('event_id'))
    field = str(request.args.get('field'))
    value = request.args.getlist('value')
    db.events.update_one({"_id" : ObjectId(event_id)},{ "$set": { field : value } } )

    response = {"db entry status":True}
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# load list of events
@app.route('/admin/view/eventslist', methods=['GET'])
def get_events_list():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)
    
    # make queries
    query_result = db.events.find({},{"_id":1,"name":1,"issueDt":1})
    response = list(query_result)
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# load event details
@app.route('/admin/view/eventinfo', methods=['GET'])
def get_event_info_admin():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)
    
    event_id = ObjectId(request.args.get('event_id'))
    # make queries
    query_result = db.events.find_one({"_id" : ObjectId(event_id)})
    response = query_result
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# load list of participants
@app.route('/admin/view/participantslist', methods=['GET'])
def get_participants_list():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)
    
    event_id = request.args.get('event_id')
    # make queries
    query_result = db.participants.find({"event_id" : event_id},{"_id" : 1, "name":1})
    response = list(query_result)
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# Load Participant details
@app.route('/admin/view/participantinfo', methods = ['GET'])
def get_participant_info_admin():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)
    
    participant_id = ObjectId(request.args.get('participant_id'))
    event_id = request.args.get('event_id')
    # make queries
    query_result = db.participants.find_one({"_id" : participant_id, "event_id" : event_id})
    response = query_result
    print(response)
    r = make_response(json.dumps(response, cls = CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# add participant
@app.route('/admin/add/participant', methods=['POST'])
def add_participant():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)
    
    data_string = request.args.get("data")
    item = json.loads(data_string)
    db.participants.insert_one(item)

    response = {"db entry status":True}
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# add participant in bulk
@app.route('/admin/add/participants', methods=['POST'])
def add_participants():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)
    
    data_string = request.args.get("data")
    items = json.loads(data_string)
    db.participants.insert_many(items)

    response = {"db entry status":True}
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# Update Participant
@app.route('/admin/update/participant', methods=['POST'])
def update_participant():
    # Get the provided API key from the request headers
    provided_key = request.headers.get("API-Auth-Key")

    # Check if the provided key matches the expected API key
    if provided_key != api_auth_key:
        # If the keys don't match, return an error response with status code 401
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)

    # Get the participant ID, event ID, field, and value from the request arguments
    participant_id = ObjectId(request.args.get('participant_id'))
    event_id = request.args.get('event_id')
    field = str(request.args.get('field'))
    value = str(request.args.get('value'))

    # Update the participant's field in the database
    db.participants.update_one(
        {"_id" : ObjectId(participant_id), "event_id" : event_id},
        { "$set": {field : value} }
    )

    # Print the field and value (for debugging purposes)
    print(field, "\t", value)

    # Prepare the success response with status code 200
    response = {"db entry status":True}
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r



## for Figma Plugin

@app.route("/plugin/getgeninfo", methods=['GET'])
def get_gen_info():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)
    
    event_id = ObjectId(request.args.get('event_id'))

    pipeline = [
        {
            "$match": {
                "_id": event_id
            }
        },
        {
            "$lookup": {
                "from": "participants",
                "localField": "_id",
                "foreignField": "event_id",
                "as": "participants"
            }
        },
        {
            "$project": {
                "_id": 0,
                "event": {
                    "_id": "$_id",
                    "name": "$name",
                    "desc": "$desc",
                    "issueDt": "$issueDt"
                },
                "participants": {
                    "$map": {
                        "input": "$participants",
                        "as": "participant",
                        "in": {
                            "$arrayToObject": {
                                "$filter": {
                                    "input": { "$objectToArray": "$$participant" },
                                    "as": "field",
                                    "cond": {
                                        "$ne": [ "$$field.k", "event_id" ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    ]

    result  = db.events.aggregate(pipeline).next()

    r = make_response(json.dumps(result, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    r.headers.add('Access-Control-Allow-Origin', '*')
    return r

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969)
