import pandas as pd
import re
from datetime import datetime

def clean_key(key):
    key = re.sub(r'[^\w\s]', '', key)  # Remove non-alphanumeric except underscore/space
    key = key.replace(' ', '_')
    return key.lower()

def build_cypher_queries(df):
    cypher_queries = []

    # 1. Create parent node first
    all_models = [str(row.get("Model", f"Model_{idx+1}")) for idx, row in df.iterrows()]
    all_models_str = ", ".join([f'"{m}"' for m in all_models])
    parent_cypher = f'MERGE (models:MODELS {{ all_llm_models: [{all_models_str}], created_at: "{datetime.now().isoformat()}" }})'
    cypher_queries.append(parent_cypher)

    # 2. Create all model nodes
    for idx, (_, row) in enumerate(df.iterrows(), 1):
        alias = f"a{idx}"
        properties = []
        model_name = str(row.get("Model", f"Model_{idx}"))
        for col, val in row.items():
            if pd.notnull(val):
                key = clean_key(col)
                if isinstance(val, str):
                    val_str = f'"{val}"'
                else:
                    val_str = str(val)
                properties.append(f'{key}: {val_str}')
        prop_str = ", ".join(properties)
        cypher = f'MERGE ({alias}:{clean_key(model_name)} {{ {prop_str} }})'
        cypher_queries.append(cypher)
    return cypher_queries

def build_alias_model_map(df):
    alias_model_map = {}
    for idx, row in enumerate(df.itertuples(index=False), 1):
        alias = f"a{idx}"
        model_name = getattr(row, "Model", f"Model_{idx}")
        alias_model_map[alias] = str(model_name)
    return alias_model_map

def build_relationship_queries(num_models):
    rel_cypher_queries = []
    for i in range(1, num_models + 1):
        rel_cypher = f"MERGE (models)-[:LLM_Model]->(a{i})"
        rel_cypher_queries.append(rel_cypher)
    return rel_cypher_queries
