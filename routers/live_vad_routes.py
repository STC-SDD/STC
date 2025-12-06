from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pathlib import Path
import asyncio
import logging

from services.vad_service import get_vad_segments_live, Segment
from services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)
router = APIRouter()

VIDEO_DIR = Path("video")

@router.websocket("/ws/vad-live/{video_filename}")
async def vad_live_simulation(websocket: WebSocket, video_filename: str):
    """
    WebSocket pour la simulation de VAD en temps réel.
    - Simule la lecture d'un fichier audio à vitesse 1x.
    - Détecte les segments de voix en direct.
    - Envoie les timestamps (start, end) dès qu'un segment est finalisé.
    - Le client reçoit les segments avec une minute d'avance sur la lecture vidéo.
    """
    await websocket_manager.connect(websocket)
    video_path = VIDEO_DIR / video_filename
    
    if not video_path.exists():
        logger.warning(f"Tentative de connexion VAD live pour un fichier inexistant: {video_filename}")
        await websocket.close(code=4004, reason=f"Video '{video_filename}' not found.")
        return

    try:
        logger.info(f"Début de la simulation VAD live pour: {video_filename}")
        
        # La fonction get_vad_segments_live est un générateur asynchrone
        # qui simule le traitement en temps réel.
        async for segment in get_vad_segments_live(
            video_path=video_path,
            aggressiveness=3,
            min_silence_ms=400,
            min_duration_ms=1000
        ):
            logger.info(f"Segment VAD détecté en direct: {segment}")
            await websocket.send_json({
                "type": "vad_segment",
                "start_time": segment.start_time,
                "end_time": segment.end_time,
                "duration": segment.duration
            })

        # Informer le client que la simulation est terminée
        await websocket.send_json({"type": "vad_end", "message": "VAD processing finished."})
        logger.info(f"Fin de la simulation VAD live pour: {video_filename}")

    except WebSocketDisconnect:
        logger.info("Client déconnecté du WebSocket VAD live.")
    except Exception as e:
        logger.error(f"Erreur durant la simulation VAD live: {e}", exc_info=True)
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        websocket_manager.disconnect(websocket)
        logger.info("Nettoyage de la connexion WebSocket VAD live.")
