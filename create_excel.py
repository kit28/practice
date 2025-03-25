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
    df = pd.DataFrame(analysis_data, columns=['Question', 'Actual_Weightage', 'Evaluation_Score', 'Reason', 'Threshold_value', 'Effective_Weightage', 'Final_Score', 'Final_verdict'])
    df.to_csv("output_final.csv", index=False)

    return
