from functools import wraps
from flask import request, jsonify, current_app

def bearer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # The app context is now guaranteed to be available here
        expected_token = current_app.config.get('BEARER_TOKEN')

        if not expected_token:
            # This error will now correctly report if the server config is missing
            return jsonify({"error": "BEARER_TOKEN is not configured on the server."}), 500

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization header is missing"}), 401

        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return jsonify({"error": "Authorization header must be in 'Bearer <token>' format"}), 401
        
        token = parts[1]

        if token != expected_token:
            return jsonify({"error": "Invalid or expired token"}), 403

        return f(*args, **kwargs)
    return decorated_function 