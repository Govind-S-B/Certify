from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client.certify

db.counter.insert_one({
   "_id" : "event",
   "seq" : 1
})