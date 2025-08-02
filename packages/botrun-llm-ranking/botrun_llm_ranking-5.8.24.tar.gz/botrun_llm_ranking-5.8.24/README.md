# LLM 評分系統

這是一個使用 Streamlit 和 LiteLLM 建立的語言模型評估系統。系統可以測試不同的語言模型，並使用 Claude 作為評分模型來評估回答品質。

## 作為 Python 套件使用

### 快速開始

本系統提供通用的測試執行函數，可以輕鬆整合到你的專案中：

```python
from llm_ranking.eval.boolean_eval import run_test_cases
from llm_ranking.models.boolean_test_case import BooleanTestCase
from llm_ranking.models.test_result import TestCaseResult
from llm_ranking.utils.boolean_test_case_reader import get_bool_test_case_eval_prompt

# 1. 建立測試案例
test_cases = [
    BooleanTestCase(
        id="test_1",
        messages=[{"role": "user", "content": "什麼是人工智能？"}],
        judge_model="google/gemini-2.5-flash",
        # evaluation_prompt 可以手動指定或使用 get_bool_test_case_eval_prompt 生成
        evaluation_prompt=get_bool_test_case_eval_prompt(
            pass_criteria="正確解釋人工智能的基本概念和應用",
            fail_criteria="回應不準確、過於簡略或包含錯誤資訊"
        )
    )
]

# 2. 定義你的 API 調用函數
def my_api_caller(test_case: BooleanTestCase) -> str:
    """
    自定義的 API 調用函數
    
    Args:
        test_case: 測試案例，包含 model、messages 等資訊
        
    Returns:
        模型的回應內容
    """
    # 這裡實作你的 API 調用邏輯
    # test_case.model 可以用來決定要調用哪個模型
    # test_case.messages 包含對話訊息
    
    # 範例：調用 OpenAI API
    import openai
    response = openai.ChatCompletion.create(
        model=test_case.model,
        messages=test_case.messages
    )
    return response.choices[0].message.content

# 3. 執行測試
test_generator = run_test_cases(test_cases, my_api_caller)

# 4. 處理結果
for result in test_generator:
    print(f"測試 {result.id}: {'通過' if result.is_pass else '失敗'}")
    print(f"輸出: {result.output}")
    print(f"評估原因: {result.pass_fail_reason}")
    print("-" * 50)
```

### 評估提示生成

#### get_bool_test_case_eval_prompt 函數
```python
from llm_ranking.utils.boolean_test_case_reader import get_bool_test_case_eval_prompt

# 生成標準化的評估提示
eval_prompt = get_bool_test_case_eval_prompt(
    pass_criteria="回應必須包含正確的技術解釋和實際應用例子",
    fail_criteria="回應包含錯誤資訊、過於簡略或偏離主題"
)

print(eval_prompt)
# 輸出格式化的中文評估提示，包含過關和不過關原則
```

**參數說明：**
- `pass_criteria`: 通過測試的標準（過關原則）
- `fail_criteria`: 未通過測試的標準（不過關原則）

**返回：** 格式化的中文評估提示字串，可直接用於 `evaluation_prompt` 欄位

### 主要組件

#### TestCaseResult 類別
```python
class TestCaseResult(BaseModel):
    id: str                    # 測試案例 ID
    output: str               # 模型回應內容
    is_pass: bool            # 是否通過測試
    pass_fail_reason: str    # 通過/失敗的詳細原因
```

#### run_test_cases 函數
```python
def run_test_cases(
    test_cases: List[BooleanTestCase], 
    get_response: Callable[[BooleanTestCase], str]
) -> Generator[TestCaseResult, None, None]:
```

**參數說明：**
- `test_cases`: 測試案例列表
- `get_response`: 你的 API 調用函數，接收 `BooleanTestCase` 並返回回應字串

**返回：** Generator，逐一產出 `TestCaseResult` 物件

### 進階使用範例

#### 批量測試多個模型
```python
models_to_test = ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet"]

for model in models_to_test:
    print(f"\n測試模型: {model}")
    
    test_cases = [
        BooleanTestCase(
            id=f"test_{model}_1",
            system_prompt="You are a helpful assistant.",
            messages=[{"role": "user", "content": "解釋量子計算"}],
            model=model,
            judge_model="anthropic/claude-3-sonnet",
            evaluation_prompt=get_bool_test_case_eval_prompt(
                pass_criteria="正確解釋量子計算的基本原理和應用",
                fail_criteria="回應不準確或缺乏重要概念"
            ),
            pass_criteria="正確解釋量子計算的基本原理和應用",
            fail_criteria="回應不準確或缺乏重要概念"
        )
    ]
    
    for result in run_test_cases(test_cases, my_api_caller):
        print(f"  結果: {'✓' if result.is_pass else '✗'} - {result.pass_fail_reason}")
```

#### 整合自定義評估邏輯
```python
# 如果你需要更複雜的錯誤處理
def robust_api_caller(test_case: BooleanTestCase) -> str:
    try:
        # 你的 API 調用邏輯
        return call_your_model_api(test_case)
    except Exception as e:
        # 自定義錯誤處理
        return f"調用失敗: {str(e)}"

# 使用你的健壯 API 調用函數
results = list(run_test_cases(test_cases, robust_api_caller))
```

## 安裝步驟

1. 安裝依賴：
```bash
pip install -r requirements.txt
```

2. 設置環境變數：
創建 `.env` 文件並添加以下內容：
```
OPENAI_API_KEY=你的OpenAI API金鑰
ANTHROPIC_API_KEY=你的Anthropic API金鑰
GOOGLE_API_KEY=你的Google API金鑰（如果要使用Gemini）
OPENROUTER_API_KEY=你的OpenRouter API金鑰（用於評估模型）
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

## Streamlit 應用程式

### 運行主應用程式：
```bash
streamlit run app.py
```

### 運行津貼測試應用程式：
```bash
streamlit run subsidy_app.py
```

## 使用方法

1. 在文本框中輸入測試問題
2. 輸入正確答案
3. 從下拉選單中選擇要測試的語言模型
4. 點擊「開始測試」按鈕
5. 等待系統生成模型回應和評分結果

## 支援的模型

- GPT-3.5 Turbo
- GPT-4
- Claude-2
- Gemini Pro
- Mistral-7B-Instruct

## poetry export requirements.txt
```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes --without-urls
```