from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/")
def serve_subtitler_page():
    with open("static/subtitler.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())
