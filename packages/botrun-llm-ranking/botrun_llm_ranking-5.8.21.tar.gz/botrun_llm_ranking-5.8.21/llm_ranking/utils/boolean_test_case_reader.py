from llm_ranking.eval import boolean_eval
from llm_ranking.libs.llm_models_hub import LLMModelsHub
from llm_ranking.models.boolean_test_case import BooleanTestCase
from llm_ranking.eval.boolean_eval import bool_eval
from pathlib import Path
import pandas as pd
from typing import List
import uuid
import json


def read_boolean_test_case_from_file(
    file_path: str,
    system_prompt: str,
    model: str,
    judge_model: str,
) -> List[BooleanTestCase]:
    """
    這個會讀取 csv 檔案，並且將每一行轉換成 BooleanTestCase 物件
    column 必須要有：messages, pass_criteria, fail_criteria
    """
    df = pd.read_csv(file_path)
    return read_boolean_test_case_from_df(df, system_prompt, model, judge_model)


def read_boolean_test_case_from_df(
    df: pd.DataFrame,
    system_prompt: str,
    model: str,
    judge_model: str,
) -> List[BooleanTestCase]:
    """
    將 DataFrame 的每一行轉換成 BooleanTestCase 物件
    column 必須要有：id, messages, pass_criteria, fail_criteria
    """
    eval_prompt = """
你會檢查模型的回應，當符合 <過關原則> 內全部條件，並且不符合 <不過關原則> 內全部條件，則回傳 true，否則回傳 false
如果不符合 <過關原則> 任何一個條件，則回傳 false
如果符合 <不過關原則> 任何一個條件符合，則回傳 false

<過關原則>
{pass_criteria}
</過關原則>

<不過關原則>:
{fail_criteria}
</不過關原則>
"""

    test_cases: List[BooleanTestCase] = []

    for _, row in df.iterrows():
        try:
            # 清理 messages 字串中的控制字符
            messages_str = str(row["messages"])
            # 移除常見的控制字符
            messages_str = (
                messages_str.replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t")
            )
            # 嘗試解析 JSON
            messages = json.loads(messages_str)
        except json.JSONDecodeError as e:
            print(f"JSON 解析錯誤 for id {row['id']}: {e}")
            print(f"原始 messages: {repr(row['messages'])}")
            # 如果解析失敗，使用預設的 messages 格式
            messages = [{"role": "user", "content": str(row["messages"])}]

        test_case = BooleanTestCase(
            id=row["id"],
            system_prompt=system_prompt,
            messages=messages,
            model=model,
            judge_model=judge_model,
            evaluation_prompt=eval_prompt.format(
                pass_criteria=row["pass_criteria"],
                fail_criteria=row["fail_criteria"],
            ),
        )
        test_cases.append(test_case)

    return test_cases
