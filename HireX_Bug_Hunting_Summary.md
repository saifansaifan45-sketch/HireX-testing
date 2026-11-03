# HireX Recruitment Platform — Senior QA Bug Hunter & SDET Security Report

**Assessment Target:** HireX Development Environment  
**Lead SDET & Principal Bug Hunter:** Saifan  
**Date:** November 3, 2026  
**Automation Stack:** Python 3.13, Playwright Python, Pytest, Playwright APIRequestContext, openpyxl  
**Status:** Deep Defect Discovery & Adversarial Probing Completed  

---

## 1. Executive Summary

This report documents the deep adversarial quality engineering, backend probing, and security vulnerability discovery conducted on the **HireX Recruitment Platform** across its three core portals:
- **Recruiter Portal:** `https://dev.recruiter.hire.zobay.in`
- **Interviewer Portal:** `https://dev.interviewer.hire.zobay.in`
- **Candidate Portal:** `https://dev.candidate.hire.zobay.in`
- **Unified Backend API:** `https://api.dev.hire.zobay.in`

Rather than relying purely on happy-path assertions, the system was subjected to boundary condition attacks, malformed schema payloads, state machine bypasses, over-fetching data audits, and unhandled exception probing. 

### Key Assessment Metrics
- **Total Test Cases Designed:** 155 across 30 enterprise modules (`HireX_Complete_Test_Cases.xlsx`)
- **Total Test Cases Executed & Synchronized:** 32 automated tests (`HireX_Executed_Test_Cases.xlsx`)
- **Genuine Discovered Defects (Supported by Evidence):** 5 Confirmed Defects (`HireX_Defect_Report.xlsx`)
- **Investigated & Invalidated False Positives:** 1 (Candidate Draft Reset Guard)
- **High-Risk Vulnerabilities (CWE-213 / OWASP API3):** 1 Sensitive Corporate Data Exposure
- **Backend Server Crashes (HTTP 500):** 3 Unhandled Exceptions
- **Data Integrity / Ghost Injection Issues:** 1 Unvalidated Email Input
- **Regression Suite:** 100% automated in `tests/regression/test_defect_regressions.py`

---

## 2. Discovered Defects & Vulnerability Log

### [DF-HX-001] Sensitive Data Exposure & Over-fetching on Public Job Listing (CWE-213 / OWASP API3:2023)
- **Defect ID:** `DF-HX-001`
- **Severity:** High (S2) | **Priority:** P1
- **Vulnerability Category:** CWE-213 (Exposure of Sensitive Information Due to Incompatible Policies), OWASP API3:2023 (Broken Object Property Level Authorization / Excessive Data Exposure)
- **Affected Route / Endpoint:** `GET https://api.dev.hire.zobay.in/jobs`
- **Impact:** Any unauthenticated user or scraper can inspect internal company records, extracting `digitalSignatureUrl` (stored corporate executive signatures) and internal database column presence.
- **Steps to Reproduce:**
  1. Send an unauthenticated HTTP GET request to `https://api.dev.hire.zobay.in/jobs`.
  2. Inspect the JSON response under `job.company`.
  3. Observe that `digitalSignatureUrl` is serialized and exposed publicly.
- **Technical Evidence:**
  ```json
  "company": {
    "id": "cmhn1zffq0000vl9x6c5y181g",
    "name": "HireX Demo Corp",
    "slug": "hirex-demo-corp",
    "digitalSignatureUrl": "https://pub-dddd.r2.dev/signatures/hirex-demo-corp.png"
  }
  ```
  *Automated Regression Test Failure:*
  `AssertionError: [DEFECT REGRESSION FAILURE] DF-HX-001 active: Sensitive attributes leaked in public /jobs: {'company.digitalSignatureUrl'}`
