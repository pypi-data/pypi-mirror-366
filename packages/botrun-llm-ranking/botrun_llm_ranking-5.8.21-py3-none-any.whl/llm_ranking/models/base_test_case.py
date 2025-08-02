from typing import Dict, List
from pydantic import BaseModel


class BaseTestCase(BaseModel):
    id: str
    system_prompt: str
    messages: List[Dict[str, str]]
    model: str
    judge_model: str
    evaluation_prompt: str
