from fastapi import APIRouter
import json
import os

router = APIRouter()

@router.get("/subtitles")
def get_subtitles():
    print("📌 /subtitles endpoint HIT")
    path = "data/subtitles.json"
    if not os.path.exists(path):
        print("❌ subtitles.json introuvable !")
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("📌 subtitles chargés :", data)
    return list(data.values())
