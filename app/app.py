from flask import Flask, request

# Custom imports
from webhook_hdr import WebhookHdr

app = Flask(__name__)


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    whdr = WebhookHdr(request.json)
    return {"ok": whdr.result}
