from pydantic import BaseModel

class QueryRequest(BaseModel):
    subject: str
    question: str