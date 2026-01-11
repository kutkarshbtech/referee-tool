import streamlit as st
import pandas as pd
import json
import re

from src.keyword_extraction import invoke_claude_keyphrase, generate_requirement_extraction_prompt
from src.cypher_query import build_alias_model_map, build_relationship_queries, build_cypher_queries
from src.recommend import score_models

from neo4j import GraphDatabase

# Neo4j AuraDB connection class
class AuraDBConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_queries(self, query):
        with self.driver.session() as session:
            session.run(query)
        print("Query executed successfully!")

# Replace with your AuraDB credentials
URI = "neo4j+ssc://ce98dab8.databases.neo4j.io:7687"
USERNAME = "neo4j"
PASSWORD = "neo4j_passwoed"

# Streamlit UI
def main():
    st.set_page_config(page_title="LLM Model Recommendation", layout="centered")
    st.title("LLM Model Recommendation System")

    # Add "Update Queries" button at top-right
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("Update Queries"):
            df = pd.read_excel("data/Model_info.xlsx")
            cypher_queries = build_cypher_queries(df)
            rel_cypher_queries = build_relationship_queries(len(df))
            complete_queries = cypher_queries + rel_cypher_queries

            for q in complete_queries:
                try:
                    conn = AuraDBConnection(URI, USERNAME, PASSWORD)
                    conn.run_queries(q)
                    conn.close()
                except Exception as e:
                    st.error(f"Failed to run query:\n{q}\n\nError: {e}")
            st.success("All Cypher queries updated successfully!")

    # Session state variables
    if "cypher_query" not in st.session_state:
        st.session_state.cypher_query = None
    if "best_model" not in st.session_state:
        st.session_state.best_model = None
    if "combined_summary" not in st.session_state:
        st.session_state.combined_summary = None

    st.write("Enter your project description to discover the best-fit model.")

    df = pd.read_excel("data/Model_info.xlsx")
    field_list = list(df.columns)

    project_description = st.text_area("Project Description")

    if st.button("Submit"):
        if not project_description.strip():
            st.warning("Please enter a valid description.")
            return

        prompt = generate_requirement_extraction_prompt(project_description)
        records = invoke_claude_keyphrase(prompt)

        # If Claude fails, try loading saved output
        if not records:
            try:
                with open("outputs/claude_output.json", "r") as f:
                    records = json.load(f)
            except Exception:
                st.error("No valid Claude output found.")
                return

        user_fields = [(rec["field"], rec["keyword"]) for rec in records if rec.get("keyword") and rec["field"] in field_list]

        if not user_fields:
            st.warning("No relevant fields were matched with model metadata.")
            return

        ranked_df = score_models(df, user_fields)
        best_model = ranked_df.iloc[0]["Model"]

        # Store results
        st.session_state.best_model = best_model
        st.session_state.combined_summary = "\n".join([
            f"{rec['field']}: {rec['summary']}"
            for rec in records
            if rec.get("keyword") and rec["field"] in df.columns
        ])

        # Display Results
        st.subheader("Recommended Model")
        st.write(f"**Model Selected:** {best_model}")

        st.write("**Why this model?**")
        for rec in records:
            if rec.get("keyword") and rec["field"] in df.columns:
                st.markdown(f"- **{rec['field']}**: {rec['summary']}")

    # If a model has been selected, allow "Agree" to generate Cypher query
    if st.session_state.best_model:
        if st.button("Agree"):
            alias_model_map = build_alias_model_map(df)
            alias = next((k for k, v in alias_model_map.items() if v == st.session_state.best_model), "UNKNOWN_ALIAS")
            today_str = pd.Timestamp.today().strftime('%Y-%m-%d')

            cleaned_best_model = re.sub(r'[^a-z0-9]+', '_', st.session_state.best_model.lower()).strip('_')

            cypher_best_model = (
                f'MATCH ({alias}:{cleaned_best_model})\n'
                f'MERGE (p:Project {{ '
                f'description: "{project_description}", '
                f'summary: "{st.session_state.combined_summary}", '
                f'date: "{today_str}" '
                f'}})\n'
                f'MERGE (p)-[:USES_MODEL]->({alias})'
            )

            st.session_state.cypher_query = cypher_best_model

    # Display and execute Cypher query
    if st.session_state.cypher_query:
        st.subheader("Generated Cypher Query")
        st.code(st.session_state.cypher_query, language="cypher")

        try:
            conn = AuraDBConnection(URI, USERNAME, PASSWORD)
            conn.run_queries(st.session_state.cypher_query)
            conn.close()
            st.success("Knowledge Graph query executed successfully!")
        except Exception as e:
            st.error(f"Error executing query: {e}")

if __name__ == "__main__":
    main()
