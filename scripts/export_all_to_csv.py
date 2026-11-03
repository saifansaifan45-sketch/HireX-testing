"""
Export all HireX QA Excel Workbooks to Google Sheets-compatible CSV format (UTF-8-SIG).
Generates:
1. HireX_Defect_Report.csv
2. HireX_Executed_Test_Cases.csv
3. HireX_Complete_Test_Cases.csv (All 540 test cases with Module column)
4. HireX_DOM_Element_Inventory.csv
5. HireX_Locator_Inventory.csv
6. HireX_Application_Inventory.csv
7. HireX_Requirements_Traceability_Matrix.csv
"""
import openpyxl
import csv
import os

OUTPUT_DIR = "."
CSV_REPORTS_DIR = "csv_reports"
os.makedirs(CSV_REPORTS_DIR, exist_ok=True)
os.makedirs(os.path.join(CSV_REPORTS_DIR, "modules"), exist_ok=True)


def convert_sheet_to_csv(sheet, output_csv_path, skip_rows=0):
    with open(output_csv_path, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        for r_idx, row in enumerate(sheet.iter_rows(values_only=True), start=1):
            if r_idx <= skip_rows:
                continue
            # Filter out completely empty rows
            if any(cell is not None and str(cell).strip() != "" for cell in row):
                cleaned_row = [str(cell) if cell is not None else "" for cell in row]
                writer.writerow(cleaned_row)
    print(f"[CSV EXPORT] Generated: {output_csv_path}")


def export_all():
    # 1. Defect Report
    if os.path.exists("HireX_Defect_Report.xlsx"):
        wb = openpyxl.load_workbook("HireX_Defect_Report.xlsx")
        ws = wb.active
        # Skip row 1 (meta banner), row 2 is column headers
        convert_sheet_to_csv(ws, "HireX_Defect_Report.csv", skip_rows=1)
        convert_sheet_to_csv(ws, os.path.join(CSV_REPORTS_DIR, "HireX_Defect_Report.csv"), skip_rows=1)

    # 2. Executed Test Cases
    if os.path.exists("HireX_Executed_Test_Cases.xlsx"):
        wb = openpyxl.load_workbook("HireX_Executed_Test_Cases.xlsx")
        ws = wb.active
        convert_sheet_to_csv(ws, "HireX_Executed_Test_Cases.csv", skip_rows=1)
        convert_sheet_to_csv(ws, os.path.join(CSV_REPORTS_DIR, "HireX_Executed_Test_Cases.csv"), skip_rows=1)

    # 3. Application Surface Inventory
    if os.path.exists("HireX_Application_Inventory.xlsx"):
        wb = openpyxl.load_workbook("HireX_Application_Inventory.xlsx")
        ws = wb.active
        convert_sheet_to_csv(ws, "HireX_Application_Inventory.csv", skip_rows=1)
        convert_sheet_to_csv(ws, os.path.join(CSV_REPORTS_DIR, "HireX_Application_Inventory.csv"), skip_rows=1)

    # 4. DOM Element Inventory
    if os.path.exists("HireX_DOM_Element_Inventory.xlsx"):
        wb = openpyxl.load_workbook("HireX_DOM_Element_Inventory.xlsx")
        ws = wb.active
        convert_sheet_to_csv(ws, "HireX_DOM_Element_Inventory.csv", skip_rows=1)
        convert_sheet_to_csv(ws, os.path.join(CSV_REPORTS_DIR, "HireX_DOM_Element_Inventory.csv"), skip_rows=1)

    # 5. Locator Inventory
    if os.path.exists("HireX_Locator_Inventory.xlsx"):
        wb = openpyxl.load_workbook("HireX_Locator_Inventory.xlsx")
        ws = wb.active
        convert_sheet_to_csv(ws, "HireX_Locator_Inventory.csv", skip_rows=1)
        convert_sheet_to_csv(ws, os.path.join(CSV_REPORTS_DIR, "HireX_Locator_Inventory.csv"), skip_rows=1)

    # 6. Requirements Traceability Matrix
    if os.path.exists("HireX_Requirements_Traceability_Matrix.xlsx"):
        wb = openpyxl.load_workbook("HireX_Requirements_Traceability_Matrix.xlsx")
        ws = wb.active
        # Headers are on row 8
        convert_sheet_to_csv(ws, "HireX_Requirements_Traceability_Matrix.csv", skip_rows=7)
        convert_sheet_to_csv(ws, os.path.join(CSV_REPORTS_DIR, "HireX_Requirements_Traceability_Matrix.csv"), skip_rows=7)

    # 7. Complete Test Cases (Master CSV combining all 30 module sheets)
    if os.path.exists("HireX_Complete_Test_Cases.xlsx"):
        wb = openpyxl.load_workbook("HireX_Complete_Test_Cases.xlsx")
        master_csv_path = "HireX_Complete_Test_Cases.csv"
        master_csv_copy = os.path.join(CSV_REPORTS_DIR, "HireX_Complete_Test_Cases.csv")

        headers = ["Module", "TC_ID", "Scenario Description", "Preconditions", "Test_Data", "Expected Result", "Actual Result", "Status", "Priority"]
        
        all_rows = []
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            # Also export individual sheet CSV
            safe_name = sheet_name.replace(" ", "_")
            module_csv_path = os.path.join(CSV_REPORTS_DIR, "modules", f"{safe_name}.csv")
            convert_sheet_to_csv(ws, module_csv_path, skip_rows=7)

            # Rows start at row 9 (1-indexed)
            for row in ws.iter_rows(min_row=9, values_only=True):
                if any(cell is not None and str(cell).strip() != "" for cell in row):
                    all_rows.append([sheet_name] + [str(c) if c is not None else "" for c in row[:8]])

        for target in [master_csv_path, master_csv_copy]:
            with open(target, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(all_rows)
            print(f"[CSV EXPORT] Generated Master Test Cases CSV ({len(all_rows)} rows): {target}")


if __name__ == "__main__":
    export_all()