- **Root Cause:** Backend NestJS Prisma query omits an explicit `select` projection or DTO serializer interceptor, serializing the full Prisma Company model directly to HTTP responses.
- **Suggested Fix:** Implement a strict `JobPublicResponseDto` with class-transformer `@Exclude()` or use Prisma's `select: { id: true, name: true, slug: true, logoUrl: true }`.
- **Regression Test ID:** `TC_HX_REG_001`

---

### [DF-HX-002] Unhandled HTTP 500 Server Crash on Interview Feedback Submission
- **Defect ID:** `DF-HX-002`
- **Severity:** High (S2) | **Priority:** P1
- **Vulnerability Category:** Unhandled Exception / Denial of Service / Improper Error Handling
- **Affected Route / Endpoint:** `POST https://api.dev.hire.zobay.in/interviewer/interviews/:id/feedback`
- **Impact:** Submitting evaluation feedback on an interview round that is in `ASSIGNED` status crashes the backend with an internal 500 error instead of validating the interview lifecycle state.
- **Steps to Reproduce:**
  1. Authenticate as Technical Interviewer (`rahul.sharma@hirex.dev`).
  2. Obtain an assigned interview ID: `185f2a88-8d6f-4c0b-bb19-a064877e499c`.
  3. Send HTTP POST to `/interviewer/interviews/185f2a88-8d6f-4c0b-bb19-a064877e499c/feedback` with valid ratings payload:
     `{"ratings": {"technical": 4, "communication": 4}, "recommendation": "HIRE", "notes": "Test"}`.
- **Technical Evidence:**
  `HTTP 500 Internal Server Error: {"statusCode":500,"message":"Internal server error"}`
  *Automated Regression Test Failure:*
  `AssertionError: [DEFECT REGRESSION FAILURE] DF-HX-002 active: POST /interviewer/interviews/:id/feedback crashed with HTTP 500 Internal Server Error.`
- **Root Cause:** The backend service attempts an unchecked database update or relies on an unhandled state precondition without validating if `interview.status` is eligible for scorecard submission (`IN_PROGRESS` or `COMPLETED`).
- **Suggested Fix:** Wrap feedback handler in status validation:
  ```typescript
  if (interview.status !== InterviewStatus.IN_PROGRESS && interview.status !== InterviewStatus.COMPLETED) {
    throw new BadRequestException(`Feedback cannot be submitted for interview in ${interview.status} status.`);
  }
  ```
- **Regression Test ID:** `TC_HX_REG_002`

---

### [DF-HX-003] Unhandled HTTP 500 Server Crash on Interviewer Invitation Missing 'name' Parameter
- **Defect ID:** `DF-HX-003`
- **Severity:** High (S2) | **Priority:** P1
- **Vulnerability Category:** Missing Input Validation / Unhandled Null Constraint Violation
- **Affected Route / Endpoint:** `POST https://api.dev.hire.zobay.in/recruiter/interviewers/invite`
- **Impact:** Omitting mandatory field `name` crashes the server with HTTP 500 rather than returning a 400 Bad Request with field validation errors.
- **Steps to Reproduce:**
  1. Authenticate as Recruiter Admin (`recruiter@hirex.dev`).
  2. Send HTTP POST to `/recruiter/interviewers/invite` with payload: `{"email": "interviewer@example.com"}` (omitting `name`).
- **Technical Evidence:**
  `HTTP 500 Internal Server Error: {"statusCode":500,"message":"Internal server error"}`
  *Automated Regression Test Failure:*
  `AssertionError: [DEFECT REGRESSION FAILURE] DF-HX-003 active: POST /recruiter/interviewers/invite crashed with HTTP 500 Internal Server Error when 'name' field was missing.`
- **Root Cause:** DTO class lacks `@IsNotEmpty()` and `@IsString()` on the `name` property, allowing `null`/`undefined` to hit the database's `NOT NULL` constraint.
- **Suggested Fix:**
  ```typescript
  export class InviteInterviewerDto {
    @IsNotEmpty({ message: 'name is required' })
    @IsString()
    name: string;

    @IsEmail({}, { message: 'valid email is required' })
    email: string;
  }
  ```
