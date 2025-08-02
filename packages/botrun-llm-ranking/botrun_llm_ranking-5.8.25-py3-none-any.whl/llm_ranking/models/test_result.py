from pydantic import BaseModel


class BooleanTestResult(BaseModel):
    """Boolean test result model for evaluation results"""

    id: str
    success: bool
    model_response: str
    judge_model_response: str
    note: str = ""


class TestCaseResult(BaseModel):
    """Test case result model for test execution results"""
    
    id: str
    output: str  # 來自 get_response
    is_pass: bool  # evaluation.pass_result
    pass_fail_reason: str  # evaluation.pass_fail_reason
