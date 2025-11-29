from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.websocket_manager import WebSocketManager
from services.fragment_assigner import fragments_state

router = APIRouter()
ws_manager = WebSocketManager()

@router.websocket("/ws/{sous_titreur}")
async def websocket_endpoint(ws: WebSocket, sous_titreur: str):
    await ws_manager.connect(sous_titreur, ws)

    # Envoyer les fragments pour ce sous-titreur
    for frag_id, info in fragments_state.items():
        if info["sous_titreur"] == sous_titreur:
            await ws_manager.send_personal_message(
                sous_titreur,
                f"Fragment {frag_id}: start {info['start']}s - end {info['end']}s"
            )

    try:
        while True:
            data = await ws.receive_text()
            print(f"{sous_titreur} a envoyé : {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(sous_titreur)
        print(f"{sous_titreur} déconnecté")
