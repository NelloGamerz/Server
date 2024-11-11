from flask import Flask, jsonify
from flask_cors import CORS
import speedtest
import logging
from logging.handlers import RotatingFileHandler
import os
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Flask environment config
app.config['FLASK_ENV'] = os.environ.get('FLASK_ENV', 'production')

# Configure logging
if not app.debug:
    log_handler = RotatingFileHandler('app.log', maxBytes=10 * 1024 * 1024, backupCount=3)
    log_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(formatter)
    app.logger.addHandler(log_handler)
else:
    app.logger.setLevel(logging.DEBUG)

def measure_download_speed():
    """Measures internet download speed."""
    try:
        test = speedtest.Speedtest()
        test.get_best_server()  # Select the best server based on latency
        download_speed = test.download() / 1_000_000  # Convert to Mbps
        return download_speed
    except Exception as e:
        logging.error(f"Download speed measurement failed: {e}")
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
        logging.error(f"Upload/Ping measurement failed: {e}")
        raise

@app.route('/api/speedtest/download', methods=['GET'])
def download_speed():
    try:
        download_speed_mbps = measure_download_speed()
        return jsonify({'download': download_speed_mbps})
    except Exception as e:
        logging.error("Download speed measurement failed:", exc_info=e)
        return jsonify({'error': 'Download speed measurement failed'}), 500

@app.route("/api/speedtest/upload_ping", methods=["GET"])
def upload_ping():
    try:
        upload_speed, ping = measure_upload_ping()
        return jsonify({"upload": upload_speed, "ping": ping})
    except Exception as e:
        logging.error(f"Error in /api/speedtest/upload_ping: {e}")
        return jsonify({"error": "Failed to measure upload speed and ping"}), 500

@app.route('/api/speedtest', methods=['GET'])
def speedtest_endpoint():
    result = None

    # Run speedtest in background thread
    def speedtest_thread():
        nonlocal result
        try:
            download_speed_mbps = measure_download_speed()
            upload_speed, ping = measure_upload_ping()
            result = {'download': download_speed_mbps, 'upload': upload_speed, 'ping': ping}
        except Exception as e:
            logging.error(f"Error in speedtest: {e}")
            result = {'error': 'Speedtest failed'}

    thread = threading.Thread(target=speedtest_thread)
    thread.start()
    thread.join()  # Wait for the thread to finish before returning response

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
