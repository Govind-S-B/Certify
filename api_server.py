from flask import Flask, make_response,request
from bson import ObjectId
from pymongo import MongoClient
import json
from datetime import datetime

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return str(obj)
        return super().default(obj)

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client.certify

# status check

@app.route('/active', methods=['GET'])
def get_active_status():
    response = {'active': True}
    
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# for validate page

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

# for admin page

@app.route('/admin/add/event', methods=['POST'])
def add_event():
    item = {}
    
    item["name"] = str(request.args.get('name'))
    item['desc'] = str(request.args.get('desc'))
    item['fields'] = str(request.args.get('fields')).split()
    item['issueDt'] = None

    db.events.insert_one(item)

    response = {"db entry status":True}

    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

# for figma plugin

@app.route("/plugin/getgeninfo", methods=['GET'])
def get_gen_info():
    event_id = ObjectId(request.args.get('event_id'))

    # make queries
    event = db.events.find_one({"_id":event_id},{"fields":0})
    participants = list(db.participants.find({"event_id":event_id}))

    response = {
        "event": event,
        "participants": participants
    }

    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    r.headers.add('Access-Control-Allow-Origin', '*')
    return r

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969)
