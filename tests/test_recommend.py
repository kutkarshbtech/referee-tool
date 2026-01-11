import pandas as pd
import pytest
from src.recommend import score_models

# Build dataframe from provided data
@pytest.fixture
def llm_df():
    data = {
        "Model": [
            "Grok 4",
            "o3-pro",
            "Gemini 2.5 Pro",
            "o3",
            "o4-mini (high)",
            "Qwen3 235B 2507 (Reasoning)"
        ],
        "Creator": ["xAI", "OpenAI", "Google", "OpenAI", "OpenAI", "Alibaba"],
        "License": ["Proprietary", "Proprietary", "Proprietary", "Proprietary", "Proprietary", "Open"],
        "Context Window": ["256k", "200k", "1m", "200k", "200k", "256k"],
        "Artificial Analysis Intelligence Index": [73, 71, 70, 70, 70, 69],
        "MMLU-Pro (Reasoning & Knowledge)": ["87%", None, "86%", "85%", "83%", "84%"],
        "GPQA Diamond (Scientific Reasoning)": ["88%", "85%", "84%", "83%", "78%", "79%"],
        "Humanity's Last Exam (Reasoning & Knowledge)": ["24%", None, "21%", "20%", "18%", "15%"],
        "LiveCodeBench (Coding)": ["82%", None, "80%", "78%", "80%", "79%"],
        "SciCode (Coding)": ["46%", None, "43%", "41%", "47%", "42%"],
        "HumanEval (Coding)": ["98%", None, None, "99%", "99%", "98%"],
        "MATH-500 (Quantitative Reasoning)": ["99%", None, "97%", "99%", "99%", "98%"],
        "AIME 2024 (Competition Math)": ["94%", None, "89%", "90%", "94%", "94%"],
        "Input Price (USD/1M Tokens)": [3.00, 20.00, 1.25, 2.00, 1.10, 0.70],
        "Output Price (USD/1M Tokens)": [15.00, 80.00, 10.00, 8.00, 4.40, 8.40],
        "Median (Tokens/s)": [68.3, 32.5, 147.4, 184.7, 118.2, 62.6],
        "Reasoning (Time (s))": [0, 0, 0, 0, 0, 31.94]
    }
    return pd.DataFrame(data)

def test_score_models_with_real_data(llm_df):
    # User cares about reasoning, cost, and latency
    user_fields = [
        ("MMLU-Pro (Reasoning & Knowledge)", "reasoning"),
        ("Input Price (USD/1M Tokens)", "low cost"),
        ("Median (Tokens/s)", "high throughput")
    ]

    ranked = score_models(llm_df, user_fields)

    # Ensure Score column exists
    assert "Score" in ranked.columns

    # Ensure dataframe is sorted by score descending
    scores = ranked["Score"].tolist()
    assert scores == sorted(scores, reverse=True)

    # Print top model for debugging
    top_model = ranked.iloc[0]["Model"]
    print("Top recommended model:", top_model)
