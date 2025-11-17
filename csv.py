import os
import csv

# --- CONFIG ---
pdf_folder = "path/to/your/folder"  # Replace with your actual folder path
output_csv = "pdf_file_list.csv"

# --- Get PDF filenames ---
pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")]

# --- Write to CSV ---
with open(output_csv, mode="w", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Filename"])
    for pdf in pdf_files:
        writer.writerow([pdf])

print(f"CSV created with {len(pdf_files)} PDF files.")


def load_reference_examples(
    path: str,
    sheet_name: str,
    column_field: str,
    description_field: Optional[str],
    filter_column: Optional[str] = None   # 👈 new param
) -> List[ReferenceExample]:

    df = pd.read_excel(path, sheet_name=sheet_name)

    if column_field not in df.columns:
        raise ValueError(f"Reference sheet '{sheet_name}' missing column '{column_field}'")

    # Identify description column if provided
    desc_col = description_field if description_field and description_field in df.columns else None

    # Validate filter column
    if filter_column and filter_column not in df.columns:
        raise ValueError(f"Filter column '{filter_column}' not found in sheet '{sheet_name}'")

    examples = []

    for _, row in df.iterrows():

        # -----------------------------
        # FILTER LOGIC
        # include row ONLY if filter_column == "true"
        # -----------------------------
        if filter_column:
            val = str(row[filter_column]).strip().lower()
            if val != "true":
                continue  # skip this row

        # Main column
        col = str(row[column_field]).strip()
        if not col:
            continue

        # Description
        desc = None
        if desc_col:
            val = row[desc_col]
            desc = None if pd.isna(val) else str(val).strip()

        examples.append(
            ReferenceExample(column_name=col, description=desc or "")
        )

    if not examples:
        raise ValueError("Reference examples list is empty")

    return examples