from fastapi import APIRouter, File, UploadFile, HTTPException
from pathlib import Path
import shutil
import tempfile
from pydub import AudioSegment
import logging

from services.vad_service import get_vad_segments, Segment as VadSegment

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Dossier temporaire pour le traitement des fichiers
TEMP_DIR = Path(tempfile.gettempdir())

def convert_to_required_wav(input_path: Path, output_path: Path) -> None:
    """
    Convertit un fichier audio/vidéo en format WAV 16kHz, 16-bit, mono.
    """
    try:
        logger.info(f"Conversion de {input_path.name} en WAV...")
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_frame_rate(16000).set_sample_width(2).set_channels(1)
        audio.export(output_path, format="wav")
        logger.info(f"Conversion réussie: {output_path.name}")
    except Exception as e:
        logger.error(f"Erreur de conversion audio: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de conversion audio: {e}")

@router.post("/vad/segment-file/", tags=["VAD"])
async def segment_file_handler(file: UploadFile = File(...)):
    """
    Accepte un fichier audio/vidéo, le segmente en utilisant VAD et retourne les timestamps.
    
    Le fichier est d'abord converti en WAV 16kHz, 16-bit, mono, qui est le format
    requis par le service VAD (webrtcvad).
    """
    input_path = TEMP_DIR / file.filename
    wav_path = TEMP_DIR / f"processed_{input_path.stem}.wav"

    try:
        # 1. Sauvegarder le fichier uploadé temporairement
        with input_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Fichier uploadé sauvegardé: {input_path}")

        # 2. Convertir le fichier au format WAV requis
        convert_to_required_wav(input_path, wav_path)

        # 3. Lancer la segmentation VAD
        segments = get_vad_segments(
            wav_path=wav_path,
            aggressiveness=3,      # Agressivité VAD (0-3)
            min_silence_ms=300,    # Silence minimum pour couper
            min_duration_ms=1000   # Durée minimale d'un segment
        )

        # 4. Retourner les segments
        return {"filename": file.filename, "segments": segments}

    except HTTPException as e:
        # Re-lever les exceptions HTTP pour que FastAPI les gère
        raise e
    except Exception as e:
        logger.error(f"Erreur inattendue dans le handler de segmentation: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne du serveur: {e}")
    finally:
        # 5. Nettoyer les fichiers temporaires
        if input_path.exists():
            input_path.unlink()
        if wav_path.exists():
            wav_path.unlink()
        logger.info("Nettoyage des fichiers temporaires terminé.")
