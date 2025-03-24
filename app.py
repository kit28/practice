from flask import Flask, request, jsonify, send_file
import json
import ast
import parameters
from load_prompt import load_and_prepare_prompts
from create_excel import create_excel_report

# app = Flask(__name__)
client = parameters.load_llm()

#@app.route('/analyze', methods=['POST'])
def analyze_transcript():
    ques_prompt_list, ques_weightage_list, actual_ques_list = load_and_prepare_prompts(parameters.transcript_text, parameters.ques_file_list)

    analysis_data = []
    for prompt, weight, ques in zip(ques_prompt_list, ques_weightage_list, actual_ques_list):
        response = parameters.generate_llm_response(client, prompt)
        response = json.loads(response)
        analysis_data.append((ques, weight, response['evaluation'], response['reason'], float(0.1*response['evaluation'])*float(weight)))

    create_excel_report(analysis_data)
    return analysis_data


print(analyze_transcript())

# if __name__ == '__main__':
#     app.run(debug=True)

curl -X POST "http://localhost:8000/analyze/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@transcript.txt"
