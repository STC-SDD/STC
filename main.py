from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json
import asyncio
from fastapi.staticfiles import StaticFiles



app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


clients = {}
fragments_state = {}

# --- Charger les fichiers JSON ---
def load_fragments():
    
    with open("fragments.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_sous_titreurs():
    with open("sous_titreurs.json", "r", encoding="utf-8") as f:
        return json.load(f)

# --- Attribution Round Robin ---
def attribuer_fragments(fragments, sous_titreurs):
    fragments_state = {}
    st_names = [k for k, v in sous_titreurs.items() if v == "connecté"]
    for i, frag in enumerate(fragments):
        st = st_names[i % len(st_names)]
        fragments_state[frag["id"]] = {"start": frag["start"], "end": frag["end"],
                                       "sous_titreur": st, "statut": "en cours"}
    # Sauvegarder dans JSON
    with open("fragments_state.json", "w", encoding="utf-8") as f:
        json.dump(fragments_state, f, ensure_ascii=False, indent=4)
    return fragments_state

# --- Initialisation au démarrage ---
@app.on_event("startup")
async def startup_event():
    fragments = load_fragments()
    sous_titreurs = load_sous_titreurs()
    global fragments_state
    fragments_state = attribuer_fragments(fragments, sous_titreurs)
    print("Fragments attribués au démarrage.")

# --- WebSocket ---
@app.websocket("/ws/{sous_titreur}")
async def websocket_endpoint(ws: WebSocket, sous_titreur: str):
    await ws.accept()
    clients[sous_titreur] = ws

    # --- Envoyer les fragments attribués à ce sous-titreur ---
    for frag_id, info in fragments_state.items():
        if info["sous_titreur"] == sous_titreur:
            await ws.send_text(f"Fragment {frag_id}: start {info['start']}s - end {info['end']}s")

    try:
        while True:
            data = await ws.receive_text()
            print(f"{sous_titreur} a envoyé : {data}")
    except WebSocketDisconnect:
        clients.pop(sous_titreur, None)
        print(f"{sous_titreur} déconnecté")

# --- Page HTML ---
@app.get("/")
def get():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Sous-titreur</title>
      <style>
        #subtitle { position: absolute; bottom: 40px; width: 100%; text-align: center; font-size: 22px; color: white; text-shadow: 2px 2px 4px black; }
        #container { position: relative; width: 640px; }
      </style>
    </head>
    <body>
      <h2>Interface Sous-titreur</h2>
      <div id="container">
       <video id="video" width="640" controls>
  <source src="/static/sous_titrage.mp4" type="video/mp4">
</video>

        <div id="subtitle"></div>
      </div>
      <div>
        <input type="text" id="inputSubtitle" placeholder="Écrire le sous-titre..." disabled>
        <button id="submitBtn" disabled>Soumettre</button>
      </div>

      <div id="fragments"></div>

<script>
const sous_titreur = prompt("Entrez votre nom de sous-titreur :");
const ws = new WebSocket(`ws://localhost:8000/ws/${sous_titreur}`);
let fragments = [];
let currentFrag = null;
let waitingSubmission = false;

// --- Affichage des fragments assignés ---
const fragmentsDiv = document.getElementById("fragments");

ws.onmessage = (event) => {
    // Parse fragment numbers from string
    const regex = /Fragment \d+: start ([0-9.]+)s - end ([0-9.]+)s/;
    const match = event.data.match(regex);
    if (match) {
        const frag = {
            start: parseFloat(match[1]),
            end: parseFloat(match[2]),
            text: "",       // pour stocker le sous-titre envoyé
            submitted: false
        };
        fragments.push(frag);
        fragments.sort((a, b) => a.start - b.start);

        // Afficher le fragment assigné
        fragmentsDiv.innerHTML += `<p>Fragment assigné: start ${frag.start}s - end ${frag.end}s</p>`;
        console.log("Fragment assigné:", frag);
    }
};

const video = document.getElementById("video");
const input = document.getElementById("inputSubtitle");
const btn = document.getElementById("submitBtn");

video.ontimeupdate = () => {
    const t = video.currentTime;

    // Si on attend la soumission, ne rien changer
    if (waitingSubmission) {
        input.disabled = false;
        btn.disabled = false;
        return;
    }

    // Chercher le fragment actuel
    currentFrag = fragments.find(f => t >= f.start && t < f.end);

    if (currentFrag) {
        // Activer la saisie
        input.disabled = false;
        btn.disabled = false;
    } else {
        // Si on est juste après un fragment (fin atteinte)
        const justEndedFrag = fragments.find(f => t >= f.end && !f.submitted);
        if (justEndedFrag) {
            // Mute la vidéo
            video.muted = true;
            currentFrag = justEndedFrag;
            waitingSubmission = true;
            input.disabled = false;
            btn.disabled = false;
        } else {
            input.disabled = true;
            btn.disabled = true;
        }
    }
};

btn.onclick = () => {
    if (input.value.trim() !== "") {
        // Envoyer le sous-titre au serveur
        ws.send(input.value);

        // Stocker le texte et marquer le fragment comme soumis
        if (currentFrag) {
            currentFrag.submitted = true;
            currentFrag.text = input.value;

            // Afficher le sous-titre saisi sous le fragment
            fragmentsDiv.innerHTML += `<p>Sous-titre soumis: "${input.value}" pour fragment ${currentFrag.start}-${currentFrag.end}s</p>`;
        }

        // Réactiver le son et désactiver le bouton
        video.muted = false;
        input.disabled = true;
        btn.disabled = true;
        waitingSubmission = false;

        input.value = "";
    }
};
</script>



    </body>
    </html>
    """
    return HTMLResponse(html_content)