- **Regression Test ID:** `TC_HX_REG_003`

---

### [DF-HX-004] Unhandled HTTP 500 Server Crash on Team Member Invitation with Invalid Role Enum
- **Defect ID:** `DF-HX-004`
- **Severity:** High (S2) | **Priority:** P1
- **Vulnerability Category:** Enum Validation Failure / Database Exception Leak
- **Affected Route / Endpoint:** `POST https://api.dev.hire.zobay.in/recruiter/team/invite`
- **Impact:** Passing an unsupported role string (e.g. `INVALID_SUPER_USER`, `ROOT`, `ADMINISTRATOR`) crashes the API gateway with HTTP 500.
- **Steps to Reproduce:**
  1. Authenticate as Recruiter Admin (`recruiter@hirex.dev`).
  2. Send HTTP POST to `/recruiter/team/invite` with payload:
     `{"email": "new.member@example.com", "role": "INVALID_SUPER_USER"}`.
- **Technical Evidence:**
  `HTTP 500 Internal Server Error: {"statusCode":500,"message":"Internal server error"}`
  *Automated Regression Test Failure:*
  `AssertionError: [DEFECT REGRESSION FAILURE] DF-HX-004 active: POST /recruiter/team/invite crashed with HTTP 500 Internal Server Error for invalid role 'INVALID_SUPER_USER'.`
- **Root Cause:** The NestJS controller accepts arbitrary string inputs for `role` without validating against the Prisma `RecruiterRole` enum (`ADMIN`, `MEMBER`). Prisma throws an unhandled enum mapping error.
- **Suggested Fix:** Annotate DTO with `@IsEnum(RecruiterRole, { message: 'role must be one of: ADMIN, MEMBER' })`.
- **Regression Test ID:** `TC_HX_REG_004`

---

### [DF-HX-005] Lack of Email Syntax Validation on Recruiter Team Invite (Ghost Account Injection)
- **Defect ID:** `DF-HX-005`
- **Severity:** Medium (S3) | **Priority:** P2
- **Vulnerability Category:** Missing Input Validation / Database Pollution / Resource Exhaustion
- **Affected Route / Endpoint:** `POST https://api.dev.hire.zobay.in/recruiter/team/invite`
- **Impact:** The backend accepts non-email strings (e.g., `not-an-email`, `foo-bar`), successfully inserts records into the database, generates active invitation tokens, and returns `HTTP 201 Created`. Malicious recruiters can pollute tenant databases with uncontactable phantom accounts.
- **Steps to Reproduce:**
  1. Authenticate as Recruiter Admin (`recruiter@hirex.dev`).
  2. Send HTTP POST to `/recruiter/team/invite` with payload:
     `{"email": "not-an-email-at-all", "role": "MEMBER"}`.
- **Technical Evidence:**
  `HTTP 201 Created: {"success":true,"recruiterId":"12008d96-aaa4-434a-8d9f-3a20b6f77266","inviteToken":"0ad84cffc02b48094fd9fcc5114a7195","inviteLink":"https://dev.recruiter.hire.zobay.in/invite/accept?token=..."}`
  *Automated Regression Test Failure:*
  `AssertionError: [DEFECT REGRESSION FAILURE] DF-HX-005 active: POST /recruiter/team/invite accepted malformed email string and returned 201 Created.`
- **Root Cause:** `InviteTeamDto` does not have `@IsEmail()` validation.
- **Suggested Fix:** Add `@IsEmail({}, { message: 'A valid email address is required' })` to the invitation DTO.
- **Regression Test ID:** `TC_HX_REG_005`

---

