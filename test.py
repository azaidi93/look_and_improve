import numpy as np
import pandas as pd
from pymongo import MongoClient
import settings
client = MongoClient('mongodb://127.0.0.1:27017/')
db = client.quiz
user = db.user

words = []
results = user.find_one({"name": settings.GLOBAL_USERNAME})
results = results.get("vocab")
print (len(results))
for key, value in results.items() :
    words.append(key)


for word in words:
    print word
