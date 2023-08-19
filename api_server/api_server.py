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


## STATUS

# Public
@app.route('/status', methods=['GET'])
def get_active_status():
    response = {'active': True}
    
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r


## EVENT

# Public
@app.route('/event/info', methods=['GET'])
def get_event_info():
    event_id = ObjectId(request.args.get('event_id'))
    query_result = db.events.find_one({"_id":event_id})
    r = make_response(json.dumps(query_result, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# load list of events
@app.route('/event/list', methods=['GET'])
def get_events_list():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)
    
    query_result = list(db.events.find({},{"_id":1,"name":1,"issueDt":1}))
    r = make_response(json.dumps(query_result, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# Add Event
@app.route('/event/add', methods=['POST'])
def add_event():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)
    
    item = {}
    item["name"] = str(request.args.get('name'))
    item['desc'] = str(request.args.get('desc'))
    item['fields'] =  str(request.args.get('fields')).split(',')
    item['issueDt'] = None
    db.events.insert_one(item)

    response = {"db entry status":True}
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# Finalize Event
@app.route('/event/finalize', methods=['POST'])
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
@app.route('/event/update', methods=['POST'])
def update_event():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)

    event_id = ObjectId(request.args.get('event_id'))
    field = str(request.args.get('field'))
    if field == "fields":
        value = str(request.args.get('value')).split(',')
    else:
        value = str(request.args.get('value'))
    db.events.update_one({"_id" : ObjectId(event_id)},{ "$set": { field : value } } )

    response = {"db entry status":True}
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# Delete Event
@app.route('/event/delete', methods=['DELETE'])
def delete_event():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)
    
    event_id = ObjectId(request.args.get('event_id'))
    db.events.delete_one({"_id" : event_id})
    db.participants.delete_many({"event_id" : event_id})

    response = {"db entry status":True}
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r


## PARTICIPANT

# Public
@app.route('/participant/info', methods=['GET'])
def get_participant_info():
    event_id = ObjectId(request.args.get('event_id'))
    participant_id = ObjectId(request.args.get('participant_id'))
    
    query_result = db.participants.find_one({"event_id":event_id,"_id" : participant_id})
    r = make_response(json.dumps(query_result, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# load list of participants
@app.route('/participant/list', methods=['GET'])
def get_participants_list():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)
    
    event_id = ObjectId(request.args.get('event_id'))
    query_result = list(db.participants.find({"event_id" : event_id}))
    r = make_response(json.dumps(query_result, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# add participants
@app.route('/participant/add', methods=['POST'])
def add_participants():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)
    
    data_string = request.args.get("data")
    items = json.loads(data_string)

    # Convert Participant Id from string to ObjectId
    for participant in items:
        if 'event_id' in participant:
            participant['event_id'] = ObjectId(participant['event_id'])
    db.participants.insert_many(items)

    response = {"db entry status":True}
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# Update Participant
@app.route('/participant/update', methods=['POST'])
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
    event_id = ObjectId(request.args.get('event_id'))
    field = str(request.args.get('field'))
    value = str(request.args.get('value'))

    # Update the participant's field in the database
    db.participants.update_one(
        {"_id" : participant_id, "event_id" : event_id},
        { "$set": {field : value} }
    )

    # Prepare the success response with status code 200
    response = {"db entry status":True}
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# Delete Participant
@app.route('/participant/delete', methods=['DELETE'])
def delete_participant():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)
    
    
    participant_id = ObjectId(request.args.get('participant_id'))
    event_id = ObjectId(request.args.get('event_id'))
    db.participants.delete_one({"_id" : participant_id, "event_id" : event_id})

    response = {"db entry status":True}
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# Delete Participants in bulk
@app.route('/participant/delete-batch', methods=['DELETE'])
def delete_participants():
    provided_key = request.headers.get("API-Auth-Key")
    if provided_key != api_auth_key:
        response = {"error": "Invalid API key"}
        return make_response(json.dumps(response), 401)
    
    event_id = ObjectId(request.args.get('event_id'))
    db.participants.delete_many({"event_id" : event_id})

    response = {"db entry status":True}
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r


## PLUGIN

@app.route("/plugin/gen-info", methods=['GET'])
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

