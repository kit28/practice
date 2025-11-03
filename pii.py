import pandas as pd
import json
from openai import OpenAI

# ---------- CONFIG ----------
client = OpenAI(api_key="your_api_key_here")   # or adjust if using another LLM endpoint
data_file = "your_excel_with_multiple_sheets.xlsx"
pii_ref_file = "pii_reference.xlsx"

# ---------- LOAD PII REFERENCE ----------
pii_ref = pd.read_excel(pii_ref_file)
pii_context = "\n".join([
    f"{row['name']}: {row['definition']}" 
    for _, row in pii_ref.iterrows()
])

# ---------- READ MULTIPLE SHEETS ----------
xls = pd.ExcelFile(data_file)

# Store final results
all_results = []

for sheet_name in xls.sheet_names:
    df = pd.read_excel(data_file, sheet_name=sheet_name)

    # Only if the sheet has the target column
    if 'ColumnName' not in df.columns:
        continue

    # Get unique column names to classify (avoid duplicates)
    columns_to_classify = df['ColumnName'].dropna().unique().tolist()
    if not columns_to_classify:
        continue

    # ---------- PROMPT ----------
    prompt = f"""
You are an expert in data governance and PII identification.

Below are known PII field names and their definitions:
{pii_context}

Now, you are given a list of column names from a dataset.
For each, classify whether it represents a PII (personally identifiable information) field or not.

Return the output **strictly as JSON** in this format:
{{
  "column_name1": "PII" or "Not PII",
  "column_name2": "PII" or "Not PII",
  ...
}}

List of column names to classify:
{columns_to_classify}
"""

    # ---------- CALL GEMMA 3 27B IT ----------
    response = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    result_text = response.choices[0].message.content

    # Try parsing JSON safely
    try:
        result_json = json.loads(result_text)
    except json.JSONDecodeError:
        print(f"⚠️ Model output not valid JSON in sheet {sheet_name}:\n{result_text}")
        continue

    # Store with sheet context
    for col, label in result_json.items():
        all_results.append({
            "sheet": sheet_name,
            "column_name": col,
            "classification": label
        })

# ---------- SAVE FINAL RESULTS ----------
final_df = pd.DataFrame(all_results)
final_df.to_excel("PII_classification_results.xlsx", index=False)

print("✅ Classification complete. Results saved to 'PII_classification_results.xlsx'")