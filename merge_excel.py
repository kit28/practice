import pandas as pd

# Read files
df_qwen = pd.read_excel("qwen_transcriptions.xlsx")
df_feedback = pd.read_excel("feedback.xlsx")

# Clean column names (important)
df_qwen.columns = df_qwen.columns.str.strip()
df_feedback.columns = df_feedback.columns.str.strip()

# Keep only required columns
df_qwen = df_qwen[
    ["audio_names", "qwen_transcription", "LLM_translation"]
]

df_feedback = df_feedback[
    ["audio_names", "Business_feedback"]
]

# Remove any leading/trailing spaces in audio names
df_qwen["audio_names"] = df_qwen["audio_names"].astype(str).str.strip()
df_feedback["audio_names"] = df_feedback["audio_names"].astype(str).str.strip()

# Merge
merged_df = df_qwen.merge(
    df_feedback,
    on="audio_names",
    how="left"
)

# Save output
merged_df.to_excel(
    "merged_output.xlsx",
    index=False
)

print(f"Rows in output: {len(merged_df)}")
print("Saved to merged_output.xlsx")