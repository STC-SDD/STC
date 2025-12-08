from typing import Dict, Optional
from datetime import datetime
import asyncio
import os
import random
import csv  # NEW

from fastapi import WebSocket
from pydantic import BaseModel

# Ensure directories exist (as in your original code)
os.makedirs("uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("data", exist_ok=True)  # for users.csv


class Subtitler(BaseModel):
    id: str
    name: str
    assigned: int
    completed: int
    active: bool
    accuracy: float
    avg_time: float
    last_activity: str


class VideoInfo(BaseModel):
    filename: str
    upload_time: str
    size: int
    url: str


class ConnectedUser(BaseModel):
    username: str
    connected_at: str
    status: str  # "online", "offline"
    last_seen: str
    typing_status: str  # "idle", "typing"
    current_text: str


subtitlers_db: Dict[str, Subtitler] = {
    "sub_001": Subtitler(
        id="sub_001",
        name="Alice Martin",
        assigned=25,
        completed=18,
        active=True,
        accuracy=95.5,
        avg_time=12.3,
        last_activity="2 min ago",
    ),
    "sub_002": Subtitler(
        id="sub_002",
        name="Bob Durant",
        assigned=30,
        completed=25,
        active=True,
        accuracy=92.8,
        avg_time=15.1,
        last_activity="1 min ago",
    ),
    "sub_003": Subtitler(
        id="sub_003",
        name="Claire Dubois",
        assigned=20,
        completed=12,
        active=False,
        accuracy=88.2,
        avg_time=18.5,
        last_activity="10 min ago",
    ),
    "sub_004": Subtitler(
        id="sub_004",
        name="David Benali",
        assigned=15,
        completed=8,
        active=True,
        accuracy=97.2,
        avg_time=10.8,
        last_activity="30 sec ago",
    ),
}

# Shared runtime state (moved from your original file)
active_websockets: Dict[str, WebSocket] = {}  # username -> websocket
connected_users: Dict[str, ConnectedUser] = {}  # username -> user info
current_video: Optional[VideoInfo] = None

# Throttling control for admin updates
pending_broadcast: bool = False

# ---------- CSV credentials ----------

USERS_CSV_PATH = os.path.join("data", "users.csv")


def load_user_credentials() -> Dict[str, str]:
    """
    Load username/password pairs from data/users.csv.

    Expected CSV format (with header row):
        username,password
        alice,secret123
        bob,anotherpass
    """
    creds: Dict[str, str] = {}
    if not os.path.exists(USERS_CSV_PATH):
        return creds

    with open(USERS_CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Requires columns "username" and "password"
        for row in reader:
            u = (row.get("username") or "").strip()
            p = (row.get("password") or "").strip()
            if u and p:
                creds[u] = p
    return creds


# ---------- metrics helpers ----------


def get_summary():
    total = len(subtitlers_db)
    active = sum(1 for s in subtitlers_db.values() if s.active)
    total_seg = sum(s.assigned for s in subtitlers_db.values())
    completed_seg = sum(s.completed for s in subtitlers_db.values())
    completion = round((completed_seg / total_seg * 100) if total_seg > 0 else 0, 1)
    avg_acc = round(
        sum(s.accuracy for s in subtitlers_db.values()) / total if total > 0 else 0, 1
    )
    return {
        "total": total,
        "active": active,
        "completion": completion,
        "accuracy": avg_acc,
    }


def get_user_stats():
    total = len(connected_users)
    active = sum(1 for u in connected_users.values() if u.status == "online")
    typing = sum(
        1
        for u in connected_users.values()
        if u.typing_status == "typing" and u.status == "online"
    )
    with_text = sum(
        1
        for u in connected_users.values()
        if u.current_text and len(u.current_text.strip()) > 0
    )

    return {
        "total": total,
        "active": active,
        "typing": typing,
        "with_text": with_text,
    }


async def broadcast_user_update():
    """
    Throttled broadcast for user updates (typing/save/offline) to admin.
    """
    global pending_broadcast

    if pending_broadcast:
        return

    pending_broadcast = True
    await asyncio.sleep(0.15)
    pending_broadcast = False

    if "admin" in active_websockets:
        data = {
            "subtitlers": [s.model_dump() for s in subtitlers_db.values()],
            "summary": get_summary(),
            "video": current_video.model_dump() if current_video else None,
            "users": [u.model_dump() for u in connected_users.values()],
            "user_stats": get_user_stats(),
        }
        try:
            await active_websockets["admin"].send_json(data)
        except Exception:
            # Admin will be cleaned up by the metrics loop
            pass


async def update_metrics_loop():
    """
    Background task started from main.py.
    This is your original `update_metrics` inside `lifespan`, unchanged in logic.
    It updates subtitler metrics and broadcasts full state in real time.
    """
    import socket

    # Log server URLs once when the loop starts
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "127.0.0.1"

    print("✅ Server running on:")
    print("   Local:   http://localhost:8000")
    print(f"   Network: http://{local_ip}:8000")
    print(f"   Admin Dashboard: http://{local_ip}:8000")
    print(f"   Client Access:   http://{local_ip}:8000/client")
    print("\n   Share the network address with other users on your local network")

    while True:
        await asyncio.sleep(3)

        # Simulate subtitler progress
        for s in subtitlers_db.values():
            if s.active and s.completed < s.assigned:
                if random.random() > 0.6:
                    s.completed += 1
                    s.last_activity = "Just now"

        # Broadcast updates to all connected clients
        if active_websockets:
            data = {
                "subtitlers": [s.model_dump() for s in subtitlers_db.values()],
                "summary": get_summary(),
                "video": current_video.model_dump() if current_video else None,
                "users": [u.model_dump() for u in connected_users.values()],
                "user_stats": get_user_stats(),
            }

            disconnected = []
            for username, ws in list(active_websockets.items()):
                try:
                    await ws.send_json(data)
                except Exception as e:
                    print(f"Error sending to {username}: {e}")
                    disconnected.append(username)

            # Mark disconnected users
            for username in disconnected:
                if username in active_websockets:
                    del active_websockets[username]
                if username in connected_users and username != "admin":
                    connected_users[username].status = "offline"
                    connected_users[username].last_seen = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
