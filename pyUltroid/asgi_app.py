# pyUltroid/asgi_app.py
import os
import asyncio
import subprocess
import signal
from threading import Thread

_subproc = None
_started = False

# Simple ASGI app (no FastAPI / pydantic)
async def app(scope, receive, send):
    global _started
    if scope["type"] == "lifespan":
        while True:
            msg = await receive()
            if msg["type"] == "lifespan.startup":
                # Start subprocess once at startup
                if not _started:
                    _started = True
                    start_subprocess()
                await send({"type": "lifespan.startup.complete"})
            elif msg["type"] == "lifespan.shutdown":
                stop_subprocess()
                await send({"type": "lifespan.shutdown.complete"})
                return
    elif scope["type"] == "http":
        path = scope.get("path", "/")
        if path == "/":
            body = b'{"status":"Ultroid ASGI alive"}'
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    (b"content-type", b"application/json"),
                ],
            })
            await send({"type": "http.response.body", "body": body})
            return
        if path == "/health":
            body = b'{"ok": true}'
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    (b"content-type", b"application/json"),
                ],
            })
            await send({"type": "http.response.body", "body": body})
            return

        # 404 for everything else
        body = b'{"error":"not found"}'
        await send({
            "type": "http.response.start",
            "status": 404,
            "headers": [
                (b"content-type", b"application/json"),
            ],
        })
        await send({"type": "http.response.body", "body": body})
    else:
        # other ASGI scopes not handled
        return

def _stream_stdout(proc):
    if proc.stdout is None:
        return
    for line in proc.stdout:
        print("[ultroid subprocess]", line.rstrip())

def start_subprocess():
    global _subproc
    if _subproc is not None:
        return
    cmd = ["python", "-m", "pyUltroid"]
    env = os.environ.copy()
    # Start Ultroid subprocess
    _subproc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
        bufsize=1,
    )
    # Stream stdout in background thread (so it doesn't block event loop)
    t = Thread(target=_stream_stdout, args=(_subproc,), daemon=True)
    t.start()
    print("Started ultroid subprocess, PID:", _subproc.pid)

def stop_subprocess():
    global _subproc
    if not _subproc:
        return
    try:
        _subproc.send_signal(signal.SIGINT)
    except Exception:
        pass
    try:
        _subproc.terminate()
    except Exception:
        pass
    try:
        _subproc.wait(timeout=5)
    except Exception:
        try:
            _subproc.kill()
        except Exception:
            pass
    print("Ultroid subprocess stopped")
    _subproc = None
