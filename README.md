---
# Referee Tool: LLM Model Recommendation System

## Overview
This project implements **Week 6: The Referee** challenge.  
It is designed to support research and decision‑making when selecting large language models (LLMs).  
The tool helps users choose the most suitable LLM for their project by:
- Extracting requirements from a natural language description (Claude via AWS Bedrock).
- Scoring and ranking models based on metadata in `data/Model_info.xlsx`.
- Explaining trade‑offs for each recommendation.
- Storing results in a Neo4j knowledge graph for future analysis and reuse.

Instead of providing a single answer, the tool acts as a **referee** — comparing options, explaining trade‑offs, and enabling informed decisions with more resources to start similar problem statements.

---

## Features
- **Requirement Extraction**: Uses Claude (AWS Bedrock) to analyze project descriptions and identify relevant fields.  
- **Model Scoring**: Normalizes metrics (latency, cost, reasoning, throughput) and ranks models.  
- **Trade‑off Explanations**: Provides concise summaries of why each model fits or doesn’t fit.  
- **Knowledge Graph Storage**: Saves decisions in Neo4j AuraDB using Cypher queries.  
- **Interactive UI**: Streamlit app for submitting descriptions, viewing recommendations, and pushing results to Neo4j.

---

## Project Structure

referee-tool/
│
├── .kiro/                # Required directory for submission
│   └── config.json
│
├── data/
│   └── Model_info.xlsx   # LLM model metadata
│
├── src/
│   ├── cypher_query.py       # Cypher query builder
│   ├── keyword_extraction.py # Claude prompt + AWS Bedrock invocation
│   ├── recommend.py          # Scoring and ranking logic
│   └── __init__.py
│
├── outputs/
│   └── claude_output.json    # Saved Claude response
│
├── tests/
│   └── test_recommend.py     # Unit tests
│
├── main.py                   # Streamlit app entry point
├── requirements.txt          # Dependencies
└── README.md                 # Documentation


---

## How to Run

1. **Clone the repo**
git clone https://github.com/kutkarshbtech/referee-tool.git
cd referee-tool

2. **Install dependencies**
pip install -r requirements.txt

3. **Run the Streamlit app**
streamlit run main.py

---

## Example Usage

**Input:**
We need a low-latency, cost-efficient LLM for real-time chatbot deployment.

**Output:**
- 🏆 Recommended Model: **Model_X**
- **Why:**
  - **Latency**: Fast response time ideal for real-time use  
  - **Cost**: Low input price per 100K tokens  
  - **Reasoning**: Strong performance on MMLU and GPQA  

---

## Knowledge Graph Integration
- All models and project selections are stored in **Neo4j AuraDB**.  
- Cypher queries link projects to chosen models.  
- Enables future research: track which models were chosen for similar problems and compare outcomes.

---

## Submission Notes
- `.kiro/` directory included at root.  
- Blog post published on AWS Builder Center (with screenshots).  
- Repo + blog link submitted via AI for Bharat dashboard.  

---

## Screenshots

## Screenshots

### Streamlit UI
![ui-screen](streamlit_ui.png)
![input](input.png)

### Recommendation Output
![output](output.png)

### Neo4j Graph
![cypher-output](cpher_output.png)
![neo4j-model-nodes](neo4j_output.png)
![added-node](newly_added_node.png)

---


## Acknowledgements
- Built as part of **AI for Bharat Week 6 Challenge: The Referee**.  
- Powered by **AWS Bedrock (Claude)**, **Neo4j AuraDB**, and **Streamlit**.  


---
