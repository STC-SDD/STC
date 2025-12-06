#!/usr/bin/env python3
"""
Module de segmentation audio intelligent pour le projet STC, utilisant WebRTC VAD.
"""

import wave
import logging
import webrtcvad
from pathlib import Path
from dataclasses import dataclass
from typing import Iterator, Tuple, List

# --- Configuration du Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# --- Constantes Audio ---
SAMPLE_RATE = 16000
SAMPLE_WIDTH = 2  # 16-bit
CHANNELS = 1
CHUNK_DURATION_MS = 20
CHUNK_BYTES = int((SAMPLE_RATE / 1000) * CHUNK_DURATION_MS * SAMPLE_WIDTH * CHANNELS)
BYTES_PER_SECOND = SAMPLE_RATE * SAMPLE_WIDTH * CHANNELS

@dataclass
class Segment:
    """Représente un segment audio avec uniquement des timestamps."""
    start_time: float
    end_time: float

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

    def __repr__(self):
        return f"Segment(start={self.start_time:.2f}s, end={self.end_time:.2f}s, duration={self.duration:.2f}s)"

class AudioStreamProcessor:
    """Gère la lecture d'un fichier WAV."""
    
    def __init__(self, wav_path: Path):
        self.wav_path = wav_path
        self._validate_file()

    def _validate_file(self):
        if not self.wav_path.exists():
            raise FileNotFoundError(f"Fichier audio introuvable: {self.wav_path}")
        try:
            with wave.open(str(self.wav_path), 'rb') as wf:
                if (wf.getframerate() != SAMPLE_RATE or
                    wf.getsampwidth() != SAMPLE_WIDTH or
                    wf.getnchannels() != CHANNELS):
                    raise ValueError(f"Format WAV invalide. Requis: {SAMPLE_RATE}Hz, Mono, 16-bit.")
        except wave.Error as e:
            raise ValueError(f"Fichier WAV corrompu ou invalide: {e}")

    def stream(self) -> Iterator[Tuple[bytes, float]]:
        """Générateur qui lit le fichier audio par chunks."""
        with wave.open(str(self.wav_path), 'rb') as wf:
            current_time = 0.0
            while True:
                chunk = wf.readframes(CHUNK_BYTES // SAMPLE_WIDTH)
                if not chunk:
                    break
                # Le dernier chunk peut être plus petit, on le gère
                if len(chunk) < CHUNK_BYTES:
                    # On pad avec du silence si nécessaire pour que webrtcvad l'accepte
                    chunk += b'\x00' * (CHUNK_BYTES - len(chunk))
                
                yield chunk, current_time
                current_time += CHUNK_DURATION_MS / 1000.0

class VadSegmenter:
    """Implémente la logique de segmentation VAD."""
    STATE_SILENCE = 0
    STATE_SPEECH = 1

    def __init__(self, aggressiveness: int, min_silence_ms: int, min_duration_ms: int):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.min_silence_chunks = max(1, min_silence_ms // CHUNK_DURATION_MS)
        self.min_duration_bytes_equivalent = int((min_duration_ms / 1000.0) * BYTES_PER_SECOND)
        
        self.state = self.STATE_SILENCE
        self.buffer = bytearray()
        self.buffer_start_time = 0.0
        self.silence_counter = 0
        
        logger.info(f"VAD Init | Agressivité: {aggressiveness} | "
                    f"Silence min: {min_silence_ms}ms | "
                    f"Durée segment min: {min_duration_ms}ms")

    def process(self, chunk: bytes, timestamp: float) -> Iterator[Segment]:
        """Traite un chunk audio et retourne un Segment si une coupure est décidée."""
        try:
            is_speech = self.vad.is_speech(chunk, SAMPLE_RATE)
        except Exception:
            is_speech = False

        if self.state == self.STATE_SILENCE:
            if is_speech:
                self.state = self.STATE_SPEECH
                self.buffer_start_time = timestamp
                self.buffer.extend(chunk)
                self.silence_counter = 0
        
        elif self.state == self.STATE_SPEECH:
            self.buffer.extend(chunk)

            if not is_speech:
                self.silence_counter += 1
            else:
                self.silence_counter = 0

            buffer_duration_bytes = len(self.buffer)
            is_silence_trigger = self.silence_counter >= self.min_silence_chunks
            is_duration_met = buffer_duration_bytes >= self.min_duration_bytes_equivalent

            if is_silence_trigger and is_duration_met:
                segment_end_time = timestamp + (CHUNK_DURATION_MS / 1000.0)
                
                yield Segment(self.buffer_start_time, segment_end_time)
                
                self.buffer = bytearray()
                self.state = self.STATE_SILENCE
                self.silence_counter = 0

    def flush(self) -> Iterator[Segment]:
        """Force la coupure du segment restant en fin de flux."""
        if self.buffer:
            end_timestamp = self.buffer_start_time + (len(self.buffer) / BYTES_PER_SECOND)
            yield Segment(self.buffer_start_time, end_timestamp)
            self.buffer = bytearray()

def get_vad_segments(
    wav_path: Path, 
    aggressiveness: int = 3, 
    min_silence_ms: int = 500, 
    min_duration_ms: int = 1000
) -> List[Segment]:
    """
    Fonction principale pour segmenter un fichier WAV et retourner les timestamps.
    """
    processor = AudioStreamProcessor(wav_path)
    segmenter = VadSegmenter(aggressiveness, min_silence_ms, min_duration_ms)
    
    segments: List[Segment] = []
    
    logger.info(f"Démarrage de la segmentation VAD pour {wav_path.name}...")
    
    for chunk, timestamp in processor.stream():
        for seg in segmenter.process(chunk, timestamp):
            segments.append(seg)
            logger.info(f" -> Nouveau segment détecté: {seg}")

    for seg in segmenter.flush():
        segments.append(seg)
        logger.info(f" -> Segment final (flush): {seg}")

    logger.info(f"Segmentation terminée. {len(segments)} segments trouvés.")
    return segments

async def get_vad_segments_live(
    video_path: Path,
    aggressiveness: int,
    min_silence_ms: int,
    min_duration_ms: int
):
    """
    Générateur asynchrone qui simule la segmentation VAD en temps réel (1x)
    à partir d'un fichier vidéo/audio en utilisant ffmpeg (sans pydub/pyaudioop).
    """
    import asyncio
    import subprocess

    if not video_path.exists():
        raise FileNotFoundError(f"Fichier vidéo introuvable: {video_path}")

    # Lancer ffmpeg pour convertir en PCM 16-bit mono 16kHz, streamé sur stdout
    # -nostdin pour éviter les blocages, -loglevel error pour propre sortie
    cmd = [
        "ffmpeg",
        "-nostdin",
        "-hide_banner",
        "-loglevel", "error",
        "-i", str(video_path),
        "-f", "s16le",      # PCM 16-bit little-endian
        "-ac", "1",          # mono
        "-ar", str(SAMPLE_RATE),  # 16000 Hz
        "-"                   # sortie sur stdout
    ]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except FileNotFoundError:
        # ffmpeg non installé ou non trouvé dans PATH
        raise RuntimeError("ffmpeg introuvable. Veuillez l'installer et vérifier le PATH.")

    segmenter = VadSegmenter(aggressiveness, min_silence_ms, min_duration_ms)
    current_time = 0.0

    try:
        while True:
            chunk = proc.stdout.read(CHUNK_BYTES)
            if not chunk:
                break

            # Si chunk incomplet (fin de flux), pad avec silence
            if len(chunk) < CHUNK_BYTES:
                chunk = chunk + (b"\x00" * (CHUNK_BYTES - len(chunk)))

            for seg in segmenter.process(chunk, current_time):
                yield seg

            # Simuler la lecture temps réel
            await asyncio.sleep(CHUNK_DURATION_MS / 1000.0)
            current_time += CHUNK_DURATION_MS / 1000.0

    finally:
        # Récupérer et logguer les erreurs ffmpeg éventuelles
        if proc.stderr:
            err = proc.stderr.read().decode(errors="ignore")
            if err:
                logger.debug(f"ffmpeg stderr: {err}")
        proc.stdout and proc.stdout.close()
        proc.stderr and proc.stderr.close()
        proc.wait()

    # Flush final pour émettre le dernier segment
    for seg in segmenter.flush():
        yield seg

async def run_live_vad_simulation_and_print(video_path: Path):
    """
    Lance la simulation VAD en direct pour un fichier vidéo et écrit
    les fragments détectés dans `data/fragments.json` au format:

    [
        {"id": "frag1", "start": <float>, "end": <float>},
        {"id": "frag2", "start": <float>, "end": <float>},
        ...
    ]
    """
    import json
    from pathlib import Path as _Path

    output_dir = _Path("data")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "fragments.json"

    # Initialise la liste de fragments au format demandé
    fragments_list = []
    try:
        # Fichier initial vide (tableau JSON)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(fragments_list, f, ensure_ascii=False, indent=2)

        # Utilise le générateur asynchrone pour obtenir les segments en direct
        async for segment in get_vad_segments_live(
            video_path=video_path,
            aggressiveness=3,
            min_silence_ms=400,
            min_duration_ms=10000
        ):
            # Ajouter le fragment (id incrémental) et réécrire le fichier pour refléter l'état live
            frag_id = f"frag{len(fragments_list) + 1}"
            fragments_list.append({
                "id": frag_id,
                "start": segment.start_time,
                "end": segment.end_time
            })
            # Écrire de façon atomique pour éviter les lectures partielles
            tmp_path = output_path.with_suffix(".tmp")
            with tmp_path.open("w", encoding="utf-8") as f:
                json.dump(fragments_list, f, ensure_ascii=False, indent=2)
            tmp_path.replace(output_path)

        # Écriture finale (utile si flush ajoute quelque chose)
        tmp_path = output_path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(fragments_list, f, ensure_ascii=False, indent=2)
        tmp_path.replace(output_path)

    except FileNotFoundError:
        logger.error(f"Fichier vidéo introuvable: {video_path}")
    except Exception as e:
        logger.error(f"Erreur durant la simulation VAD: {e}")
