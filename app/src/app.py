import sys

from flask import Flask, request

# Custom imports
from webhook_hdr import WebhookHdr
from webhook_adm_bot_hdr import WebhookAdmHdr
from general_methods import files_gm as fgm


app = Flask(__name__)
dh = fgm.DirectoriesHandler()


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    try:
        whdr = WebhookHdr(request.json)
    except KeyboardInterrupt:
        print("Exit ...")
        sys.exit()
    except Exception as _ex:
        # TODO ??
        raise _ex
        return {"ok": False}

    return {"ok": whdr.result}


@app.route("/webhook_adm", methods=["GET", "POST"])
def webhook_adm():
    try:
        whdr = WebhookAdmHdr(request.json)
    except KeyboardInterrupt:
        print("Exit ...")
        sys.exit()
    except Exception as _ex:
        # TODO ??
        raise _ex
        return {"ok": False}

    return {"ok": whdr.result}