import pandas as pd
from io import BytesIO

# def create_excel_report(analysis_data):
#     df = pd.DataFrame(analysis_data, columns=['Question', 'Weightage', 'Evaluation', 'Reason', 'Score'])
    
#     output = BytesIO()
#     with pd.ExcelWriter(output, engine='openpyxl') as writer:
#         df.to_excel(writer, index=False, sheet_name='Agent Analysis')
#     output.seek(0)
#     return output

def create_excel_report(analysis_data):
    df = pd.DataFrame(analysis_data, columns=['Question', 'Weightage', 'Evaluation', 'Reason', 'Score'])
    df.to_csv("output.csv", index=False)

    return