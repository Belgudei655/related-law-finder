from pymongo import MongoClient
import os
from dotenv import load_dotenv
import re

# Environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")


# Avoid creating the client globally
def get_db_client():
    return MongoClient(MONGO_URI, maxPoolSize=10, tls=True)


def extract_keywords(prompt):
    words = re.findall(r"\b\w+\b", prompt.lower())
    stopwords = {"би", "бол", "байна", "нь", "талаар", "бүхий"}
    return [word for word in words if word not in stopwords and len(word) > 2]


def find_related_data(prompt):
    try:
        # Create a new client for each request
        client = get_db_client()
        db = client.related_law_finder
        laws_collection = db.laws

        keywords = extract_keywords(prompt)
        if not keywords:
            return []

        search_query = " ".join(keywords)
        pipeline = [
            {
                "$search": {
                    "index": "default",
                    "text": {
                        "query": search_query,
                        "path": [
                            "title",
                            "content",
                            "sections.title",
                            "sections.articles",
                        ],
                        "fuzzy": {"maxEdits": 1},
                    },
                }
            },
            {"$addFields": {"score": {"$meta": "searchScore"}}},
            {"$sort": {"score": -1}},
            {"$limit": 10},
            {"$project": {"title": 1, "url": 1, "date": 1, "score": 1, "_id": 0}},
        ]

        results = laws_collection.aggregate(pipeline)
        return list(results)

    except Exception as e:
        print(f"Error querying the database: {e}")
        return []
