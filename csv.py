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