from fastapi import APIRouter
import json
import os

router = APIRouter()

@router.get("/subtitles")
def get_subtitles():
    path = "data/subtitles.json"   # path to the file
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
