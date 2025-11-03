import pandas as pd
import json
from openai import OpenAI

# ---------- CONFIG ----------
client = OpenAI(api_key="your_api_key_here")   # adjust if using another LLM API
data_file = "your_excel_with_multiple_sheets.xlsx"
pii_ref_file = "pii_reference.xlsx"
chunk_size = 100  # max number of values per LLM call

# ---------- LOAD PII REFERENCE ----------
pii_ref = pd.read_excel(pii_ref_file)

# Clean and strip values
pii_ref['name'] = pii_ref['name'].astype(str).str.strip()
pii_ref['definition'] = pii_ref['definition'].astype(str).str.strip()

pii_context = "\n".join([
    f"{row['name']}: {row['definition']}"
    for _, row in pii_ref.iterrows()
])

# ---------- READ MULTIPLE SHEETS ----------
xls = pd.ExcelFile(data_file)
all_results = []

for sheet_name in xls.sheet_names:
    df = pd.read_excel(data_file, sheet_name=sheet_name)

    # Skip sheets without the target column
    if 'ColumnName' not in df.columns:
        continue

    # Get unique, cleaned values to classify
    all_column_values = (
        df['ColumnName']
        .dropna()
        .astype(str)
        .map(str.strip)
        .unique()
        .tolist()
    )
    if not all_column_values:
        continue

    print(f"\n🧾 Processing sheet: {sheet_name} with {len(all_column_values)} values")

    sheet_results = {}

    # ---------- PROCESS IN CHUNKS ----------
    for i in range(0, len(all_column_values), chunk_size):
        chunk = all_column_values[i:i + chunk_size]

        # Re-strip again in case of any weird characters
        chunk = [c.strip() for c in chunk if c.strip()]

        if not chunk:
            continue

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
{chunk}
"""

        # ---------- CALL GEMMA MODEL ----------
        response = client.chat.completions.create(
            model="google/gemma-3-27b-it",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        result_text = response.choices[0].message.content

        # ---------- PARSE JSON SAFELY ----------
        try:
            result_json = json.loads(result_text)
            # Clean returned keys as well
            result_json = {k.strip(): v.strip() for k, v in result_json.items()}
            sheet_results.update(result_json)
        except json.JSONDecodeError:
            print(f"⚠️ Invalid JSON in sheet {sheet_name} (chunk starting at index {i})")
            print(result_text[:400])
            continue

    # ---------- STORE RESULTS ----------
    for col, label in sheet_results.items():
        all_results.append({
            "sheet": sheet_name,
            "column_name": col.strip(),
            "classification": label.strip()
        })

# ---------- SAVE FINAL RESULTS ----------
final_df = pd.DataFrame(all_results)
final_df.to_excel("PII_classification_results.xlsx", index=False)

print("\n✅ Classification complete. Results saved to 'PII_classification_results.xlsx'")