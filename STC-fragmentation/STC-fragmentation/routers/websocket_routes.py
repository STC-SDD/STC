from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.websocket_manager import WebSocketManager
from services import fragment_assigner  # ⬅️ CHANGEMENT ICI

router = APIRouter()
ws_manager = WebSocketManager()

@router.websocket("/ws/{client}")
async def websocket_endpoint(ws: WebSocket, client: str):
    """Single WebSocket used for fragment assignment and submissions.
    Playback is client-driven (no admin control).
    """
    await ws_manager.connect(client, ws)

    # Utiliser TOUJOURS le dict vivant dans fragment_assigner
    for frag_id, info in fragment_assigner.fragments_state.items():
        if info.get("sous_titreur") == client:
            msg = f"Fragment {frag_id}: start {info['start']}s - end {info['end']}s"
            print(f"[DEBUG WS] Envoi vers {client} -> {msg}")
            await ws_manager.send_personal_message(client, msg)

    try:
        while True:
            data = await ws.receive_text()
            print(f"{client} a envoyé : {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(client)
        print(f"{client} déconnecté")
