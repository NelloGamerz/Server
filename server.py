from flask import Flask, jsonify, request
from flask_cors import CORS
import speedtest
import logging
import threading

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Global variable to store results
speedtest_results = {"download": None, "server": None}

def measure_download_speed():
    """Measures internet download speed asynchronously."""
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        server_info = test.results.server["host"]

        # Measure download speed
        download_speed = test.download(threads=1) / 1_000_000  # Convert to Mbps
        speedtest_results["download"] = round(download_speed, 2)
        speedtest_results["server"] = server_info

        logging.info(f"Download speed: {speedtest_results['download']} Mbps, Server: {server_info}")
    except Exception as e:
        logging.error(f"Download speed measurement failed: {e}")
        speedtest_results["download"] = "Error"
        speedtest_results["server"] = "N/A"

@app.route("/", methods=["GET"])
def download_speed():
    user_ip = request.remote_addr
    logging.info(f"User IP: {user_ip}")

    if speedtest_results["download"] is None:
        # Start the speed test in a background thread
        threading.Thread(target=measure_download_speed).start()
        return jsonify({'status': 'Speed test started, please check back later.'})
    elif speedtest_results["download"] == "Error":
        return jsonify({'error': 'Download speed measurement failed'}), 500
    else:
        # Prepare the result and reset the global variable for the next request
        response = {
            'download': speedtest_results["download"],
            'server': speedtest_results["server"]
        }
        speedtest_results["download"] = None
        speedtest_results["server"] = None
        return jsonify(response)
