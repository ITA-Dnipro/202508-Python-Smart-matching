from pydantic import BaseModel

class Investor(BaseModel):
    user_id: int
    investment_focus: str
    location:str

class EmbedIn(BaseModel):
    text: str

class InvestorSearchRequest(BaseModel):
    investor_id: int
    top_k: int = 3

class MatchResult(BaseModel):
    startup_id: int
    startup_name: str
    startup_description: str
    similarity_score: float

class EchoIn(BaseModel):
    echo: str | None = None