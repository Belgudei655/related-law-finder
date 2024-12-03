from pymongo import MongoClient
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")


# Avoid creating the MongoClient globally for fork-safety
def get_db_client():
    return MongoClient(MONGO_URI, maxPoolSize=10, tls=True)


def extract_keywords(prompt):
    """
    Extract meaningful keywords from the user's prompt.
    """
    words = re.findall(r"\b\w+\b", prompt.lower())
    stopwords = {"би", "бол", "байна", "нь", "талаар", "бүхий"}
    return [word for word in words if word not in stopwords and len(word) > 2]


def find_related_data(prompt):
    """
    Query the MongoDB Atlas Search index to find related documents based on the user's prompt.
    """
    try:
        # Connect to the database
        client = get_db_client()
        db = client.related_law_finder
        laws_collection = db.laws

        # Extract keywords from the prompt
        keywords = extract_keywords(prompt)
        if not keywords:
            print("No keywords extracted.")
            return []

        # Construct the search query
        search_query = " ".join(keywords)
        print(f"Search Query: {search_query}")

        # Define the aggregation pipeline with Atlas Search
        pipeline = [
            {
                "$search": {
                    "index": "default",  # Use the index name you created in Atlas
                    "text": {
                        "query": search_query,
                        "path": [
                            "title",
                            "content",
                            "sections.title",
                            "sections.articles",
                        ],
                        "fuzzy": {"maxEdits": 1},  # Optional for typo tolerance
                    },
                }
            },
            {"$addFields": {"score": {"$meta": "searchScore"}}},  # Add relevance score
            {"$sort": {"score": -1}},  # Sort results by score
            {"$limit": 10},  # Limit to top 10 results
            {
                "$project": {"title": 1, "url": 1, "date": 1, "score": 1, "_id": 0}
            },  # Project specific fields
        ]

        # Execute the aggregation query
        print(f"Pipeline: {pipeline}")
        results = laws_collection.aggregate(pipeline)
        related_data = list(results)

        # Print and return the results
        print(f"Related Data: {related_data}")
        return related_data

    except Exception as e:
        print(f"Error querying the database: {e}")
        return []
