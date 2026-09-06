Call Quality Automation

End-to-End Process Overview

1. Purpose

The Call Quality Automation solution automates the evaluation of customer-agent interactions. The process takes call information from the source system, converts the interaction into a PII-removed transcript, evaluates the agent’s performance against defined quality parameters, and generates a consolidated analytics report.

The overall process consists of three major pipelines:

Audio Ingestion → Transcription & Diarization → Analytics & Evaluation

⸻

2. High-Level Process Flow

Verint System
↓
Audio Ingestion Pipeline
↓
Transcription Module
↓
Diarization Module
↓
PII Removal / Sanitization
↓
PII-Removed Transcript
↓
Analytics Pipeline
↓
Evaluation Across 21 Parameters
↓
Final Analytics Report

⸻

3. Audio Ingestion Pipeline

Objective

The Audio Ingestion Pipeline is responsible for retrieving the required call audio information from the Verint system through the available API interface and making it available for downstream processing.

Process

1. The pipeline initiates an API request to the Verint system.
2. Required call information is retrieved based on the configured criteria.
3. The retrieved call information is passed to the downstream processing workflow.
4. Processing status and relevant metadata are maintained to support pipeline execution and tracking.
5. Once the ingestion process is successfully completed, the call proceeds to the Transcription Pipeline.

Input

* Call audio from Verint
* Relevant call metadata

Output

* Call data ready for transcription and subsequent processing

⸻

4. Transcription Pipeline

Objective

The Transcription Pipeline converts the call interaction into a structured, speaker-aware transcript while ensuring that Personally Identifiable Information (PII) is removed from the transcript before it is used for analytics.

The pipeline consists primarily of two processing modules:

* Transcription Module
* Diarization Module

Process

1. The call audio received from the ingestion stage is passed to the Transcription Module.
2. The Transcription Module converts the spoken conversation into textual content.
3. The Diarization Module identifies and separates the conversation based on speakers.
4. Speaker attribution is applied to distinguish the agent’s conversation from the customer’s conversation.
5. The generated transcript goes through the required PII removal/sanitization process.
6. Sensitive information is removed or masked from the transcript.
7. The resulting transcript becomes the standardized input for the Analytics Pipeline.

Input

* Call audio
* Call metadata

Output

* Speaker-separated, PII-removed transcript

Key Outcome

The output of this pipeline is a structured and PII-removed transcript that can be safely passed to the analytics stage for quality evaluation.

⸻

5. Analytics Pipeline

Objective

The Analytics Pipeline evaluates the agent’s performance based on the PII-removed transcript and generates a comprehensive quality assessment.

Process

1. The PII-removed transcript is received from the Transcription Pipeline.
2. The transcript is processed by the Analytics Pipeline.
3. The agent-customer interaction is evaluated against 21 predefined quality parameters.
4. Each parameter is analyzed based on the conversation context and applicable evaluation criteria.
5. Individual parameter-level results are generated.
6. The results are consolidated to create an overall assessment of the interaction.
7. The processed results are compiled into the final analytics report.

Input

* PII-removed transcript
* Defined quality parameters and evaluation criteria

Output

* Parameter-level evaluation results
* Consolidated analytics results
* Final analytics report

⸻

6. Agent Evaluation – 21 Parameters

The Analytics Pipeline evaluates the agent interaction across 21 predefined quality parameters.

The evaluation framework is designed to assess different aspects of the agent’s interaction with the customer. Each parameter is independently evaluated according to its applicable business rules and evaluation criteria.

The evaluation produces:

* Parameter name
* Evaluation result
* Supporting conversation context, where applicable
* Parameter-level outcome
* Overall consolidated assessment

The individual parameter results are subsequently aggregated into the final analytics report.

⸻

7. Final Analytics Report

The final output of the Call Quality Automation process is an analytics report containing the results of the automated agent evaluation.

The report provides a consolidated view of:

* Call-level information
* Agent evaluation results
* Results for each of the 21 quality parameters
* Relevant observations/evidence from the conversation
* Overall quality assessment
* Applicable scores or outcomes

The report enables quality teams and business stakeholders to review agent performance without manually analyzing each call.

⸻

8. End-to-End Process Summary

Stage	Pipeline/Module	Key Activity	Output
1	Audio Ingestion	Retrieve call audio through Verint API	Call data for processing
2	Transcription	Convert conversation audio into text	Transcript
3	Diarization	Identify and separate speakers	Speaker-aware transcript
4	PII Sanitization	Remove/mask PII from transcript	PII-removed transcript
5	Analytics	Evaluate agent interaction	Parameter-level results
6	Agent Evaluation	Assess 21 quality parameters	Evaluation outcomes
7	Report Generation	Consolidate evaluation results	Final analytics report

⸻

9. Overall Process

The Call Quality Automation solution follows a sequential processing workflow:

Verint System
→ Audio Ingestion
→ Transcription
→ Diarization
→ PII Removal
→ PII-Removed Transcript
→ Analytics Processing
→ Evaluation of 21 Parameters
→ Result Consolidation
→ Final Analytics Report

This automated workflow minimizes manual intervention in the call quality assessment process and provides a standardized approach for evaluating agent interactions across the defined quality parameters.

⸻

10. Pipeline Responsibilities

Audio Ingestion Pipeline

Primary responsibility:
Retrieve call audio and associated information from the Verint system through API integration.

Transcription Pipeline

Primary responsibility:
Convert call audio into a structured, speaker-aware and PII-removed transcript.

Analytics Pipeline

Primary responsibility:
Analyze the transcript against the defined 21 quality parameters and generate the final evaluation report.

Final Outcome

Automated Call → PII-Removed Transcript → 21-Parameter Evaluation → Analytics Report