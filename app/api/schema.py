from pydantic import BaseModel

class Investor(BaseModel):
    user_id: int
    investment_focus: str
    location:str

class EmbedIn(BaseModel):
    text: str