import logging
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from functions import Crf_dict_cursor

logging.basicConfig(
    filename='datacollection.log',  # Log file name
    level=logging.INFO,  # Log level: can be set to DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format
)
# MongoDB connection
client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.1")

# create a database
db = client.research_database

# create a collection
collection = db.crossrefpapers

logging.info("Database Setup Complete")
# call the dictionary creation function
data=Crf_dict_cursor()

nextcursor = data['next-cursor']

data = data['items']

logging.info(f"Cursor Dict Created: Number of Items recieved from function: {len(data)} Sending to: {collection.name}")
for item in data:
    doi = item['DOI']
    item["_id"] = doi
    logging.info(f"Sending item with DOI => {doi} => {collection.name}")
    with open('paper-doi-list.txt', 'w') as file:
        print(item['DOI'], '\n', file=file)
    try:
        collection.insert_one(item)
        logging.info(f"Inserted document with _id: {item['_id']} successfully...")
    except DuplicateKeyError:
        logging.debug(f"Duplicate _id {item['_id']} found. Skipping this document.....")
    
logging.info("Insertion Complete")

client.close()
