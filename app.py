from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
import json
import ast
import parameters
from load_prompt import load_and_prepare_prompts
from create_excel import create_excel_report

app = FastAPI()
client = parameters.load_llm()
# client = ""

@app.post("/analyze")
def analyze_transcript(request_data: dict):
    transcript_txt_path = request_data.get("file_path")
    ques_prompt_list, ques_weightage_list, actual_ques_list = load_and_prepare_prompts(transcript_txt_path, parameters.ques_file_list)
    
    analysis_data = []
    for prompt, weight, ques in zip(ques_prompt_list, ques_weightage_list, actual_ques_list):
        response = parameters.generate_llm_response(client, prompt)
        #print("\n Response:::", response)
        
        response = json.loads(response)
        print("\n Response:::", response)
        
        eval_score = round(float(response['evaluation']),2)
        threshold_score = parameters.threshold_score
        effective_weight = round(float(0.1*response['evaluation'])*float(weight),2)
        final_score = weight if eval_score >= threshold_score else 0
        final_verdict = "good" if eval_score >= threshold_score else "bad"
        analysis_data.append((ques, weight, eval_score, response['reason'], threshold_score, effective_weight, final_score, final_verdict))

    create_excel_report(analysis_data)
    return JSONResponse(content={"message":"Analysis completed"})


# print(analyze_transcript())

# if __name__ == '__main__':
#     app.run(debug=True)
