from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# MongoDB connection
client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.1")
db = client.research_database
collection = db.crossrefpapers 

all_titles = []
with open('../ALL_TITLES.txt', 'r') as file:
    all_titles = file.readlines()
print(len(all_titles))
data = collection.find().to_list()

db_titles = []
for item in data:
    db_titles.append(item['title'][0])
    
print(len(db_titles))

confirmed_titles = []   
for title in all_titles:
    if title.replace('\n', '') in db_titles:
        confirmed_titles.append(title)
        
print(len(confirmed_titles))