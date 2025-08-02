from llm_ranking.libs.llm_models_hub import LLMModelsHub
from llm_ranking.models.boolean_test_case import BooleanTestCase
from llm_ranking.models.test_result import BooleanTestResult, TestCaseResult
import json
from litellm import completion
from typing import List, Callable, Optional, Generator, Awaitable, AsyncGenerator
import asyncio
import time
import requests
import os
from langchain_openai import ChatOpenAI
from trustcall import create_extractor
from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    """評估結果的結構化輸出"""

    pass_result: bool = Field(description="測試是否通過")
    pass_fail_reason: str = Field(description="通過或失敗的詳細原因")


def evaluate_test_result(test_case: BooleanTestCase, output: str) -> EvaluationResult:
    """
    使用 LLM 評估測試結果
    """
    # 設置 OpenRouter 的 ChatOpenAI
    llm = ChatOpenAI(
        model=test_case.judge_model,
        temperature=0,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base=os.getenv("OPENROUTER_BASE_URL"),
    )

    # 創建 trustcall extractor
    extractor = create_extractor(
        llm, tools=[EvaluationResult], tool_choice="EvaluationResult"
    )

    # 評估 prompt
    evaluation_prompt = f"""你是一個專業的測試評估機器人。請根據以下資訊評估測試結果：

<測試案例ID>
{test_case.id}
</測試案例ID>

<使用者輸入>
{test_case.messages[-1]["content"] if test_case.messages else "無輸入"}
</使用者輸入>

<系統回應>
{output}
</系統回應>

<評估標準>
{test_case.evaluation_prompt}
</評估標準>

請根據評估標準判斷系統回應是否符合要求：
1. 如果系統回應完全符合評估標準中的所有要求，則 pass_result 為 true
2. 如果系統回應不符合任何一項評估標準，則 pass_result 為 false
3. 在 pass_fail_reason 中詳細說明判斷的理由

請提供結構化的評估結果。"""

    try:
        result = extractor.invoke({"messages": [("user", evaluation_prompt)]})

        if result["responses"]:
            return result["responses"][0]
        else:
            return EvaluationResult(
                pass_result=False, pass_fail_reason="評估過程中未能產生有效結果"
            )

    except Exception as e:
        return EvaluationResult(
            pass_result=False, pass_fail_reason=f"評估過程發生錯誤: {str(e)}"
        )


def find_result_recursively(data):
    """
    有時候模型不會按照預期回覆，所以就遞迴尋找 result 的值
    """
    if isinstance(data, dict):
        if "result" in data:
            return data["result"]
        for value in data.values():
            result = find_result_recursively(value)
            if result is not None:
                return result
    return None


def bool_eval(llm_hub: LLMModelsHub, test_case: BooleanTestCase):
    model_response = ""
    for chunk in llm_hub.get_completion(
        model=test_case.model,
        messages=test_case.messages,
        stream=True,
        system_prompt=test_case.system_prompt,
    ):
        if hasattr(chunk.choices[0], "delta") and hasattr(
            chunk.choices[0].delta, "content"
        ):
            content = chunk.choices[0].delta.content
            if content:
                model_response += content

    response = completion(
        model=test_case.judge_model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that provides structured output.",
            },
            {
                "role": "user",
                "content": EVAL_PROMPT.format(
                    user_input=test_case.messages[-1]["content"],
                    model_response=model_response,
                    evaluation_prompt=test_case.evaluation_prompt,
                ),
            },
        ],
        response_format={"type": "json_object"},
    )
    judge_model_response = response.choices[0].message.content
    result = json.loads(judge_model_response)
    found_result = find_result_recursively(result)
    success = False
    if found_result is not None:
        if isinstance(found_result, bool):
            success = found_result
        else:
            success = found_result.get("result", False)

    return BooleanTestResult(
        success=success,
        id=test_case.id,
        model_response=model_response,
        judge_model_response=judge_model_response,
    )


async def subsidy_api_caller(test_case: BooleanTestCase) -> str:
    """
    Subsidy API 調用函數，提取原本 run_subsidy_test 中的 API 調用邏輯

    Args:
        test_case: 測試案例

    Returns:
        API 回應內容字串
    """
    # 從環境變數讀取 API base URL
    api_base = os.getenv("LANGRAPH_API_BASE", "http://0.0.0.0:8080")
    api_url = f"{api_base}/api/subsidy/completion"

    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        "Content-Type": "application/json",
    }

    # 準備 API 請求資料
    payload = {"messages": test_case.messages, "stream": False}

    # 調用 API (保持同步調用，因為 requests 是同步的)
    response = requests.post(api_url, headers=headers, json=payload)
    response.raise_for_status()

    # 解析回應
    response_data = response.json()
    return response_data["choices"][0]["message"]["content"]


