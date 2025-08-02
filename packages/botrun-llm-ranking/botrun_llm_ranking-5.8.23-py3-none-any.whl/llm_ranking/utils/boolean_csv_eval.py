from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
from llm_ranking.eval.boolean_eval import bool_eval
from llm_ranking.libs.llm_models_hub import LLMModelsHub
from llm_ranking.utils.boolean_test_case_reader import read_boolean_test_case_from_file
from llm_ranking.models.test_result import BooleanTestResult


def boolean_csv_eval(
    file_path: str, system_prompt: str, model: str
) -> List[BooleanTestResult]:
    """
    平行處理測試案例的評估

    Args:
        file_path: CSV 檔案路徑
        system_prompt: 系統提示詞
        model: 要測試的模型名稱

    Returns:
        List[BooleanTestResult]: 所有測試結果的列表
    """
    judge_model = "anthropic/claude-3-5-haiku-latest"
    test_cases = read_boolean_test_case_from_file(
        file_path=file_path,
        system_prompt=system_prompt,
        model=model,
        judge_model=judge_model,
    )

    llm_hub = LLMModelsHub()
    test_results = []

    # 使用 ThreadPoolExecutor 進行平行處理
    with ThreadPoolExecutor(max_workers=10) as executor:
        # 建立 future 到 test_case 的映射
        future_to_case = {
            executor.submit(bool_eval, llm_hub, test_case): test_case
            for test_case in test_cases
        }

        # 當每個 future 完成時，收集結果
        for future in as_completed(future_to_case):
            test_case = future_to_case[future]
            try:
                result = future.result()
                test_results.append(result)
                # 即時顯示進度
                print(
                    f"Completed test case {result.id}: {'Pass' if result.success else 'Fail'}"
                )
            except Exception as e:
                print(f"Test case {test_case.id} generated an exception: {str(e)}")
                test_results.append(
                    BooleanTestResult(
                        id=test_case.id,
                        success=False,
                        model_response="",
                        judge_model_response="",
                        note=f"Test case {test_case.messages} generated an exception: {str(e)}",
                    )
                )

    # 按照原始測試案例的順序排序結果
    test_results.sort(
        key=lambda x: test_cases.index(next(tc for tc in test_cases if tc.id == x.id))
    )

    return test_results
