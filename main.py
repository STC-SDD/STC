from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers.init_routes import init_routes
from services.fragment_assigner import initialize_fragments

app = FastAPI()
app.mount("/video", StaticFiles(directory="video"), name="video")

# Initialise l'état des fragments au démarrage
@app.on_event("startup")
async def startup_event():
    initialize_fragments()

# Charger toutes les routes
init_routes(app)