async def run_subsidy_test(test_cases: List[BooleanTestCase]) -> AsyncGenerator[dict, None]:
    """
    執行 subsidy 測試，作為 async generator 返回測試結果

    Args:
        test_cases: 測試案例列表

    Yields:
        每個測試的結果字典，包含 id, output, pass, score, pass_fail_reason
    """
    # 使用新的通用函數
    test_results = run_test_cases(test_cases, subsidy_api_caller)
    async for result in test_results:

        # 轉換為原本的字典格式以保持向後相容性
        yield {
            "id": result.id,
            "output": result.output,
            "pass": result.is_pass,
            "pass_fail_reason": result.pass_fail_reason,
            "score": 100 if result.is_pass else 0,
        }


async def run_test_cases(
    test_cases: List[BooleanTestCase], get_response: Callable[[BooleanTestCase], Awaitable[str]]
) -> AsyncGenerator[TestCaseResult, None]:
    """
    執行通用測試，支援自定義的回應內容獲取函數

    Args:
        test_cases: 測試案例列表
        get_response: 函數，接收 BooleanTestCase 並返回回應內容字串

    Yields:
        測試結果，每個元素為 TestCaseResult
    """
    for test_case in test_cases:
        try:
            # 呼叫自定義函數獲取回應內容
            output = await get_response(test_case)

            # 使用 LLM 評估結果
            evaluation = evaluate_test_result(test_case, output)

            # 建立測試結果
            result = TestCaseResult(
                id=test_case.id,
                output=output,
                is_pass=evaluation.pass_result,
                pass_fail_reason=evaluation.pass_fail_reason,
            )

        except Exception as e:
            import traceback

            traceback.print_exc()
            # 處理異常情況
            result = TestCaseResult(
                id=test_case.id,
                output=f"API 調用錯誤: {str(e)}",
                is_pass=False,
                pass_fail_reason=f"測試執行失敗: {str(e)}",
            )

        yield result


EVAL_PROMPT = """
你是一個驗證機器人。你的任務是根據 <使用者輸入> 及 <LLM回應> ，驗證是否有符合 <預期規則>，將結果按照 <輸出要求> 輸出。

<使用者輸入>
{user_input}
</使用者輸入>

<LLM回應>
{model_response}
</LLM回應>

<預期規則>
{evaluation_prompt}
</預期規則>

＜輸出要求＞
1. 必須且只能輸出以下格式的 JSON，只會有一層：
{{"result": boolean}}

2. 嚴格規定：
- 不允許有任何額外的空格或換行
- boolean 值必須是 true 或 false（小寫）
- 不能有額外的 key 或巢狀結構
- 不能包含註解或其他文字
- 雙引號必須是直引號(")，不能用單引號(')

3. 正確的輸出範例：
{{"result":true}}
{{"result":false}}

4. 錯誤的輸出範例（以下格式都不允許）：
{{'result': true}}
{{"result": True}}
{{ "result": true }}
{{"json_input": {{"result": true}}}}
{{"json": {{"result": true}}}}
{{"input": {{"result": true}}}}
{{}}

請嚴格按照以上規則輸出，不要加入任何其他內容。
＜／輸出要求＞
"""


if __name__ == "__main__":
    # result_str = '{"result": {"result": true}}'
    # result = json.loads(result_str)
    # result = find_result_recursively(result)
    # print(result)
    eval_prompt = """
你會檢查模型的回應，當符合 <過關原則> 內全部條件，並且不符合 <不過關原則> 內全部條件，則回傳 true，否則回傳 false
如果不符合 <過關原則> 任何一個條件，則回傳 false
如果符合 <不過關原則> 任何一個條件符合，則回傳 false

<過關原則>
- 模型有回答與使用者提問相關的內容
</過關原則>

<不過關原則>:
- 模型沒有回答與使用者提問相關的內容
</不過關原則>
"""
    llm_hub = LLMModelsHub()
    test_case = BooleanTestCase(
        id="test_case_1",
        system_prompt="You are a helpful assistant.",
        messages=[{"role": "user", "content": "最近的國際新聞有什麼?"}],
        model="langgraph/perplexity_search_agent",
        judge_model="anthropic/claude-3-5-haiku-latest",
        evaluation_prompt=eval_prompt,
    )
    result = bool_eval(llm_hub, test_case)
    print(result)
