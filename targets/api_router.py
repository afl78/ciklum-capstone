# targets/api_router.py
import requests
from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def trigger_webhook():
    data = request.json
    # Risk: SSRF / Unvalidated URL forward from LLM payload
    target_url = data.get("destination_url")
    return requests.get(target_url).text
