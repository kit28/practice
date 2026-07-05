import os
import pandas as pd

# ==========================
# INPUTS
# ==========================

EXCEL_FILE = r"final_feedback_report.xlsx"
AUDIO_FOLDER = r"audio_calls"
OUTPUT_FILE = r"filtered_feedback_report.xlsx"

# ==========================
# GET UNIVERSAL IDs FROM WAV FILES
# ==========================

audio_ids = {
    os.path.splitext(f)[0].strip()
    for f in os.listdir(AUDIO_FOLDER)
    if f.lower().endswith(".wav")
}

print(f"Found {len(audio_ids)} audio files.")

# ==========================
# READ EXCEL
# ==========================

df = pd.read_excel(
    EXCEL_FILE,
    sheet_name="Merged Feedback",   # remove this line if only one sheet exists
    dtype={"Universal_ID": str}
)

# Force Universal_ID to string
df["Universal_ID"] = (
    df["Universal_ID"]
    .astype(str)
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
)

# ==========================
# FILTER
# ==========================

filtered_df = df[df["Universal_ID"].isin(audio_ids)].copy()

# Keep as string
filtered_df["Universal_ID"] = filtered_df["Universal_ID"].astype(str)

# ==========================
# SAVE
# ==========================

with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    filtered_df.to_excel(writer, sheet_name="Merged Feedback", index=False)

print(f"Rows before : {len(df)}")
print(f"Rows after  : {len(filtered_df)}")
print(f"Saved to: {OUTPUT_FILE}")