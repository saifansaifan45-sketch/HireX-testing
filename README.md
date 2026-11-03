# HireX End-to-End Test Automation & Bug Hunting Framework

![HireX QA Framework](https://img.shields.io/badge/QA%20Architecture-Playwright%20Python-581C87?style=for-the-badge)
![Pytest](https://img.shields.io/badge/Test%20Runner-Pytest-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Coverage](https://img.shields.io/badge/Test%20Cases-540%20Scenarios-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Defects%20Uncovered-7%20Active-red?style=for-the-badge)

Enterprise-grade End-to-End (E2E) automation testing and adversarial security probing framework for the **HireX Multi-Portal Recruitment Platform**.

---

## 🎯 Target Application Scope

- **Recruiter Portal:** `https://dev.recruiter.hire.zobay.in`
- **Interviewer Portal:** `https://dev.interviewer.hire.zobay.in`
- **Candidate Portal:** `https://dev.candidate.hire.zobay.in`
- **Unified REST API:** `https://api.dev.hire.zobay.in`

---

## 🏗️ Framework Architecture

```text
HireX-testing/
│
├── config/                  # Centralized environment & role configuration
│   ├── settings.py
│   └── environments.py
│
├── api/                     # Dedicated API clients using Playwright APIRequestContext
│   ├── base_client.py
│   ├── auth_client.py
│   ├── jobs_client.py
│   ├── applications_client.py
│   ├── interviews_client.py
│   ├── offers_client.py
│   └── documents_client.py
│
├── pages/                   # Page Object Model (POM) with self-healing retries
│   ├── base_page.py
│   ├── recruiter/
│   ├── interviewer/
│   └── candidate/
│
├── fixtures/                # Pytest fixtures & browser context lifecycle
│   └── conftest.py
│
├── tests/                   # Modular automated test suites
│   ├── smoke/               # High-priority availability & health probes
│   ├── functional/          # Cross-portal recruiter, interviewer & candidate flows
│   ├── api/                 # REST API schema & endpoint validations
│   ├── security/            # RBAC, portal session isolation, SQLi & XSS resilience
│   ├── performance/         # Latency benchmarking against SLOs
│   ├── e2e/                 # Full recruitment lifecycle (Apply -> Screen -> Interview -> Offer)
│   └── regression/          # Automated regression tests for discovered defects
│
├── scripts/                 # Real browser DOM inspectors & report generators
│   ├── dom_locator_inspector.py
│   ├── export_all_to_csv.py
│   ├── generate_complete_500_test_cases.py
│   └── sync_results.py
│
├── csv_reports/             # Google Sheets-ready CSV exports across all modules
├── HireX_Complete_Test_Cases.xlsx
├── HireX_Defect_Report.xlsx
├── HireX_Executed_Test_Cases.xlsx
├── HireX_DOM_Element_Inventory.xlsx
├── HireX_Locator_Inventory.xlsx
├── HireX_Application_Inventory.xlsx
├── HireX_Requirements_Traceability_Matrix.xlsx
└── HireX_Automation_Execution_Report.html
```

---

## 🚨 Discovered Application Defects (7 Confirmed & Automated)

| Defect ID | Severity / Priority | Module | Vulnerability & Defect Summary | Root Cause | Regression Test ID |
|---|---|---|---|---|---|
| **DF-HX-001** | **High (S2) / P1** | Jobs API | **CWE-213 / OWASP API3: Sensitive Data Exposure**: Public `GET /jobs` leaks executive `digitalSignatureUrl` assets. | Unfiltered Prisma model serialization to HTTP response. | `TC_HX_REG_001` |
| **DF-HX-002** | **High (S2) / P1** | Interviews | **Unhandled HTTP 500 Server Crash**: Submitting evaluation feedback on an interview in `ASSIGNED` status crashes the backend. | Missing interview lifecycle state pre-check (`IN_PROGRESS`/`COMPLETED`). | `TC_HX_FEED_001` |
| **DF-HX-003** | **High (S2) / P1** | Team Management | **Unhandled HTTP 500 Server Crash**: `POST /recruiter/interviewers/invite` crashes when omitting mandatory `name` parameter. | Missing `@IsNotEmpty()` and `@IsString()` class-validator decorators on DTO. | `TC_HX_TEAM_001` |
| **DF-HX-004** | **High (S2) / P1** | Team & RBAC | **Unhandled HTTP 500 Server Crash**: `POST /recruiter/team/invite` crashes when passed an invalid role enum (e.g. `INVALID_SUPER_USER`). | Unhandled Prisma Enum mapping exception at API gateway level. | `TC_HX_TEAM_002` |
| **DF-HX-005** | **Medium (S3) / P2** | Team & Security | **Missing Email Syntax Validation (Ghost Account Injection)**: Accepts malformed non-email strings, inserts DB records, and issues tokens (`201 Created`). | Missing `@IsEmail()` decorator on `InviteTeamDto`. | `TC_HX_TEAM_003` |
| **DF-HX-006** | **High (S2) / P1** | Storage & Resumes | **Broken Cloud Asset Storage URLs (Hardcoded `localhost:3001`)**: Candidate resume files contain `http://localhost:3001/uploads`, causing browser `ERR_CONNECTION_REFUSED`. | Database seed migration hardcodes local dev port instead of cloud CDN base URL. | `TC_HX_DOC_001` |
| **DF-HX-007** | **Medium (S3) / P2** | Candidate Profile | **Missing Non-Empty Validation on Profile Name (Blank Dossiers)**: `PUT /candidate/me` accepts `{"name": ""}` with `200 OK`, wiping candidate identity. | `UpdateCandidateProfileDto` omits `@IsNotEmpty()` and `@MinLength(1)`. | `TC_HX_CAND_001` |

---

## ⚡ Setup & Execution

### 1. Prerequisites
- Python 3.10+ (Recommended Python 3.13)
- Playwright Chromium binaries

### 2. Installation
```bash
git clone https://github.com/saifansaifan145-sketch/HireX-testing.git
cd HireX-testing
pip install -r requirements.txt
playwright install chromium
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 4. Running Tests

```bash
# Run all automated tests in headless mode
pytest -v

# Run tests in headed browser mode
pytest --headed -v

# Run with slow motion for visual debugging (e.g. 500ms delay per step)
pytest --headed --slowmo 500 -v

# Run defect regression suite only
pytest tests/regression/test_defect_regressions.py -v

# Run specific functional suites
pytest tests/functional/ -v
pytest tests/security/ -v
pytest tests/performance/ -v
```

---

## 📊 Reports & Deliverables

- **Interactive HTML Dashboard:** `HireX_Automation_Execution_Report.html`
- **Master Test Repository (540 TCs across 30 sheets):** `HireX_Complete_Test_Cases.xlsx`
- **Google Sheets Ready CSVs:** Located in `./` and `csv_reports/modules/`
- **Requirements Traceability Matrix (RTM):** `HireX_Requirements_Traceability_Matrix.xlsx`
- **DOM & Locator Intelligence Inventories:** `HireX_DOM_Element_Inventory.xlsx` & `HireX_Locator_Inventory.xlsx`
- **Comprehensive Bug Hunting Security Report:** `HireX_Bug_Hunting_Summary.md`

---

## 👤 Author
**Saifan**  
Senior QA Automation Architect & Principal SDET  
Portfolio: [saifansaifan145-sketch](https://github.com/saifansaifan145-sketch)

