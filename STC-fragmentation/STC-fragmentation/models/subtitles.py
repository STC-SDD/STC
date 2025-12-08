from pydantic import BaseModel

class Subtitle(BaseModel):
    fragment_id: str
    text: str
    submitted_by: str
