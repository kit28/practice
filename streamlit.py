import pandas as pd

# File paths
file_a = "A.xlsx"
file_b = "B.xlsx"

# Read Excel files
df_a = pd.read_excel(file_a)
df_b = pd.read_excel(file_b)

# Get unique IDs from A
ids_a = set(df_a["ID"].dropna().astype(str).str.strip())

# Get unique User Acc Names from B
ids_b = set(df_b["User Acc Name"].dropna().astype(str).str.strip())

# Find IDs present in B but NOT in A
ids_only_in_b = sorted(ids_b - ids_a)

# Create output DataFrame
result = pd.DataFrame({"User ID": ids_only_in_b})

# Save to a new Excel file
output_file = "IDs_in_B_not_in_A.xlsx"
result.to_excel(output_file, index=False)

print(f"Found {len(ids_only_in_b)} unique IDs.")
print(f"Output saved to: {output_file}")