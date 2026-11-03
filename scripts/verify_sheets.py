import openpyxl

wb = openpyxl.load_workbook("HireX_Complete_Test_Cases.xlsx")
print("Total sheets:", len(wb.sheetnames))
total_rows = 0
for name in wb.sheetnames:
    ws = wb[name]
    # Rows start at 9
    tc_count = max(0, ws.max_row - 8)
    total_rows += tc_count
print("Total test case rows across all sheets:", total_rows)