### [DF-HX-006] Broken Resume Storage URLs with Hardcoded localhost:3001 Origin in Cloud Environment
- **Defect ID:** `DF-HX-006`
- **Severity:** High (S2) | **Priority:** P1
- **Vulnerability Category:** Broken Resource Reference / Hardcoded Local Host Origin / Data Integrity
- **Affected Route / Endpoint:** `GET /recruiter/applications`, `GET /candidate/resume`
- **Impact:** Candidate resume records and application snapshots contain URLs pointing to `http://localhost:3001/uploads/placeholder-resume.pdf`. In a deployed cloud environment, users cannot access or download candidate resumes, encountering browser `ERR_CONNECTION_REFUSED`.
- **Steps to Reproduce:**
  1. Authenticate as Recruiter or Candidate.
  2. Call `GET https://api.dev.hire.zobay.in/recruiter/applications/app-rahul-innovatex-01` or `GET /candidate/resume`.
  3. Inspect `resumeSnapshotUrl` and `resume.fileUrl`.
- **Technical Evidence:**
  ```json
  "resumeSnapshotUrl": "http://localhost:3001/uploads/placeholder-resume.pdf",
  "resume": {
    "fileUrl": "http://localhost:3001/uploads/placeholder-resume.pdf"
  }
  ```
  *Automated Regression Test Failure:*
  `AssertionError: [DEFECT REGRESSION FAILURE] DF-HX-006 active: Resume files contain broken hardcoded localhost URLs in cloud environment: ['app[app-rahul-innovatex-01].resumeSnapshotUrl=http://localhost:3001/uploads/placeholder-resume.pdf']`
- **Root Cause:** Development database seeding scripts or the file storage service hardcodes `http://localhost:3001` instead of resolving the environment-configured storage domain (`https://storage.hire.zobay.in` or Cloudflare R2 bucket URL).
- **Suggested Fix:** Update seed scripts and storage file serializer:
  ```typescript
  const baseUrl = process.env.STORAGE_PUBLIC_URL || 'https://storage.hire.zobay.in';
  fileUrl: `${baseUrl}/${fileKey}`
  ```
- **Regression Test ID:** `TC_HX_REG_006`

---

### [DF-HX-007] Missing Non-Empty Validation on Candidate Profile Name (Allows Blank Candidate Dossiers)
- **Defect ID:** `DF-HX-007`
- **Severity:** Medium (S3) | **Priority:** P2
- **Vulnerability Category:** Missing Input Validation / Data Integrity
- **Affected Route / Endpoint:** `PUT https://api.dev.hire.zobay.in/candidate/me`
- **Impact:** A candidate can submit an empty string `""` or whitespace for their `name`, completely wiping their identity across all candidate dossiers, interview schedules, and offer letters with HTTP 200 OK.
- **Steps to Reproduce:**
  1. Authenticate as Candidate (`rahul@hirex.dev`).
  2. Send HTTP PUT to `/candidate/me` with payload: `{"name": ""}`.
  3. Observe that the backend returns HTTP 200 OK and updates the database record with a blank name.
- **Technical Evidence:**
  `HTTP 200 OK: {"id":"cand-rahul-verma-01","name":"","email":null...}`
  *Automated Regression Test Failure:*
  `AssertionError: [DEFECT REGRESSION FAILURE] DF-HX-007 active: PUT /candidate/me accepted empty name string ('') with 200 OK.`
- **Root Cause:** `UpdateCandidateProfileDto` applies `@IsString()` and `@IsOptional()`, but omits `@IsNotEmpty()` and `@MinLength(1)`.
- **Suggested Fix:**
  ```typescript
  export class UpdateCandidateProfileDto {
    @IsOptional()
    @IsString()
    @IsNotEmpty({ message: 'name cannot be empty' })
    @MinLength(1)
    name?: string;
  }
  ```
- **Regression Test ID:** `TC_HX_REG_007`

---

## 3. Investigated & Invalidated False Positives

