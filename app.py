# app.py
import traceback
from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
import searoute as sr

load_dotenv()  # For local .env file

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           mapbox_token=os.getenv('MAPBOX_TOKEN'),
                           owm_key=os.getenv('OWM_KEY'))

@app.route('/get_route', methods=['POST'])
def get_route():
    try:
        data = request.json
        origin = data.get('origin')
        dest = data.get('dest')

        if not origin or not dest:
            return jsonify({"error": "Missing coordinates"}), 400

        route_geojson = sr.searoute(origin, dest, units="naut")

        geometry = route_geojson['geometry']
        properties = route_geojson['properties']
        distance = properties.get('length', 0)

        return jsonify({
            "geometry": geometry,
            "distance": distance,
            "units": "nautical miles"
        })

    except Exception as e:
        print("Server Error:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)