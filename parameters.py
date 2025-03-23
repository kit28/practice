from openai import OpenAI
from os import listdir
from os.path import isfile, join

instruction = f"""You are given a call transcript of a conversation between a customer and an agent, delimited by <transcript></transcript>.
Your job is to analyse the transcript and evaluate the performance of the agent out of 10, based on the following parameters <evaluation_parameter></evaluation_parameter>
Strictly reply in JSON format only, with keys 
<response_format>""" +"""\n{"evaluation":7/10 , "reason":"appropriate reasoning for your evaluation"}
</response_format>
Strictly do not generate anything else than a JSON output."""

transcript_file = "cleaned_transcript.txt"
with open(transcript_file, "r") as f:
    transcript_text = f.read()
    
ques_file_path = "prompts/"
ques_file_list = [join(ques_file_path, f) for f in listdir(ques_file_path) if isfile(join(ques_file_path, f))]

def load_llm():
    openai_api_key = "EMPTY"
    openai_api_base = "http://0.0.0.0:8000/v1"
    client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )
    return client

def generate_llm_response(client, prompt):
    chat_response = client.chat.completions.create(
        model="ibm-granite/granite-3.1-8b-instruct",
        temperature=0.1,
        messages=[
            {"role": "system", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    res = chat_response.choices[0].message.content
    return res
