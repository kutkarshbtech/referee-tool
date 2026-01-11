import json
import pandas as pd
from src.cypher_query import build_alias_model_map

def normalize_column(df, col, higher_is_better=True):
    if col not in df.columns or df[col].isnull().all():
        return pd.Series([0.0]*len(df), index=df.index)
    vals = pd.to_numeric(df[col], errors="coerce").fillna(0)
    min_v, max_v = vals.min(), vals.max()
    if max_v == min_v:
        return pd.Series([1.0]*len(df), index=df.index)
    norm = (vals - min_v) / (max_v - min_v)
    return norm if higher_is_better else 1.0 - norm

def score_models(df, user_fields):
    weights = {}
    n = len(user_fields)
    if n == 0:
        print("No valid fields for scoring.")
        return df

    weight = 1.0 / n
    for field, _ in user_fields:
        weights[field] = weight

    score = pd.Series([0.0]*len(df), index=df.index)
    for col, w in weights.items():
        lower_is_better = any(k in col.lower() for k in ["latency", "cost", "price", "time"])
        norm = normalize_column(df, col, higher_is_better=not lower_is_better)
        score += w * norm

    df_ranked = df.copy()
    df_ranked["Score"] = score
    return df_ranked.sort_values("Score", ascending=False)
