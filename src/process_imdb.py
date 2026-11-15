import os
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from pprint import pprint

# %%  Connecting MongoDB Atlas
print("\nConnecting to MongoDB Atlas...")
uri = os.environ["MONGODB_URI"]
client = MongoClient(uri)

db = client['movies'] 
collection = db['imdb_data']  

# %% Query 1: Most frequent actor pairs
print("\nQuery 1: Most frequent actor pairs in movies (top 10)")

from collections import Counter
from itertools import combinations

pair_counter = Counter()

cursor = collection.find({"stars": {"$type": "array"}})

for doc in cursor:
    stars = [s for s in doc.get("stars", []) if isinstance(s, str) and s.strip()]
    if len(stars) >= 2:
        for pair in combinations(stars, 2):
            pair_key = " & ".join(sorted(pair))
            pair_counter[pair_key] += 1

top_10_pairs = pair_counter.most_common(10)

for pair, count in top_10_pairs:
    print(f"{pair}: {count} movies")


# %% Query 2: Average IMDb rating by certificate (e.g., PG, R)
print("\nQuery 2: Average IMDb rating by certificate")
pipeline = [
    {"$match": {"imdb_rating": {"$ne": None}, "certificate": {"$ne": None}}},
    {"$group": {"_id": "$certificate", "avg_rating": {"$avg": "$imdb_rating"}}},
    {"$sort": {"avg_rating": -1}}
]
for doc in collection.aggregate(pipeline):
    pprint(doc)

# %% Query 3: Find the longest movie(s)
print("\nQuery 3: Longest movie(s) by runtime")
pipeline = [
    {"$match": {"runtime": {"$regex": "min"}}},
    {"$project": {
        "title": 1,
        "runtime": 1,
        "runtime_minutes": {
            "$toInt": {"$arrayElemAt": [{"$split": ["$runtime", " "]}, 0]}
        }
    }},
    {"$sort": {"runtime_minutes": -1}},
    {"$limit": 5}
]
for doc in collection.aggregate(pipeline):
    pprint(doc)

# %% Query 4: Directors with the highest average gross (with at least 3 films)
print("\nQuery 4: Top directors by average gross (min 3 films)")
pipeline = [
    {"$match": {"gross": {"$ne": None}}},
    {"$group": {
        "_id": "$director",
        "avg_gross": {"$avg": "$gross"},
        "movie_count": {"$sum": 1}
    }},
    {"$match": {"movie_count": {"$gte": 3}}},
    {"$sort": {"avg_gross": -1}},
    {"$limit": 5}
]
for doc in collection.aggregate(pipeline):
    pprint(doc)

# %% Query 5: Decade-wise average rating
print("\nQuery 5: Average IMDb rating by decade")
pipeline = [
    {"$match": {"year": {"$ne": None}, "imdb_rating": {"$ne": None}}},
    {"$project": {
        "decade": {"$concat": [{"$toString": {"$subtract": ["$year", {"$mod": ["$year", 10]}]}}, "s"]},
        "imdb_rating": 1
    }},
    {"$group": {"_id": "$decade", "avg_rating": {"$avg": "$imdb_rating"}}},
    {"$sort": {"_id": 1}}
]
for doc in collection.aggregate(pipeline):
    pprint(doc)
