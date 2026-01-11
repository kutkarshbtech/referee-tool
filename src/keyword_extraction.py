import boto3
import json
import os
import pandas as pd

# Configure AWS if not globally set
os.environ["AWS_ACCESS_KEY_ID"] = "access id"
os.environ["AWS_SECRET_ACCESS_KEY"] = "secret key"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

def generate_requirement_extraction_prompt(user_project_description):
    df = pd.read_excel("data/Model_info.xlsx")
    fields = list(df.columns)
    field_list = ", ".join(fields)

    prompt = f"""
You are an expert requirements analyst. Given the following user project description, extract a list of keywords and a short summary (10–15 words) for the extracted fields: {field_list}.

For each field:
- Output a relevant keyword from field_list (if applicable).
- Write a concise 10–15 word summary describing how this field relates to the project.

User Project Description:
\"\"\"{user_project_description}\"\"\"

Respond in this format:
[
  {{
    "field": "<Field Name>",
    "keyword": "<Relevant keyword or phrase>",
    "summary": "<10–15 word summary of the relationship to the project>"
  }},
  ...
]
"""
    return prompt.strip()

def invoke_claude_keyphrase(prompt, 
                             model_id="anthropic.claude-3-sonnet-20240229-v1:0", 
                             region="us-east-1"):
    client = boto3.client("bedrock-runtime", region_name=region)

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 8000,
        "temperature": 0.5,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)
        )
        result = json.loads(response["body"].read())

        # Extract the text content from Claude
        text_output = result.get("content", [{}])[0].get("text", "").strip()

        # Try to parse the text into JSON array
        try:
            parsed_output = json.loads(text_output)
        except json.JSONDecodeError:
            parsed_output = []

        # Save only the parsed array
        with open("outputs/claude_output.json", "w") as f:
            json.dump(parsed_output, f, indent=2)

        return parsed_output
    except Exception as e:
        print("Claude invocation failed:", str(e))
        return []