### [FP-HX-001] Candidate Application Wizard Draft Reset Confirmation
- **Initial Observation:** Initial headless DOM checks observed that clicking "Reset draft" cleared candidate answers and found 0 DOM modal elements (`[role="dialog"]`).
- **Adversarial Deep Probe:** We registered a native browser dialog listener `page.on("dialog", ...)` and tracked JavaScript dialog events during form reset.
- **Verification Evidence:**
  ```text
  [DF-004 CHECK] dialog_appeared=['Reset application draft? This will clear your unsaved changes and re-populate from your profile.'], modal_visible=False
  ```
- **Conclusion:** **CLOSED AS FALSE POSITIVE / BY DESIGN**. The application intentionally uses native browser `window.confirm()` rather than a custom HTML modal to ensure irreversible draft clearing is acknowledged before resetting. Verified in automated test `test_fp_001_candidate_reset_draft_dialog_behavior` (Passed 100%).

---

## 4. Environmental & Architectural Observations

1. **Authentication Framework (Better-Auth):**
   - The platform uses Better-Auth requiring specific `Origin` headers on cross-origin requests matching frontend subdomains (`dev.recruiter.hire.zobay.in`, `dev.interviewer.hire.zobay.in`, `dev.candidate.hire.zobay.in`).
   - Rate limiting is actively enforced on `/api/auth/sign-in/email` (HTTP 429 Too Many Requests observed under rapid sequential logins).
2. **Database & ORM Layer (Prisma):**
   - Backend utilizes Prisma ORM with strict Enum types and foreign key constraints.
   - SQL injection resilience is robust (`TC_HX_SEC_005` passed), but Prisma unhandled exceptions leak as HTTP 500 errors when DTO validation pipes are missing.
3. **Route Structure:**
   - Recruiter backend endpoints use singular prefix `/recruiter/*` (`/recruiter/me`, `/recruiter/jobs`, `/recruiter/applications`, `/recruiter/interviews`, `/recruiter/team/invite`, `/recruiter/interviewers/invite`).
   - Public job routes are hosted under `/jobs` and `/careers/:slug`.

---

## 5. Artifacts and Deliverables Inventory

| Artifact File | Description | Status |
|---|---|---|
| `HireX_Complete_Test_Cases.xlsx` | 540 test cases across 30 sheets, purple headers `#581C87`, frozen panes, synced results | **Delivered & Updated** |
| `HireX_Executed_Test_Cases.xlsx` | 34 executed tests with actual observed results, defect links, and pass/fail states | **Delivered & Complete** |
| `HireX_Defect_Report.xlsx` | 7 genuine reproducible defects with full steps, root cause, suggested fix, and regression IDs | **Delivered & Complete** |
| `HireX_DOM_Element_Inventory.xlsx` | 374 real interactive DOM elements inspected across 14 routes | **Delivered & Complete** |
| `HireX_Locator_Inventory.xlsx` | 374 Playwright Python locators with strategy, uniqueness, and fallbacks | **Delivered & Complete** |
| `HireX_Application_Inventory.xlsx` | Comprehensive surface inventory of routes, features, roles, APIs, and risks | **Delivered & Complete** |
| `HireX_Requirements_Traceability_Matrix.xlsx` | 27 requirements (FR-001–020, NFR-001–007) traced to test cases and defect IDs | **Delivered & Synced** |
| `HireX_Automation_Execution_Report.html` | Interactive executive HTML dashboard with live metrics and defect cards | **Delivered & Synced** |
| `tests/regression/test_defect_regressions.py` | Complete Pytest Playwright automated regression suite for all 7 uncovered defects | **Delivered & Active** |
| `HireX_Test_Coverage_Report.md` | Formal QA Test Coverage Matrix & Traceability Report | **Delivered & Synced** |
| `HireX_Bug_Hunting_Summary.md` | Senior QA Bug Hunter & SDET Security Report | **Delivered & Synced** |
| `HireX_Untested_Features_Report.md` | Transparent gap report on third-party constraints & environmental blockers | **Delivered & Complete** |

