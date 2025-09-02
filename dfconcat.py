import os
import pandas as pd

# Folder path
folder_path = "path/to/your/folder"

# List all Excel files in folder
files = [f for f in os.listdir(folder_path) if f.endswith((".xlsx", ".xls"))]

# If no files found
if not files:
    print("No Excel files found in the folder.")
else:
    dfs = []
    for file in files:
        file_path = os.path.join(folder_path, file)
        try:
            df = pd.read_excel(file_path)
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    if dfs:  # Only if there are valid dataframes
        final_df = pd.concat(dfs, ignore_index=True)
        output_path = os.path.join(folder_path, "combined_output.xlsx")
        final_df.to_excel(output_path, index=False)
        print(f"Combined file saved at: {output_path}")
    else:
        print("No valid Excel data to combine.")