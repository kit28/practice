import os
import openai
import yaml
import pandas as pd
from flask import Flask, request, jsonify, send_file
from io import BytesIO

app = Flask(__name__)

openai.api_key = 'YOUR_OPENAI_API_KEY'

QUESTION_FILES = [f"prompts/question_{i}.yaml" for i in range(1, 6)]

def load_and_prepare_prompts(transcript):
    prompts = []
    for file in QUESTION_FILES:
        with open(file, 'r') as stream:
            data = yaml.safe_load(stream)
            # Replace placeholder with actual transcript
            full_prompt = f"{data['question']}\n\n{data['examples']}\n\nTranscript:\n{transcript}\n"
            prompts.append(full_prompt)
    return prompts

def generate_llm_response(prompt):
    # Replace with your actual LLM call logic
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

def create_excel_report(analysis_data):
    df = pd.DataFrame(analysis_data, columns=['Question', 'Analysis'])
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Agent Analysis')
    output.seek(0)
    return output

@app.route('/analyze', methods=['POST'])
def analyze_transcript():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    transcript_file = request.files['file']
    transcript_text = transcript_file.read().decode('utf-8')

    # Prepare each YAML-based question prompt
    question_prompts = load_and_prepare_prompts(transcript_text)

    analysis_data = []
    for i, prompt in enumerate(question_prompts):
        response = generate_llm_response(prompt)
        analysis_data.append((f"Q{i+1}", response))

    # Generate Excel
    excel_output = create_excel_report(analysis_data)

    return send_file(
        excel_output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='agent_analysis.xlsx'
    )

if __name__ == '__main__':
    app.run(debug=True)

#curl -X POST http://localhost:5000/analyze -F "file=@transcript.txt" --output agent_analysis.xlsx

