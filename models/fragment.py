from pydantic import BaseModel

class Fragment(BaseModel):
    id: str
    start: float
    end: float
    sous_titreur: str | None = None  # assigned subtitler
    statut: str = "unassigned"  # "unassigned", "en cours", "done"
