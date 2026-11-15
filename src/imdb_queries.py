import os
from pymongo import MongoClient
from pprint import pprint
import csv

# %% Connecting to MongoDB Atlas
print("\nConnecting to MongoDB...")
uri = os.environ["MONGODB_URI"]
client = MongoClient(uri)

db = client['movies']
collection = db['imdb_data']

print("\nAvailable databases:")
try:
    pprint(client.list_database_names())
except Exception as e:
    print("Error:", e)

print("\nTarget collection: movies.imdb_data")

# %% Loading Data from CSV 

file_path = os.path.join('data', 'imdb_top_1000.csv')

documents = []
print("\nReading and cleaning CSV data...")

with open(file_path, mode='r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if not row['Series_Title']:
            continue  # skip if no title

        genres = [g.strip() for g in row['Genre'].split(',')] if row.get('Genre') else []

        # Clean and validate certificate
        certificate = row.get('Certificate')
        certificate = certificate.strip() if certificate and certificate.strip() else None

        # Clean and validate runtime
        runtime = row.get('Runtime')
        runtime = runtime.strip() if runtime and 'min' in runtime else None

        # Build document
        doc = {
            "title": row['Series_Title'].strip(),
            "year": int(row['Released_Year']) if row['Released_Year'].isdigit() else None,
            "genre": genres,
            "director": row.get('Director', '').strip(),
            "stars": [row.get('Star1'), row.get('Star2'), row.get('Star3'), row.get('Star4')],
            "certificate": certificate,
            "runtime": runtime,
            "imdb_rating": float(row['IMDB_Rating']) if row.get('IMDB_Rating') else None,
            "gross": int(row['Gross'].replace(',', '')) if row.get('Gross') and row['Gross'].replace(',', '').isdigit() else None
        }

        documents.append(doc)

# Insert only if collection is empty
if collection.estimated_document_count() == 0 and documents:
    result = collection.insert_many(documents)
    print(f"\nInserted {len(result.inserted_ids)} documents into 'imdb_data'.")
else:
    print("\nCollection already has data or no documents to insert.")

# %% Query 1: Most frequent actor pairs

print("\nQuery 1: Most frequent actor pairs in movies (top 10)")

pair_counts = {}
cursor = collection.find({"stars": {"$type": "array"}})

for doc in cursor:
    stars = [s for s in doc.get("stars", []) if isinstance(s, str) and s.strip()]
    n = len(stars)
    for i in range(n):
        for j in range(i + 1, n):
            actor1 = stars[i].strip()
            actor2 = stars[j].strip()
            if actor1 and actor2:
                key = " & ".join(sorted([actor1, actor2]))
                pair_counts[key] = pair_counts.get(key, 0) + 1

top_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)[:10]

for pair, count in top_pairs:
    print(f"{pair}: {count} movies")

# %% Query 2: Correlation between IMDb rating and gross revenue

print("\nQuery 2: Movies with both IMDb rating and gross revenue for correlation analysis")

pipeline = [
    {"$match": {"imdb_rating": {"$ne": None}, "gross": {"$ne": None}}},
    {"$project": {
        "title": 1,
        "imdb_rating": 1,
        "gross": 1
    }},
    {"$sort": {"imdb_rating": -1}},
    {"$limit": 20}
]
for doc in collection.aggregate(pipeline):
    pprint(doc)

# %% Query 3: Recommend movies by shared genres

print("\nQuery 3: Recommend movies based on shared genres with 'The Dark Knight'")

reference_movie = collection.find_one({"title": "The Dark Knight"})
if reference_movie and reference_movie.get("genre"):
    shared_genres = reference_movie["genre"]
    
    pipeline = [
        {"$match": {
            "title": {"$ne": "The Dark Knight"},
            "genre": {"$in": shared_genres}
        }},
        {"$project": {
            "title": 1,
            "genre": 1,
            "shared_genres_count": {
                "$size": {"$setIntersection": ["$genre", shared_genres]}
            }
        }},
        {"$sort": {"shared_genres_count": -1}},
        {"$limit": 10}
    ]

    for doc in collection.aggregate(pipeline):
        pprint(doc)
else:
    print("Reference movie not found or has no genres.")

# %% Query 4: Directors with highest average gross (min 3 movies)

print("\nQuery 4: Top directors by average gross (min 3 movies)")

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

# %% Query 5: Average IMDb rating by decade

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
