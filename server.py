from flask import Flask, jsonify
from flask_cors import CORS
import speedtest
import logging
import threading

app = Flask(__name__)
CORS(app)
# logging.basicConfig(level=logging.DEBUG)

# Global variable to store results
speedtest_results = {"download": None}

def measure_download_speed():
    """Measures internet download speed asynchronously."""
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        download_speed = test.download() / 1_000_000  # Convert to Mbps
        speedtest_results["download"] = round(download_speed, 2)
        logging.info(f"Download speed: {speedtest_results['download']} Mbps")
    except Exception as e:
        logging.error(f"Download speed measurement failed: {e}")
        speedtest_results["download"] = "Error"

@app.route('/', methods=['GET'])
def download_speed():
    if speedtest_results["download"] is None:
        # Start the speed test in a background thread
        threading.Thread(target=measure_download_speed).start()
        return jsonify({'status': 'Speed test started, please check back later.'})
    elif speedtest_results["download"] == "Error":
        return jsonify({'error': 'Download speed measurement failed'}), 500
    else:
        return jsonify({'download': speedtest_results["download"]})

