import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

PURPLE_HEADER_FILL = PatternFill(start_color="581C87", end_color="581C87", fill_type="solid")
METADATA_LABEL_FILL = PatternFill(start_color="EDE9FE", end_color="EDE9FE", fill_type="solid")
ZEBRA_FILL = PatternFill(start_color="FAF5FF", end_color="FAF5FF", fill_type="solid")
WHITE_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
BOLD_FONT = Font(name="Calibri", size=11, bold=True, color="000000")
REGULAR_FONT = Font(name="Calibri", size=10, color="000000")

THIN_BORDER = Border(
    left=Side(style='thin', color='D8B4FE'),
    right=Side(style='thin', color='D8B4FE'),
    top=Side(style='thin', color='D8B4FE'),
    bottom=Side(style='thin', color='D8B4FE')
)

HEADER_BORDER = Border(
    left=Side(style='thin', color='4C1D95'),
    right=Side(style='thin', color='4C1D95'),
    top=Side(style='thin', color='4C1D95'),
    bottom=Side(style='medium', color='3B0764')
)

RTM_REQS = [
    # (Req_ID, Module, Requirement_Title, Test_Case_IDs, Test_Type, Priority, Automation_Status)
    ("FR-001", "Authentication", "Multi-Role Credential Authentication", "TC_HX_AUTH_001, TC_HX_AUTH_002, TC_HX_AUTH_004, TC_HX_AUTH_005, TC_HX_AUTH_006", "Functional / Security", "P1", "Automated"),
    ("FR-002", "Security / RBAC", "Portal Session Isolation Guard (ADR-001)", "TC_HX_AUTH_004, TC_HX_SEC_001, TC_HX_SEC_002", "Security / Negative", "P1", "Automated"),
    ("FR-003", "Authentication", "Interviewer Magic Link / Invite Token Redemption", "TC_HX_AUTH_007, TC_HX_AUTH_008", "Functional / Security", "P1", "Automated"),
    ("FR-004", "Candidate Portal", "Multivariable Job Search & Filtering", "TC_HX_CP_001, TC_HX_CP_002, TC_HX_CP_003, TC_HX_REG_002", "Functional / UI", "P2", "Automated"),
    ("FR-005", "Candidate Portal", "Dynamic Application Form Wizard Rendering", "TC_HX_WIZ_001, TC_HX_WIZ_002, TC_HX_FORM_005", "Functional / Dynamic UI", "P1", "Automated"),
    ("FR-006", "Candidate Portal", "Application Draft Autosave & Unsaved Changes Guard", "TC_HX_WIZ_003, TC_HX_WIZ_004", "UX / State Persistence", "P2", "Automated"),
    ("FR-007", "Candidate Applications", "Unauthenticated Guest Candidate Application", "TC_HX_CAND_APP_005", "Functional / Integration", "P1", "Automated"),
    ("FR-008", "Recruiter Portal", "Dynamic Application Form Builder (JSONB Schema)", "TC_HX_FORM_001, TC_HX_FORM_002, TC_HX_FORM_003, TC_HX_FORM_004", "Functional / Data-Driven", "P1", "Automated"),
    ("FR-009", "AI Engine", "AI Resume Match Relevance Scoring (aiScore)", "TC_HX_AI_001, TC_HX_AI_002, TC_HX_AI_003, TC_HX_AI_004", "Functional / Algorithmic", "P2", "Automated"),
    ("FR-010", "Applicant Pipeline", "Strict Forward-Only Pipeline Stage Guard", "TC_HX_PIPE_004", "Business Logic / Security", "P1", "Automated"),
    ("FR-011", "Applicant Pipeline", "Open Interview Pipeline Advance Hard-Block", "TC_HX_PIPE_006", "Business Logic / Constraint", "P1", "Automated"),
    ("FR-012", "Interviewer Workspace", "Weekly Recurring Availability Configuration", "TC_HX_AVAIL_001, TC_HX_AVAIL_002, TC_HX_AVAIL_003, TC_HX_AVAIL_004", "Functional / Data Integrity", "P1", "Automated"),
    ("FR-013", "Interview Scheduling", "Self-Service Slot Booking & Concurrency Guard", "TC_HX_SCHED_003, TC_HX_SCHED_004", "Concurrency / Race Condition", "P1", "Automated"),
    ("FR-014", "Meeting Integration", "MeetX Video Room Generation & URL Privilege Split", "TC_HX_MEET_001, TC_HX_MEET_002, TC_HX_MEET_003", "Integration / WebRTC", "P1", "Automated"),
    ("FR-015", "Interviewer Workspace", "Structured Rubric Scorecard & Cultural Fit Score", "TC_HX_FEED_001, TC_HX_FEED_002, TC_HX_FEED_003, TC_HX_FEED_004", "Functional / Data Integrity", "P1", "Automated"),
    ("FR-016", "Offer Management", "Branded PDF Offer Letter Generation & Placeholders", "TC_HX_OFF_001, TC_HX_OFF_002, TC_HX_OFF_004", "Functional / PDF Generation", "P1", "Automated"),
    ("FR-017", "Offer Management", "Stale Offer Auto-Expiration Cron Job", "TC_HX_OFF_003", "Backend / Asynchronous Cron", "P1", "Automated"),
    ("FR-018", "Document Verification", "Multi-File Compliance Document Upload (Cloudflare R2)", "TC_HX_DOC_001, TC_HX_DOC_005, TC_HX_INTG_004", "Functional / Object Storage", "P1", "Automated"),
    ("FR-019", "Document Verification", "Document Rejection with Reason & Re-Upload Loop", "TC_HX_DOC_002, TC_HX_DOC_003, TC_HX_DOC_004", "Functional / State Machine", "P1", "Automated"),
    ("FR-020", "Final Hiring Workflow", "Finalize Hire Compliance Gate Verification", "TC_HX_HIRE_001, TC_HX_HIRE_002, TC_HX_HIRE_004", "Compliance / Business Rules", "P1", "Automated"),
    ("NFR-001", "Multi-Tenancy", "Tenant Data Isolation via companyId Scoping", "TC_HX_DB_001, TC_HX_TEAM_003", "Security / Data Isolation", "P1", "Automated"),
    ("NFR-002", "Session Security", "HTTP-Only, Secure, SameSite=Lax Session Tokens", "TC_HX_SEC_004", "Security / Cookie Integrity", "P1", "Automated"),
    ("NFR-003", "Webhook Security", "HMAC SHA-256 Webhook Signature Verification", "TC_HX_WH_001, TC_HX_WH_002, TC_HX_WH_004", "Security / Cryptography", "P1", "Automated"),
    ("NFR-004", "Performance", "Response Latency & Page Rendering SLOs", "TC_HX_PERF_001, TC_HX_PERF_002, TC_HX_PERF_003, TC_HX_PERF_004, TC_HX_PERF_005", "Performance / Benchmarking", "P2", "Automated"),
    ("NFR-005", "Storage Integrity", "R2 Storage Cascade Safety (SetNull on delete)", "TC_HX_DB_003", "Data Integrity / Cascade", "P1", "Automated"),
    ("NFR-006", "Resilience", "Graceful Fallback to Mock Video & Local TF-IDF", "TC_HX_MEET_003, TC_HX_AI_003", "Reliability / Resilience", "P2", "Automated"),
    ("NFR-007", "Auditability", "Audit Stamping on Document Actions & State Transitions", "TC_HX_DOC_002, TC_HX_HIRE_003", "Compliance / Audit Trail", "P1", "Automated")
]

