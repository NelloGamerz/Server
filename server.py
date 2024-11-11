from flask import Flask, jsonify
from flask_cors import CORS
import speedtest
import logging
import os
from logging.handlers import RotatingFileHandler
import threading

# Set up Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load environment-based configurations
app.config.from_object(os.environ.get('FLASK_CONFIG', 'config.DevelopmentConfig'))

# Configure logging
if not app.debug:  # Production logging setup
    log_handler = RotatingFileHandler('app.log', maxBytes=10 * 1024 * 1024, backupCount=3)
    log_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(formatter)
    app.logger.addHandler(log_handler)
else:  # Development logging setup
    app.logger.setLevel(logging.DEBUG)

def measure_download_speed():
    """Measures internet download speed."""
    try:
        test = speedtest.Speedtest()
        test.get_best_server()  # Select the best server based on latency
        download_speed = test.download() / 1_000_000  # Convert to Mbps
        return download_speed
    except Exception as e:
        app.logger.error(f"Download speed measurement failed: {e}")
        raise

def measure_upload_ping():
    """Measures internet upload speed and ping."""
    try:
        test = speedtest.Speedtest()
        test.get_best_server()  # Select the best server based on latency
        upload_speed = test.upload() / 1_000_000  # Convert to Mbps
        ping = test.results.ping  # Ping in milliseconds
        return upload_speed, ping
    except Exception as e:
        app.logger.error(f"Upload/Ping measurement failed: {e}")
        raise

@app.route('/api/speedtest/download', methods=['GET'])
def download_speed():
    """Endpoint for downloading speed."""
    try:
        download_speed_mbps = measure_download_speed()
        return jsonify({'download': download_speed_mbps})
    except Exception as e:
        app.logger.error("Download speed measurement failed:", exc_info=e)
        return jsonify({'error': 'Download speed measurement failed'}), 500

@app.route("/api/speedtest/upload_ping", methods=["GET"])
def upload_ping():
    """Endpoint for upload speed and ping."""
    try:
        upload_speed, ping = measure_upload_ping()
        return jsonify({"upload": upload_speed, "ping": ping})
    except Exception as e:
        app.logger.error(f"Error in /api/speedtest/upload_ping: {e}")
        return jsonify({"error": "Failed to measure upload speed and ping"}), 500

# Run the app using Gunicorn for production (or use `flask run` in development)
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)  # Ensure it's bound to all IPs for production use
