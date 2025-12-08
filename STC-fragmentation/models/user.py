from pydantic import BaseModel

class User(BaseModel):
    username: str
    role: str  # "admin", "subtitler", "watcher"
    status: str = "offline"  # optional: "connecté" or "offline"
