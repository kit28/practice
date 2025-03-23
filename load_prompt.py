import yaml
import parameters

def load_and_prepare_prompts(transcript, question_file_list):
    prompts = []
    question_weightage_list = []
    actual_ques_list = []
    for file in question_file_list:
        with open(file, 'r') as stream:
            data = yaml.safe_load(stream)
            # Replace placeholder with actual transcript
            full_prompt = parameters.instruction + f"""\n
<evaluation_parameter>
Question: {data['question']}
Example: {data['examples']}
</evaluation_parameter>

<transcript>
{transcript}
</transcript>"""

            #print("\n\nprompt:::",full_prompt)
            prompts.append(full_prompt)
            question_weightage_list.append(data['weightage'])
            actual_ques_list.append(data['question'])
    return prompts, question_weightage_list, actual_ques_list