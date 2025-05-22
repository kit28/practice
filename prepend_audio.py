import os
from pydub import AudioSegment

# Paths
prepend_file = "path/to/prepend.wav"
folder_path = "path/to/wav/folder"
output_folder = os.path.join(folder_path, "output")

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Load the file to prepend
prepend_audio = AudioSegment.from_wav(prepend_file)

# Process each .wav file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".wav") and filename != os.path.basename(prepend_file):
        file_path = os.path.join(folder_path, filename)
        original_audio = AudioSegment.from_wav(file_path)

        combined = prepend_audio + original_audio

        output_path = os.path.join(output_folder, filename)
        combined.export(output_path, format="wav")

        print(f"Saved: {output_path}")