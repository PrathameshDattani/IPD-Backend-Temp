from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://temperature-dashboard-eosin.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
collection = db[os.getenv("COLLECTION_NAME")]

# Request Body Schema
class ItemRequest(BaseModel):
    item: str


# ------------------------------------------------
# OBJECT ID RANGES (EXACT FROM YOUR PDF)
# ------------------------------------------------
OBJECT_RANGES = {
    "Ice Gel Bag": {
        "start": ObjectId("692217a74bf378bf90fcc039"),   # Start  (Page 1)
        "end":   ObjectId("69222f454bf378bf90fcc294")    # End    (Page 2)
    },
    "Frozen Onion": {
        "start": ObjectId("6922a6742ac4169f239852e4"),    # Start  (Page 3)
        "end":   ObjectId("6922beb22ac4169f2398554f")     # End    (Page 4)
    },
    "Frozen Unpeeled Potato": {
        "start": ObjectId("6922cb2123a56a4d029c8b61"),    # Start  (Page 5)
        "end":   ObjectId("6922da9a23a56a4d029c8cec")     # End    (Page 6)
    },
    "Frozen Peeled Potato": {
        "start": ObjectId("6923044a53ea1203f6c35c11"),    # Start  (Page 7)
        "end":   ObjectId("6923264953ea1203f6c35f75")     # End    (Page 8)
    },
    "Frozen Tomato": {
        "start": ObjectId("69232a4913e11f2f97a58d13"),    # Start  (Page 9)
        "end":   ObjectId("6923535613e11f2f97a5912b")     # End    (Page 10)
    }
}


# Utility to convert _id → string
def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc


# ------------------------------------------------
# API ROUTE → Fetch all readings in the ID range
# ------------------------------------------------
@app.post("/get-readings")
def get_readings(req: ItemRequest):

    item = req.item

    if item not in OBJECT_RANGES:
        raise HTTPException(404, f"Invalid item: {item}")

    start_id = OBJECT_RANGES[item]["start"]
    end_id = OBJECT_RANGES[item]["end"]

    # Query MongoDB
    docs = list(
        collection.find({
            "_id": {
                "$gte": start_id,
                "$lte": end_id
            }
        }).sort("_id", 1)
    )

    return {
        "item": item,
        "count": len(docs),
        "readings": [serialize(doc) for doc in docs]
    }
