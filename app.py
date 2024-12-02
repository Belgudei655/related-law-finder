from flask import Flask, request, jsonify
from query import find_related_data
import os

app = Flask(__name__)


@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Find related data based on the user's prompt
    related_data = find_related_data(prompt)

    # Limit the results to the top 5 most relevant entries
    return jsonify({"related_data": related_data[:5]})


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
