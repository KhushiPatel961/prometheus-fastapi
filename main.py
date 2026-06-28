import time
import uuid
import json
from collections import deque

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

START_TIME = time.time()

logs = deque(maxlen=1000)

REQUEST_COUNTER = Counter(
    "http_requests_total",
    "Total HTTP requests"
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())

    response = await call_next(request)

    REQUEST_COUNTER.inc()

    logs.append({
        "level": "INFO",
        "ts": time.time(),
        "path": request.url.path,
        "request_id": request_id
    })

    response.headers["X-Request-ID"] = request_id

    return response


@app.get("/work")
def work(n: int):
    x = 0
    for i in range(n):
        x += i

    return {
        "email": "22f3001561@ds.study.iitm.ac.in",
        "done": n
    }


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "uptime_s": time.time() - START_TIME
    }


@app.get("/logs/tail")
def tail(limit: int = 10):
    return list(logs)[-limit:]


@app.get("/metrics")
def metrics():
    return PlainTextResponse(
        generate_latest().decode(),
        media_type=CONTENT_TYPE_LATEST,
    )
