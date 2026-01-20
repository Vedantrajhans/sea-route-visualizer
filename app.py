import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
import searoute as sr

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/get_route', methods=['POST'])
def get_route():
    """
    Calculate sea route between two coordinates using searoute library.
    
    Expected JSON payload:
    {
        "origin": [longitude, latitude],
        "dest": [longitude, latitude]
    }
    
    Returns:
    {
        "geometry": {...},  # GeoJSON LineString geometry
        "distance": float,   # Distance in nautical miles
        "units": "nautical miles"
    }
    """
    try:
        # 1. Parse incoming data
        data = request.json
        origin = data.get('origin')
        dest = data.get('dest')

        print(f"🔹 Received Request:")
        print(f"   Origin: {origin}")
        print(f"   Destination: {dest}")

        # 2. Validate coordinates
        if not origin or not dest:
            print("❌ Error: Missing coordinates")
            return jsonify({"error": "Missing origin or destination coordinates"}), 400

        if len(origin) != 2 or len(dest) != 2:
            print("❌ Error: Invalid coordinate format")
            return jsonify({"error": "Coordinates must be [longitude, latitude]"}), 400

        # 3. Calculate sea route
        print("🔹 Calculating Sea Route...")
        
        # Use searoute library to calculate maritime route
        # units='nm' returns distance in nautical miles
        route_geojson = sr.searoute(origin, dest, units='nm')

        if not route_geojson:
            print("❌ Error: Library returned empty route")
            return jsonify({"error": "Could not calculate sea route between these coordinates"}), 500

        # 4. Extract distance from properties
        properties = route_geojson.get('properties', {})
        distance = properties.get('length', 0)
        
        print(f"✅ Success!")
        print(f"   Distance: {distance} nautical miles")
        print(f"   Coordinates in route: {len(route_geojson['geometry']['coordinates'])}")

        # 5. Return response
        return jsonify({
            "geometry": route_geojson['geometry'],
            "distance": round(distance, 1),
            "units": "nautical miles",
            "properties": properties
        })

    except Exception as e:
        print("❌ CRITICAL SERVER ERROR:")
        print(traceback.format_exc())
        return jsonify({
            "error": str(e),
            "message": "Internal server error occurred while calculating route"
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify server is running."""
    return jsonify({
        "status": "healthy",
        "message": "SeaRoute server is running",
        "version": "1.0.0"
    })


@app.route('/', methods=['GET'])
def home():
    """Root endpoint with API information."""
    return jsonify({
        "service": "SeaRoute API",
        "version": "1.0.0",
        "endpoints": {
            "/get_route": "POST - Calculate sea route between two points",
            "/health": "GET - Health check"
        },
        "usage": {
            "endpoint": "/get_route",
            "method": "POST",
            "payload": {
                "origin": "[longitude, latitude]",
                "dest": "[longitude, latitude]"
            },
            "example": {
                "origin": [103.8198, 1.2644],
                "dest": [4.4770, 51.9244]
            }
        }
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🚢 SeaRoute API Server")
    print("=" * 60)
    print("✅ Server starting on http://localhost:5000")
    print("📍 Endpoints:")
    print("   - POST /get_route  → Calculate maritime routes")
    print("   - GET  /health     → Health check")
    print("   - GET  /           → API documentation")
    print("=" * 60)
    print("💡 Make sure 'searoute' library is installed:")
    print("   pip install searoute")
    print("=" * 60)
    
    # Run the Flask application
    app.run(
        debug=True,      # Enable debug mode for development
        port=5000,       # Run on port 5000
        host='0.0.0.0'   # Allow connections from any IP
    )