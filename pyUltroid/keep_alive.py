# pyUltroid/keep_alive.py
import os
from threading import Thread
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Ultroid is alive!"

def _run():
    port = int(os.environ.get("PORT", 8080))
    # do not use reloader (will spawn child process)
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

def start():
    t = Thread(target=_run, daemon=True)
    t.start()
