# pyUltroid/asgi_app.py
import os
import asyncio
import signal
import subprocess
from fastapi import FastAPI

app = FastAPI()
_subproc = None

@app.get("/")
async def root():
    return {"status": "Ultroid ASGI alive"}

@app.get("/health")
async def health():
    return {"ok": True}

@app.on_event("startup")
async def startup_event():
    global _subproc
    if _subproc is not None:
        return

    cmd = ["python", "-m", "pyUltroid"]
    env = os.environ.copy()

    # start Ultroid as child process so uvicorn remains the main PID 1
    _subproc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
        bufsize=1
    )

    # stream child stdout to container logs without blocking event loop
    loop = asyncio.get_event_loop()
    def _stream():
        if _subproc.stdout is None:
            return
        for line in _subproc.stdout:
            print("[ultroid subprocess]", line.rstrip())
    loop.run_in_executor(None, _stream)

@app.on_event("shutdown")
async def shutdown_event():
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
