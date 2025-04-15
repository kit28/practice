import streamlit as st
import os
import tempfile
import shutil
from whisper_transcribe import WhisperTranscriber
from translation import JSONToSRTTranslator
from diarization import DiarizationProcessor
from analytics import analyze_transcript
from logger import setup_logging, log_gpu_usage
import logging
import uuid

# Set up logging
logger = logging.getLogger(__name__)

def process_audio_file(audio_path, base_output_dir, prompts_folder="prompts"):
    """
    Processes a single audio file and returns the path to the generated CSV report.
    """
    session_id = uuid.uuid4().hex
    output_folder = os.path.join(base_output_dir, session_id, "output")
    log_folder = os.path.join(base_output_dir, session_id, "logs")

    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(log_folder, exist_ok=True)
    setup_logging(log_folder)

    try:
        # Initialize pipeline components
        transcriber = WhisperTranscriber()
        translator = JSONToSRTTranslator()
        diarizer = DiarizationProcessor()

        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        transcription_json = os.path.join(output_folder, f"{base_name}_transcription.json")
        translation_txt = os.path.join(output_folder, f"{base_name}_translation.txt")
        diarization_txt = os.path.join(output_folder, f"{base_name}_diarization.txt")
        analytics_csv = os.path.join(output_folder, f"{base_name}_analytics.csv")

        # Transcription
        transcription_data = transcriber.transcribe(audio_path)
        transcriber.save_to_json(transcription_data, transcription_json)

        # Translation
        translator.set_input_file(transcription_json)
        translator.convert_to_srt()
        translator.translate()
        translator.save_translation(translation_txt)

        # Diarization
        diarizer.set_input_file(translation_txt)
        diarizer.process_diarization()
        diarizer.save_output(diarization_txt)

        # Analytics
        analytic_prompt_folder = os.path.join(prompts_folder, "analytic_prompt")
        question_files = [os.path.join(analytic_prompt_folder, f) for f in os.listdir(analytic_prompt_folder)
                          if os.path.isfile(os.path.join(analytic_prompt_folder, f)) and f.endswith('.yaml')]
        result = analyze_transcript(diarization_txt, analytics_csv, question_files)
        if "error" in result:
            raise RuntimeError(result["error"])

        return analytics_csv

    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        raise e

# Streamlit UI
st.title("Audio Analytics Report Generator")

uploaded_file = st.file_uploader("Upload a WAV audio file", type=["wav"])

if uploaded_file:
    with st.spinner("Processing audio..."):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                audio_path = os.path.join(tmpdir, uploaded_file.name)
                with open(audio_path, "wb") as f:
                    f.write(uploaded_file.read())

                analytics_csv_path = process_audio_file(audio_path, tmpdir)

                with open(analytics_csv_path, "rb") as f:
                    st.success("Report generated successfully!")
                    st.download_button(
                        label="Download Analytics CSV",
                        data=f,
                        file_name=os.path.basename(analytics_csv_path),
                        mime="text/csv"
                    )

        except Exception as e:
            st.error(f"Failed to process the file: {str(e)}")