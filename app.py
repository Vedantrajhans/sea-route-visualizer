import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import searoute as sr
import os

app = Flask(__name__, static_folder="public", static_url_path="")
CORS(app)  # optional, good for dev

# Serve frontend
@app.route("/")
def index():
    return send_from_directory("public", "index.html")

# Health check
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# Calculate sea route
@app.route("/get_route", methods=["POST"])
def get_route():
    try:
        data = request.json
        origin = data.get("origin")
        dest = data.get("dest")

        if not origin or not dest:
            return jsonify({"error": "Missing origin or destination"}), 400

        def valid(c):
            return (
                isinstance(c, list)
                and len(c) == 2
                and isinstance(c[0], (int, float))
                and isinstance(c[1], (int, float))
                and -180 <= c[0] <= 180
                and -90 <= c[1] <= 90
            )

        if not valid(origin) or not valid(dest):
            return jsonify({"error": "Invalid coordinates"}), 400

        route = sr.searoute(origin, dest, units="nm")

        if not route or not route.get("geometry"):
            return jsonify({"error": "No maritime route found"}), 422

        distance = route.get("properties", {}).get("length", 0)

        return jsonify({
            "geometry": route["geometry"],
            "distance": round(distance, 1),
            "units": "nautical miles"
        })

    except Exception:
        print(traceback.format_exc())
        return jsonify({"error": "Server error"}), 500

# Optional local testing
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
