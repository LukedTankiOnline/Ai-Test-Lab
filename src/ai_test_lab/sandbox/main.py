import uuid
import time
import json
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx

from ..storage import Storage
from ..analysis.risk import batch_analyze_logs, analyze_text_risk
from ..client import send_prompt

app = FastAPI(title="AI Test Lab Sandbox")
templates = Jinja2Templates(directory="templates")
app.mount("/artifacts", StaticFiles(directory="artifacts"), name="artifacts")

storage = Storage()


@app.post("/api/send_prompt")
async def api_send_prompt(request: Request):
    body = await request.json()
    model = body.get("model", "simulated")
    prompt = body.get("prompt", "")
    session_id = body.get("session_id") or str(uuid.uuid4())
    start = time.time()
    result = send_prompt(prompt, model=model)
    latency = result.get("latency_ms", (time.time() - start) * 1000.0)
    storage.insert_log(session_id=session_id, model=model, prompt=prompt, response=result.get("response",""),
                       tokens_in=result.get("tokens_in",0), tokens_out=result.get("tokens_out",0),
                       latency_ms=latency, metadata=result.get("meta"))
    return JSONResponse({"session_id": session_id, **result})


@app.get("/")
async def root():
    # Redirect root to the dashboard for convenience when deployed at domain root
    return RedirectResponse(url="/dashboard")


@app.get("/favicon.ico")
async def favicon():
    # Return no content for favicon requests (avoid 404 noise). Replace with a real icon if desired.
    return Response(status_code=204)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    logs = storage.query_logs(200)
    return templates.TemplateResponse("dashboard.html", {"request": request, "logs": logs})


@app.post("/replay")
async def replay(session_id: str = Form(...)):
    # replay logs from a session
    logs = [l for l in storage.query_logs(1000) if l.get("session_id") == session_id]
    for l in reversed(logs):
        # naive replay: send again
        await httpx.post("http://localhost:8000/api/send_prompt", json={"model": l.get("model"), "prompt": l.get("prompt"), "session_id": session_id})
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/api/logs")
async def get_logs(limit: int = 100):
    logs = storage.query_logs(limit)
    # annotate with risk for quick consumption
    annotated = batch_analyze_logs(logs)
    return JSONResponse(annotated)


@app.get("/api/export_report")
async def export_report(limit: int = 100):
    logs = storage.query_logs(limit)
    annotated = batch_analyze_logs(logs)
    # simple JSON report
    return JSONResponse({"count": len(annotated), "logs": annotated})