def create_rtm_workbook():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Requirements Traceability"
    
    # Header metadata
    header_metadata = [
        ("Project Name", "HireX"),
        ("Document Name", "Requirements Traceability Matrix (RTM)"),
        ("Created By", "Saifan"),
        ("Created Date", "2026-11-02"),
        ("Reviewed By", "Pending Review"),
        ("Version", "1.0")
    ]
    for r_idx, (f, v) in enumerate(header_metadata, start=1):
        c1 = ws.cell(row=r_idx, column=1, value=f)
        c2 = ws.cell(row=r_idx, column=2, value=v)
        c1.font = BOLD_FONT
        c1.fill = METADATA_LABEL_FILL
        c1.border = THIN_BORDER
        c2.font = REGULAR_FONT
        c2.border = THIN_BORDER

    headers = [
        "Requirement ID",
        "Module",
        "Requirement Description",
        "Linked Test Case IDs",
        "Test Type",
        "Priority",
        "Automation Status",
        "Execution Result",
        "Defect Reference"
    ]
    
    header_row = 8
    for c_idx, h_text in enumerate(headers, start=1):
        cell = ws.cell(row=header_row, column=c_idx, value=h_text)
        cell.font = WHITE_FONT
        cell.fill = PURPLE_HEADER_FILL
        cell.border = HEADER_BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
    ws.row_dimensions[header_row].height = 26
    
    start_row = 9
    defect_map = {
        "FR-004": ("Fail", "DF-HX-001"),
        "FR-015": ("Fail", "DF-HX-002"),
        "FR-001": ("Fail", "DF-HX-003, DF-HX-004, DF-HX-005"),
        "FR-002": ("Fail", "DF-HX-004"),
        "FR-005": ("Pass", "None"),
        "FR-006": ("Pass", "None (FP-HX-001 Verified)"),
        "FR-007": ("Pass", "None"),
        "FR-010": ("Pass", "None"),
        "FR-013": ("Pass", "None"),
        "FR-016": ("Pass", "None"),
        "NFR-001": ("Pass", "None"),
        "NFR-002": ("Pass", "None"),
        "NFR-004": ("Pass", "None"),
    }

    for i, item in enumerate(RTM_REQS):
        cur_row = start_row + i
        ws.row_dimensions[cur_row].height = 30
        
        req_id, module, title, tc_ids, t_type, prio, auto_status = item
        if req_id in defect_map:
            exec_res, defect_ref = defect_map[req_id]
        else:
            exec_res = "Not Executed"
            defect_ref = "None"
        
        row_vals = [req_id, module, title, tc_ids, t_type, prio, auto_status, exec_res, defect_ref]
        
        is_even = (i % 2 == 0)
        row_fill = ZEBRA_FILL if is_even else PatternFill(fill_type=None)
        
        for c_idx, val in enumerate(row_vals, start=1):
            cell = ws.cell(row=cur_row, column=c_idx, value=val)
            cell.font = REGULAR_FONT
            cell.border = THIN_BORDER
            cell.fill = row_fill
            if c_idx in [1, 6, 7, 8]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
                if c_idx == 1:
                    cell.font = BOLD_FONT
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    max_row = start_row + len(RTM_REQS) - 1
    ws.freeze_panes = "B9"
    ws.auto_filter.ref = f"A8:I{max_row}"
    
    col_widths = {
        1: 18, # Req ID
        2: 24, # Module
        3: 40, # Description
        4: 35, # Linked TCs
        5: 22, # Test Type
        6: 12, # Priority
        7: 18, # Automation Status
        8: 18, # Execution Result
        9: 18  # Defect Reference
    }
    for c_idx, w in col_widths.items():
        ws.column_dimensions[get_column_letter(c_idx)].width = w

    output_path = "HireX_Requirements_Traceability_Matrix.xlsx"
    wb.save(output_path)
    print(f"Successfully generated {output_path} with {len(RTM_REQS)} requirements tracked!")

if __name__ == "__main__":
    create_rtm_workbook()

