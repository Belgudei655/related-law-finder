from flask import Flask, request, jsonify
from query import find_related_data
import json

app = Flask(__name__)

# Load data once at startup
with open("data.json", encoding="utf-8") as file:
    data = json.load(file)


@app.route("/search", methods=["POST"])
def search():
    request_data = request.get_json()
    prompt = request_data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Find related data
    related_data = find_related_data(prompt, data)

    return jsonify({"related_data": related_data})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
