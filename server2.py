from flask import Flask, jsonify
from flask_cors import CORS
import speedtest
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
