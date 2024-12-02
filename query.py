from pymongo import MongoClient
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB connection
client = MongoClient(
    MONGO_URI, maxPoolSize=50
)  # Connection pooling for better performance
db = client.related_law_finder
laws_collection = db.laws


def extract_keywords(prompt):
    """
    Extract meaningful keywords or phrases from the user prompt.
    """
    # Convert prompt to lowercase and extract words
    words = re.findall(r"\b\w+\b", prompt.lower())

    # Remove stopwords (add more as needed)
    stopwords = {"би", "бол", "байна", "нь", "талаар", "бүхий"}
    keywords = [word for word in words if word not in stopwords and len(word) > 2]
    return keywords


def find_related_data(prompt):
    try:
        # Enhanced keyword extraction
        keywords = extract_keywords(prompt)
        if not keywords:
            return []

        # Build the search query
        search_query = " ".join(keywords)

        # Use Atlas Search with fuzzy matching
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

        related_data = list(results)
        return related_data

    except Exception as e:
        print(f"Error querying the database: {e}")
        return []
