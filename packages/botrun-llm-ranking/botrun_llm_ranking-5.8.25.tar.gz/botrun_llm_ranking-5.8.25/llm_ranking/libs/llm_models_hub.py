import os
from typing import List, Dict, Generator, Any, Union
from litellm import completion
from dotenv import load_dotenv
import time
import asyncio

from llm_ranking.utils.langgraph_util import run_graph

# from botrun_litellm import botrun_litellm_completion

# 載入環境變數
load_dotenv()


class LLMModelsHub:
    def __init__(self):
        # 初始化各種 API 金鑰和 base URL
        self.botrun_base_url = os.getenv("BOTRUN_BASE_URL")
        self.botrun_api_key = os.getenv("BOTRUN_API_KEY")
        self.taide_base_url = os.getenv("TAIDE_BASE_URL")
        self.taide_api_key = os.getenv("TAIDE_API_KEY")

    def _call_botrun_model(
        self, model: str, messages: List[Dict[str, str]], stream: bool = True
    ) -> Generator[Any, None, None]:
        """處理 botrun 模型的呼叫"""
        return completion(
            model=model.replace("botrun/", ""),
            messages=messages,
            stream=stream,
            api_base=self.botrun_base_url,
            api_key=self.botrun_api_key,
        )

    def _call_taide_model(
        self, model: str, messages: List[Dict[str, str]], stream: bool = True
    ) -> Generator[Any, None, None]:
        """處理 taide 模型的呼叫"""
        return completion(
            model=model.replace("taide/", ""),
            messages=messages,
            stream=stream,
            api_base=self.taide_base_url,
            api_key=self.taide_api_key,
        )

    def _call_langgraph_model(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = True,
        system_prompt: str = "",
    ) -> Generator[Any, None, None]:
        """處理 langgraph 模型的呼叫（範例實現）"""

        class DummyResponse:
            def __init__(self, text):
                self.choices = [
                    type(
                        "DummyChoice",
                        (),
                        {"delta": type("DummyDelta", (), {"content": text})()},
                    )
                ]

        # 如果是串流模式，分段回傳
        # if stream:
        #     response_text = "this is langgraph model response"
        #     for char in response_text:
        #         yield DummyResponse(char)
        # else:
        content = asyncio.run(run_graph(model, messages, system_prompt))
        yield DummyResponse(content)

    def _call_default_model(
        self, model: str, messages: List[Dict[str, str]], stream: bool = True
    ) -> Generator[Any, None, None]:
        """處理其他模型的呼叫（使用預設的 litellm 設定）"""
        return completion(model=model, messages=messages, stream=stream)

    def get_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = True,
        system_prompt: str = "",
    ) -> Generator[Any, None, None]:
        """統一的模型呼叫介面"""
        try:
            if model.startswith("botrun/"):
                return self._call_botrun_model(model, messages, stream)
            elif model.startswith("taide/"):
                return self._call_taide_model(model, messages, stream)
            elif model.startswith("langgraph/"):
                return self._call_langgraph_model(
                    model, messages, stream, system_prompt
                )
            else:
                return self._call_default_model(model, messages, stream)
        except Exception as e:
            raise Exception(f"模型呼叫錯誤 ({model}): {str(e)}")
