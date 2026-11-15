import os
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from pprint import pprint
import csv

# %% Connecting to MongoDB Atlas

print("\nConnecting to MongoDB Atlas...")
uri = os.environ["MONGODB_URI"]
client = MongoClient(uri)

# %% Defining database and collection

db = client['movies'] 
collection = db['imdb_data']  

print("\nAvailable databases:")
try:
    pprint(client.list_database_names())
except Exception as e:
    print("Error:", e)

print("\nTarget collection: imdb_project.movies")

# %% Loading data from CSV and cleaning it

file_path = os.path.join('data', 'imdb_top_1000.csv')

documents = []

print("\nReading CSV data...")
with open(file_path, mode='r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader: 
        if not row['Series_Title']:
            continue

        # Split genres into list
        genres = [g.strip() for g in row['Genre'].split(',')] if row.get('Genre') else []

        doc = {
            "title": row['Series_Title'].strip(),
            "year": int(row['Released_Year']) if row['Released_Year'].isdigit() else None,
            "genre": genres,
            "director": row.get('Director', '').strip(),
            "stars": [row.get('Star1'), row.get('Star2'), row.get('Star3'), row.get('Star4')],
            "imdb_rating": float(row['IMDB_Rating']) if row.get('IMDB_Rating') else None,
            "gross": int(row['Gross'].replace(',', '')) if row.get('Gross') and row['Gross'].replace(',', '').isdigit() else None
        }
        documents.append(doc)

# %% Inserting into MongoDB
if documents:
    result = collection.insert_many(documents)
    print(f"\n Inserted {len(result.inserted_ids)} documents into 'movies'.")
else:
    print("\n No data")
