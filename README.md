# IMDb Analytics on MongoDB: Document Modelling for Semi-Structured Data

Course project for *Machine Learning and Big Data* (MSc Autonomous Vehicle Engineering, University of Naples Federico II, 2025). Individual project.

## What it does
Transforms the IMDb Top 1000 dataset from a flat CSV into a **document-oriented NoSQL model** and builds an analytics layer on **MongoDB's aggregation framework**.

## Design choices
- **MongoDB over a graph database:** each title is a self-contained entity with multi-valued fields (genres, cast) that fit nested arrays, and the data has no explicit entity-to-entity relationships that would justify a graph model.
- Schema typed for the queries it serves: year as integer, genres and stars as arrays, rating as float, gross as integer, runtime parsed at query time.
- Pre-ingestion validation (many missing gross and runtime values), an idempotent load script, and normalised names with sorted pair keys to avoid duplicate counts.

## Queries
1. Most frequent actor pairings (pair combinatorics done in Python, where `$concat` fails on nulls)
2. Rating vs. gross revenue
3. Genre-overlap recommender with `$setIntersection`
4. Top directors by average gross (only directors with ≥3 films)
5. Average rating by decade

Report: [`docs/report_imdb_mongodb.pdf`](docs/report_imdb_mongodb.pdf) · Slides: [`docs/presentation_imdb_mongodb.pdf`](docs/presentation_imdb_mongodb.pdf)

## How to run
1. Download `imdb_top_1000.csv` (IMDb Movies Dataset, Kaggle) into a `data/` folder.
2. `pip install pymongo`
3. Set your own connection string as an environment variable (never commit it):
   - Windows: `set MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>/`
   - Linux/macOS: `export MONGODB_URI=...`
4. `python src/load_data.py`, then `python src/imdb_queries.py`

## Author
Sadia Kabir Dina · [LinkedIn](https://www.linkedin.com/in/sadia-kabir-dina/)
