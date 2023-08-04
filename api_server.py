from flask import Flask,jsonify
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
app.json_encoder = CustomJSONEncoder

client = MongoClient("mongodb://localhost:27017/")
db = client.certify

@app.route('/active', methods=['GET'])
def get_active_status():
    response = {'active': True}
    return response

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

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969)
