import os
import shutil

# ===== INPUT FOLDERS =====
folder_83 = r"/path/to/folder_with_83_wavs"
folder_23 = r"/path/to/folder_with_23_wavs"
output_folder = r"/path/to/output_folder"

os.makedirs(output_folder, exist_ok=True)

# Get filenames from the 23-file folder
files_23 = {
    f.lower()
    for f in os.listdir(folder_23)
    if f.lower().endswith(".wav")
}

count = 0

# Copy files that are not in the 23-file folder
for file in os.listdir(folder_83):
    if file.lower().endswith(".wav") and file.lower() not in files_23:
        shutil.copy2(
            os.path.join(folder_83, file),
            os.path.join(output_folder, file)
        )
        count += 1

print(f"Copied {count} files to '{output_folder}'.")