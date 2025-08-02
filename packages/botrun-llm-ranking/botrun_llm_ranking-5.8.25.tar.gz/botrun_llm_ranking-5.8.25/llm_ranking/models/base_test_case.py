from typing import Dict, List, Optional
from pydantic import BaseModel


class BaseTestCase(BaseModel):
    id: str
    system_prompt: Optional[str] = None
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    judge_model: str  # Use OpenRouter model name
    evaluation_prompt: str
