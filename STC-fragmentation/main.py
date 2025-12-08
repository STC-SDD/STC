from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers.init_routes import init_routes
from services.fragment_assigner import initialize_fragments
from services.vad_service import run_live_vad_simulation_and_print
from pathlib import Path
import asyncio

app = FastAPI()
app.mount("/video", StaticFiles(directory="video"), name="video")

# Initialise l'état des fragments au démarrage
@app.on_event("startup")
async def startup_event():
    initialize_fragments()
    
    # Lance la simulation VAD en tâche de fond
    video_path = Path("video/sous_titrage.mp4")
    asyncio.create_task(run_live_vad_simulation_and_print(video_path))

# Charger toutes les routes
init_routes(app)
