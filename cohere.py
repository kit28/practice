import os
import logging
from openai import OpenAI


class CohereTranscriber:
    """
    Cohere ASR transcription module.

    Uses Cohere Transcribe Arabic model hosted through vLLM
    and exposes a simple transcribe() interface to the pipeline.
    """

    def __init__(
        self,
        base_url: str,
        model_name: str,
        language: str = "ar",
        api_key: str = "dummy",
    ):
        self.logger = logging.getLogger(__name__)

        self.base_url = base_url
        self.model_name = model_name
        self.language = language

        self.client = OpenAI(
            base_url=self.base_url,
            api_key=api_key,
        )

        self.logger.info(
            f"Cohere ASR initialized: {self.model_name}"
        )

    def transcribe(self, audio_file: str) -> str:
        """
        Transcribe a single audio file.

        Parameters
        ----------
        audio_file : str
            Path to the audio file.

        Returns
        -------
        str
            Raw Arabic transcription.
        """

        if not os.path.exists(audio_file):
            raise FileNotFoundError(
                f"Audio file not found: {audio_file}"
            )

        self.logger.info(
            f"Starting Cohere transcription: {audio_file}"
        )

        try:
            with open(audio_file, "rb") as audio:

                transcription = self.client.audio.transcriptions.create(
                    model=self.model_name,
                    file=audio,
                    language=self.language,
                )

            transcript = transcription.text

            if not transcript:
                self.logger.warning(
                    f"Empty transcription returned: {audio_file}"
                )
                return ""

            transcript = transcript.strip()

            self.logger.info(
                f"Cohere transcription completed: {audio_file}"
            )

            return transcript

        except Exception as e:

            self.logger.exception(
                f"Cohere transcription failed: {audio_file}"
            )

            raise RuntimeError(
                f"Cohere transcription failed for "
                f"{audio_file}: {str(e)}"
            ) from e


###### connfig ###################

COHERE_ASR_URL = "http://localhost:8006/v1"

COHERE_ASR_MODEL = (
    "cohere-transcribe-arabic-07-2026"
)

COHERE_ASR_LANGUAGE = "ar"

############################################

########## Translation ###################

import logging
from openai import OpenAI


class CallTranslator:
    """
    Translation and speaker diarization module.

    Takes Arabic ASR transcription and generates
    an English Agent/Customer conversation.
    """

    def __init__(
        self,
        base_url: str,
        model_name: str,
        api_key: str = "EMPTY",
    ):
        self.logger = logging.getLogger(__name__)

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        self.model_name = model_name

        self.logger.info(
            f"Translator initialized: {self.model_name}"
        )

    def translate_and_diarize(
        self,
        arabic_transcript: str,
    ) -> str:

        if not arabic_transcript:
            self.logger.warning(
                "Empty Arabic transcript received."
            )
            return ""

        prompt = f"""
You are a banking call analyst.

The following is an Arabic call transcription generated
by an ASR model.

Context:
- The call is between a Saudi Awwal Bank (SAB) support
  agent and a customer.
- The transcription may contain minor ASR errors.
- Infer speaker turns where possible.
- Translate the conversation into fluent English.
- Assign each speaker as either:
  Agent:
  Customer:

Instructions:

1. Correct obvious ASR errors only when the intended
   meaning is clear.

2. Preserve the original meaning exactly.

3. Do not add information that is not present in the
   transcription.

4. Identify speaker turns as:
   Agent:
   Customer:

5. If speaker boundaries are unclear, make the most
   reasonable inference based on conversational context.

6. Strictly preserve standard opening scripts.

7. Strictly preserve standard closing scripts.

8. Arabic names must NOT be translated into their
   literal English meanings. Preserve names as names.

9. Do not summarize the conversation.

10. Do not omit meaningful customer or agent statements.

11. Return ONLY the translated and diarized conversation.

Arabic Transcript:
{arabic_transcript}
"""

        try:

            response = self.client.chat.completions.create(
                model=self.model_name,
                temperature=0.1,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert Arabic-English "
                            "banking call translator and "
                            "conversation diarization assistant."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )

            result = response.choices[0].message.content

            if not result:
                self.logger.warning(
                    "LLM returned empty translation."
                )
                return ""

            return result.strip()

        except Exception as e:

            self.logger.exception(
                "Translation and diarization failed."
            )

            raise RuntimeError(
                f"Translation/diarization failed: {str(e)}"
            ) from e


##########################################################################
 ############## pipeline ########################

for audio_file in audio_path_list:

    try:

        # =====================================================
        # FILE PATHS
        # =====================================================

        base_name = os.path.splitext(
            os.path.basename(audio_file)
        )[0]

        transcription_txt = os.path.join(
            output_folder,
            f"{base_name}_transcription.txt"
        )

        diarization_txt = os.path.join(
            output_folder,
            f"{base_name}_diarization.txt"
        )

        analytics_csv = os.path.join(
            DETAILED_DIR,
            f"{base_name}_analytics.xlsx"
        )

        # =====================================================
        # AUDIO CONVERSION
        # =====================================================

        audio_file = convert_single_audio(
            audio_file,
            pcm_folder
        )

        # =====================================================
        # TRANSCRIPTION
        # =====================================================

        logger.info(
            f"Starting Cohere transcription for {base_name}"
        )

        arabic_transcription = transcriber.transcribe(
            audio_file
        )

        # Save raw Arabic transcription
        with open(
            transcription_txt,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(arabic_transcription)

        logging.getLogger().handlers[1].flush()

        logger.info(
            f"Transcription saved to "
            f"{transcription_txt}\n"
        )

        # =====================================================
        # TRANSLATION + DIARIZATION
        # =====================================================

        logger.info(
            f"Starting translation and diarization "
            f"for {base_name}"
        )

        diarized_transcript = translator.translate_and_diarize(
            arabic_transcription
        )

        # Save translated + diarized conversation
        with open(
            diarization_txt,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(diarized_transcript)

        logging.getLogger().handlers[1].flush()

        logger.info(
            f"Translation/diarization saved to "
            f"{diarization_txt}\n"
        )

        # =====================================================
        # VAD
        # =====================================================

        silence_flags, total_duration_seconds = vad_predict(
            audio_file
        )

        # =====================================================
        # ANALYTICS
        # =====================================================

        logger.info(
            f"Starting analytics for {base_name}"
        )

        ## analytics pipeline called here

    except Exception as e:

        logger.exception(
            f"Pipeline failed for {audio_file}: {str(e)}"
        )


