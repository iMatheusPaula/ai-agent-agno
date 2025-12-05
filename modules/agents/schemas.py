from typing import Optional
from pydantic import BaseModel


class UseAgentRequest(BaseModel):
    message: str
    session_id: str
