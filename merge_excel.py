import pandas as pd
import os
from glob import glob

def merge_excels(input_folder: str, output_file: str):
    # Get all Excel files (.xlsx, .xls)
    excel_files = glob(os.path.join(input_folder, "*.xlsx")) + \
                  glob(os.path.join(input_folder, "*.xls"))

    if not excel_files:
        raise ValueError("No Excel files found in the folder")

    df_list = []

    for file in excel_files:
        df = pd.read_excel(file)
        df_list.append(df)

    merged_df = pd.concat(df_list, ignore_index=True)

    merged_df.to_excel(output_file, index=False)

    print(f"Merged {len(excel_files)} files into {output_file}")