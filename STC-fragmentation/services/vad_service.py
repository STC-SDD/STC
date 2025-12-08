#!/usr/bin/env python3
"""
Module de segmentation audio (VAD) pour STC
"""

import wave
import logging
import webrtcvad
from pathlib import Path
from dataclasses import dataclass
from typing import Iterator, Tuple, List
import asyncio
import subprocess
import json
from services.json_loader import save_json

# Instance WebSocket globale
from services.websocket_manager import websocket_manager

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- Constantes audio ---
SAMPLE_RATE = 16000
SAMPLE_WIDTH = 2
CHANNELS = 1
CHUNK_DURATION_MS = 20
CHUNK_BYTES = int((SAMPLE_RATE / 1000) * CHUNK_DURATION_MS * SAMPLE_WIDTH * CHANNELS)
BYTES_PER_SECOND = SAMPLE_RATE * SAMPLE_WIDTH * CHANNELS


# ------------------------------
# DATACLASS Segment
# ------------------------------
@dataclass
class Segment:
    start_time: float
    end_time: float

    @property
    def duration(self):
        return self.end_time - self.start_time


# ------------------------------
# AUDIO PROCESSOR
# ------------------------------
class AudioStreamProcessor:
    def __init__(self, wav_path: Path):
        self.wav_path = wav_path
        self._validate_file()

    def _validate_file(self):
        if not self.wav_path.exists():
            raise FileNotFoundError(f"Audio file not found: {self.wav_path}")
        with wave.open(str(self.wav_path), "rb") as wf:
            if (wf.getframerate() != SAMPLE_RATE or
                wf.getsampwidth() != SAMPLE_WIDTH or
                wf.getnchannels() != CHANNELS):
                raise ValueError("Invalid WAV format")

    def stream(self):
        with wave.open(str(self.wav_path), "rb") as wf:
            current_time = 0.0
            while True:
                chunk = wf.readframes(CHUNK_BYTES // SAMPLE_WIDTH)
                if not chunk:
                    break
                if len(chunk) < CHUNK_BYTES:
                    chunk += b"\x00" * (CHUNK_BYTES - len(chunk))

                yield chunk, current_time
                current_time += CHUNK_DURATION_MS / 1000.0


# ------------------------------
# VAD SEGMENTER
# ------------------------------
class VadSegmenter:
    STATE_SILENCE = 0
    STATE_SPEECH = 1

    def __init__(self, aggressiveness, min_silence_ms, min_duration_ms):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.min_silence_chunks = max(1, min_silence_ms // CHUNK_DURATION_MS)
        self.min_duration_bytes = int((min_duration_ms / 1000.0) * BYTES_PER_SECOND)
        self.state = self.STATE_SILENCE
        self.buffer = bytearray()
        self.buffer_start_time = 0.0
        self.silence_counter = 0

    def process(self, chunk, timestamp):
        try:
            is_speech = self.vad.is_speech(chunk, SAMPLE_RATE)
        except Exception:
            is_speech = False

        if self.state == self.STATE_SILENCE:
            if is_speech:
                self.state = self.STATE_SPEECH
                self.buffer_start_time = timestamp
                self.buffer.extend(chunk)
        else:
            self.buffer.extend(chunk)
            if not is_speech:
                self.silence_counter += 1
            else:
                self.silence_counter = 0

            long_enough = len(self.buffer) >= self.min_duration_bytes
            silence_long = self.silence_counter >= self.min_silence_chunks

            if silence_long and long_enough:
                end = timestamp + (CHUNK_DURATION_MS / 1000.0)
                yield Segment(self.buffer_start_time, end)
                self.state = self.STATE_SILENCE
                self.buffer = bytearray()
                self.silence_counter = 0

    def flush(self):
        if self.buffer:
            end = self.buffer_start_time + len(self.buffer) / BYTES_PER_SECOND
            yield Segment(self.buffer_start_time, end)


# ------------------------------
# LIVE VAD via FFMPEG  (🔥 REQUIRED FUNCTION)
# ------------------------------
async def get_vad_segments_live(video_path: Path, aggressiveness, min_silence_ms, min_duration_ms):
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    cmd = [
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
        "-i", str(video_path),
        "-f", "s16le",
        "-ac", "1",
        "-ar", str(SAMPLE_RATE),
        "-"
    ]

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        raise RuntimeError("FFmpeg missing or not in PATH")

    segmenter = VadSegmenter(aggressiveness, min_silence_ms, min_duration_ms)
    current_time = 0.0

    while True:
        chunk = proc.stdout.read(CHUNK_BYTES)
        if not chunk:
            break
        if len(chunk) < CHUNK_BYTES:
            chunk += b"\x00" * (CHUNK_BYTES - len(chunk))

        for seg in segmenter.process(chunk, current_time):
            yield seg

        await asyncio.sleep(CHUNK_DURATION_MS / 1000.0)
        current_time += CHUNK_DURATION_MS / 1000.0

    for seg in segmenter.flush():
        yield seg


# ------------------------------
# LIVE VAD + JSON + BROADCAST 🔥
# ------------------------------
print("[RESET] Réinitialisation de fragments_state.json et roundrobin.json")
save_json("data/fragments_state.json", {})
save_json("data/roundrobin.json", {"order": [], "index": 0})
async def run_live_vad_simulation_and_print(video_path: Path):
    output_path = Path("data/fragments.json")
    fragments_list = []

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(fragments_list, f, indent=2)

    async for segment in get_vad_segments_live(
        video_path,
        aggressiveness=3,
        min_silence_ms=400,
        min_duration_ms=10000
    ):
        frag_id = f"frag{len(fragments_list) + 1}"

        fragments_list.append({
            "id": frag_id,
            "start": segment.start_time,
            "end": segment.end_time
        })

        tmp = output_path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(fragments_list, f, indent=2)
        tmp.replace(output_path)

        logger.info(f"[VAD] Nouveau fragment : {frag_id}")

        #  Prévenir les sous-titreurs
        await websocket_manager.broadcast("NEW_FRAGMENT_AVAILABLE")

    # Final flush
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(fragments_list, f, indent=2)
