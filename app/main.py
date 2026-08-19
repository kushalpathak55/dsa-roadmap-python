from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.algorithms.registry import get_algorithm
from app.content.loader import get_topic, load_roadmap

BASE_DIR = Path(__file__).parent

app = FastAPI(title="DSA Roadmap")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")
categories, _ = load_roadmap()
templates.env.globals["nav_categories"] = categories


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"categories": categories, "current_slug": ""})


@app.get("/topic/{slug}")
def topic_page(request: Request, slug: str):
    topic = get_topic(slug)
    if topic is None:
        raise HTTPException(status_code=404, detail=f"Unknown topic '{slug}'")
    return templates.TemplateResponse(request, "topic.html", {"topic": topic, "current_slug": slug})


@app.post("/api/run/{algo_key}")
async def run_algorithm(algo_key: str, request: Request):
    algo = get_algorithm(algo_key)
    if algo is None:
        raise HTTPException(status_code=404, detail=f"Unknown algorithm '{algo_key}'")

    body = await request.json()
    try:
        payload = algo["request_model"].model_validate(body)
    except ValidationError as exc:
        errors = exc.errors(include_context=False, include_url=False)
        return JSONResponse(status_code=422, content={"detail": errors})

    result = algo["run"](payload)
    return {"algo_key": algo_key, "family": algo["family"], **result}
