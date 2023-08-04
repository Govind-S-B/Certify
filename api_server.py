from flask import Flask, make_response
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

@app.route('/active', methods=['GET'])
def get_active_status():
    response = {'active': True}
    
    r = make_response(json.dumps(response, cls=CustomJSONEncoder))
    r.headers['Content-Type'] = 'application/json'
    return r

@app.route("/getgeninfo/<event_id>")
def get_gen_info(event_id):
    event_id = ObjectId(event_id)

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
