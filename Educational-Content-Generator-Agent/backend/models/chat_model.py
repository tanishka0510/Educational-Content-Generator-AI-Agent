from pydantic import BaseModel

class ChatRequest(BaseModel):
    filename: str
    question: str