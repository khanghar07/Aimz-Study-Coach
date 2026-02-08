import os
from typing import List

from dotenv import load_dotenv
import time
import uuid

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .gemini_client import analyze_study_material, answer_question
from .processors import build_parts_from_files
from .exports import to_markdown, to_pdf_bytes

load_dotenv()

app = FastAPI(title="Gemini Study Coach")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

SHARE_TTL_SECONDS = 24 * 3600
SHARE_STORE = {}


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
async def analyze(
    request: Request,
    files: List[UploadFile] = File(default=[]),
    goal: str = Form(default="Help me study this material for an upcoming test."),
    level: str = Form(default="Undergraduate"),
    time_budget: str = Form(default="30 minutes"),
):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return JSONResponse({"error": "GEMINI_API_KEY is not set."}, status_code=400)

    parts, stats = await build_parts_from_files(files)
    if not parts:
        return JSONResponse({"error": "No usable content found. Upload images or PDFs."}, status_code=400)

    result = analyze_study_material(
        api_key=api_key,
        goal=goal,
        level=level,
        time_budget=time_budget,
        parts=parts,
        stats=stats,
    )
    return JSONResponse(result)


@app.post("/ask")
async def ask(payload: dict):
    api_key = os.getenv("ASK_GEMINI_API_KEY", "").strip() or os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return JSONResponse({"error": "GEMINI_API_KEY is not set."}, status_code=400)

    question = (payload.get("question") or "").strip()
    analysis = payload.get("analysis") or {}
    if not question:
        return JSONResponse({"error": "Question is required."}, status_code=400)

    result = answer_question(api_key=api_key, question=question, analysis=analysis)
    return JSONResponse(result)


@app.post("/export/markdown")
async def export_markdown(payload: dict):
    md = to_markdown(payload)
    return Response(md, media_type="text/markdown")


@app.post("/export/pdf")
async def export_pdf(payload: dict):
    pdf_bytes = to_pdf_bytes(payload)
    if not pdf_bytes:
        return JSONResponse({"error": "PDF generation failed."}, status_code=500)
    headers = {"Content-Disposition": "attachment; filename=study-coach-report.pdf"}
    return Response(pdf_bytes, media_type="application/pdf", headers=headers)


def _cleanup_share_store():
    now = time.time()
    expired = [k for k, v in SHARE_STORE.items() if now - v["ts"] > SHARE_TTL_SECONDS]
    for k in expired:
        SHARE_STORE.pop(k, None)


@app.post("/share")
async def share(payload: dict, request: Request):
    _cleanup_share_store()
    sid = uuid.uuid4().hex[:8]
    SHARE_STORE[sid] = {"ts": time.time(), "data": payload}
    url = str(request.base_url) + f"share/{sid}"
    return JSONResponse({"id": sid, "url": url})


@app.get("/share/{sid}", response_class=HTMLResponse)
async def share_view(sid: str, request: Request):
    _cleanup_share_store()
    item = SHARE_STORE.get(sid)
    if not item:
        return templates.TemplateResponse(
            "share.html", {"request": request, "data": None, "sid": sid}
        )
    return templates.TemplateResponse(
        "share.html", {"request": request, "data": item["data"], "sid": sid}
    )
