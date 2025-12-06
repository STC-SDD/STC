from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/")
def serve_subtitler_page():
    """Serve the subtitler interface at root.
    Subtitler plays the video immediately (with autoplay fallback).
    """
    with open("static/subtitler.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@router.get("/viewer")
def serve_viewer_page():
    """Serve the viewer interface.
    Viewer waits 30 seconds after load before starting playback.
    """
    with open("static/viewer.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())
