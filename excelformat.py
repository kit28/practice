row = 4

# -------------------------
# Universal ID
# -------------------------
ws.merge_cells(start_row=1, start_column=1,
               end_row=3, end_column=1)

cell = ws.cell(row=1, column=1)
cell.value = "Universal ID"
_style(cell, fill="4F81BD", bold=True)

ws.cell(row=row, column=1).value = uid

# -------------------------
# Overall
# -------------------------
ws.merge_cells(start_row=1, start_column=2,
               end_row=3, end_column=2)

cell = ws.cell(row=1, column=2)
cell.value = "Overall"
_style(cell, fill="4F81BD", bold=True)

ws.cell(row=row, column=2).value = overall_verdict

# Questions start from column C
col = 3


widths[1] = 18      # Universal ID
widths[2] = 12      # Overall

question_end = ws.max_column - 3

for c in range(3, question_end + 1):
    
    