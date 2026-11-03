import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule

# Colors
PURPLE_HEADER_FILL = PatternFill(start_color="581C87", end_color="581C87", fill_type="solid") # Deep Purple
METADATA_LABEL_FILL = PatternFill(start_color="EDE9FE", end_color="EDE9FE", fill_type="solid") # Light Purple
ZEBRA_FILL = PatternFill(start_color="FAF5FF", end_color="FAF5FF", fill_type="solid")
WHITE_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
BOLD_FONT = Font(name="Calibri", size=11, bold=True, color="000000")
REGULAR_FONT = Font(name="Calibri", size=10, color="000000")
TITLE_FONT = Font(name="Calibri", size=14, bold=True, color="4C1D95")

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

MODULE_DEFINITIONS = [
    {
        "name": "Auth & Authorization",
        "sheet": "Auth & Authorization",
        "cases": [
            ("TC_HX_AUTH_001", "Verify candidate signup with valid details and 8+ char password", "Unregistered email address", "Name: Alice Candidate, Email: alice@example.com, Pass: Password123!", "Account created, HTTP 201, session cookie set, lands on dashboard", "P1"),
            ("TC_HX_AUTH_002", "Verify candidate signup rejection when password is shorter than 8 characters", "Candidate on signup page", "Name: Alice, Email: alice2@example.com, Pass: pass1", "Client-side validation warning displayed, submission blocked", "P1"),
            ("TC_HX_AUTH_003", "Verify candidate signup rejection on duplicate email address", "Email alice@example.com already registered", "Duplicate email submission", "400 Bad Request / 409 Conflict with 'Email already registered'", "P1"),
            ("TC_HX_AUTH_004", "Verify recruiter admin login with valid registered credentials", "Recruiter admin account exists", "Email: recruiter@hirex.dev, Pass: Password123!", "Successful authentication, HTTP 200, session cookie set, redirects to /dashboard", "P1"),
            ("TC_HX_AUTH_005", "Verify recruiter login error message on invalid password", "Registered recruiter email", "Email: recruiter@hirex.dev, Pass: WrongPass999!", "Authentication fails, error banner 'Invalid email or password' displayed", "P1"),
            ("TC_HX_AUTH_006", "Verify interviewer login via specialized auth endpoint", "Interviewer account exists", "Email: rahul.sharma@hirex.dev, Pass: Password123!", "Interviewer authenticated via /auth/interviewer/login, lands on interviewer workspace", "P1"),
            ("TC_HX_AUTH_007", "Verify single-use interviewer invite token redemption and account activation", "Valid invite token generated in DB", "Token: test-invite-token, Name: Devin Panelist, Pass: Password123!", "Account activated, token destroyed in DB, user logged in without extra step", "P1"),
            ("TC_HX_AUTH_008", "Verify rejection of expired or already consumed interviewer invite token", "Invite token already consumed or expired", "Token: expired-token-123", "HTTP 400/404 'Invalid or expired invitation token' displayed", "P2"),
            ("TC_HX_AUTH_009", "Verify user logout invalidates session token and clears cookies", "Authenticated session on any portal", "Click Logout / Sign Out", "Session cookie Max-Age=0, session invalidated in DB, redirects to /login", "P1"),
            ("TC_HX_AUTH_010", "Verify session persistence across browser reload when rememberMe is selected", "User logs in with Remember Me checked", "RememberMe: True", "Session cookie persists across browser restart with extended expiry", "P2"),
        ]
    },
    {
        "name": "Recruiter Dashboard",
        "sheet": "Recruiter Dashboard",
        "cases": [
            ("TC_HX_DASH_001", "Verify recruiter dashboard metrics render with correct aggregations", "Recruiter admin logged in", "Active jobs, applicants, interviews in tenant", "Total jobs, active applicants, pending interviews, and hiring metrics match DB counts", "P1"),
            ("TC_HX_DASH_002", "Verify recent applicants list on recruiter dashboard", "Applicants exist in pipeline", "Navigating to /dashboard", "Top recent candidate cards display name, role, applied date, and status", "P2"),
            ("TC_HX_DASH_003", "Verify quick action navigation links on recruiter dashboard", "Recruiter admin on /dashboard", "Click 'Job Openings', 'Applications', 'Team', 'Settings'", "Each navigation link routes to the corresponding portal view without error", "P2"),
            ("TC_HX_DASH_004", "Verify empty state display when tenant has zero active jobs", "Newly created company tenant with 0 jobs", "Navigating to /dashboard", "Clean empty state illustration with 'Create your first job' call-to-action button", "P3"),
            ("TC_HX_DASH_005", "Verify tenant name and organization badge display in sidebar", "Recruiter logged in", "Tenant: HireX Demo Corp", "Sidebar header shows 'HireX Demo Corp EMPLOYER PORTAL' branding", "P3"),
        ]
    },
    {
        "name": "Org & Team Management",
        "sheet": "Org & Team Management",
        "cases": [
            ("TC_HX_TEAM_001", "Verify recruiter admin can invite a new team member with role selection", "Recruiter Admin logged in on /team", "Email: newrecruiter@hirex.dev, Role: RECRUITER_MEMBER", "Invitation record created, status = INVITED, invitation link generated", "P1"),
            ("TC_HX_TEAM_002", "Verify team member list renders with name, email, role, and status badges", "Multiple team members exist", "Navigating to /team", "Table renders with columns: Member, Email, Role (ADMIN/RECRUITER/HIRING_MANAGER), Status", "P2"),
            ("TC_HX_TEAM_003", "Verify Recruiter Member cannot access organization deletion or billing settings", "Logged in as Recruiter Member", "Attempt to access /settings?tab=danger-zone", "Access denied / 403 Forbidden or restricted admin controls hidden", "P1"),
            ("TC_HX_TEAM_004", "Verify company profile settings update (Logo, Industry, Website, About)", "Recruiter Admin on /settings?tab=company", "Industry: 'Software', Website: 'https://hirex.dev', About: 'Talent OS'", "Updated fields saved to Company model and reflected across candidate career pages", "P2"),
            ("TC_HX_TEAM_005", "Verify duplicate team member invitation prevention", "Email already in team", "Invite existing email: recruiter@hirex.dev", "Validation error 'User already part of this organization' displayed", "P2"),
        ]
    },
    {
        "name": "Job Management",
        "sheet": "Job Management",
        "cases": [
            ("TC_HX_JOB_001", "Verify recruiter can create a new job requisition with all required fields", "Recruiter logged in on /jobs/new", "Title: 'Senior Backend Engineer', Location: 'Bengaluru', Mode: 'Remote', Type: 'Full-time', Salary: '20-25 LPA'", "Job created with status DRAFT or OPEN, visible in recruiter jobs list", "P1"),
            ("TC_HX_JOB_002", "Verify job creation validation blocks missing mandatory fields", "Recruiter on /jobs/new", "Empty Title or empty Description", "Form displays inline validation errors, submission prevented", "P1"),
            ("TC_HX_JOB_003", "Verify updating job status from OPEN to PAUSED", "Active OPEN job exists", "Select 'Pause Job' in job actions", "Job status updates to PAUSED; unlisted from public career page", "P2"),
            ("TC_HX_JOB_004", "Verify updating job status from PAUSED to CLOSED", "PAUSED job exists", "Select 'Close Job'", "Job status updates to CLOSED; candidate applications blocked", "P2"),
            ("TC_HX_JOB_005", "Verify editing existing job details persists correctly in database", "Existing job requisition", "Update description and skills array", "Changes saved to Job record and updated on public job view", "P2"),
            ("TC_HX_JOB_006", "Verify jobs list filtering by status (All, Open, Paused, Closed)", "Jobs with multiple statuses exist", "Click status filter tabs", "Table filters dynamically showing only matching job requisitions", "P3"),
        ]
    },
    {
        "name": "Application Form Builder",
        "sheet": "Application Form Builder",
        "cases": [
            ("TC_HX_FORM_001", "Verify recruiter can add custom sections to job application form", "Recruiter creating/editing job", "Section Title: 'System Design Experience'", "New section added with JSONB schema snapshot linked to ApplicationForm", "P1"),
            ("TC_HX_FORM_002", "Verify adding diverse question types (Short Text, Number, Dropdown, Checkbox, File)", "Recruiter in form builder", "Question types: SHORT_TEXT, NUMBER, DROPDOWN, FILE_UPLOAD", "All question types render with appropriate configuration controls (options, min/max)", "P1"),
            ("TC_HX_FORM_003", "Verify configuring mandatory vs optional question toggle", "Question in form builder", "Toggle 'Required' switch to ON", "Field schema sets required: true; enforced during candidate apply wizard", "P2"),
            ("TC_HX_FORM_004", "Verify deleting a section removes its child questions from the schema", "Section with 2 questions", "Click delete section button", "Section and its child questions are removed from form preview and schema", "P2"),
            ("TC_HX_FORM_005", "Verify GET /jobs/:id/application-form returns full JSONB question schema", "Job published with custom form", "API GET /jobs/{jobId}/application-form", "HTTP 200 with sections, questions, types, and validation rules", "P1"),
        ]
    },
    {
        "name": "Candidate Applications",
        "sheet": "Candidate Applications",
        "cases": [
            ("TC_HX_CAND_APP_001", "Verify registered candidate can submit an application for an open job", "Candidate authenticated, job OPEN", "Job ID, custom screening answers, resumeId", "HTTP 201 Created, Application record created in status APPLIED", "P1"),
            ("TC_HX_CAND_APP_002", "Verify duplicate application prevention for the same candidate and job", "Candidate already applied to job", "Submit second application to same job", "HTTP 400 / 409 'You have already applied for this position'", "P1"),
            ("TC_HX_CAND_APP_003", "Verify candidate application with cover note and portfolio link", "Candidate on application wizard", "Cover note: '10 years experience', Portfolio: 'https://github.com/alice'", "Cover note and links persisted and viewable by recruiter", "P2"),
            ("TC_HX_CAND_APP_004", "Verify application submission fails when mandatory screening questions are unanswered", "Job has required questions", "Submit without answering mandatory questions", "Validation error blocks submission; highlights missing fields", "P1"),
            ("TC_HX_CAND_APP_005", "Verify guest candidate application via /public/guest-resume", "Unauthenticated visitor", "Name: Bob Guest, Email: bob.guest@example.com, Resume PDF", "HTTP 201, Guest candidate profile and application created in status APPLIED", "P1"),
        ]
    },
    {
        "name": "Applicant Pipeline Kanban",
        "sheet": "Applicant Pipeline Kanban",
        "cases": [
            ("TC_HX_PIPE_001", "Verify Kanban board displays candidates in all standard stages", "Applicants in varied stages", "Navigate to /applicants?jobId={id}", "Columns render: APPLIED, SCREENING, INTERVIEW, OFFER_STAGE, DOCUMENT_VERIFICATION, HIRED", "P1"),
            ("TC_HX_PIPE_002", "Verify candidate card progression from APPLIED to SCREENING", "Candidate in APPLIED stage", "Drag or update status to SCREENING", "Application status updates to SCREENING in DB and UI immediately", "P1"),
            ("TC_HX_PIPE_003", "Verify candidate card progression from SCREENING to INTERVIEW", "Candidate in SCREENING stage", "Update status to INTERVIEW", "Status updates to INTERVIEW; candidate eligible for interview slot generation", "P1"),
            ("TC_HX_PIPE_004", "Verify strict forward-only guard: Reject reverting from SCREENING to APPLIED", "Candidate in SCREENING stage", "Attempt PATCH /applications/{id}/status {status: 'APPLIED'}", "HTTP 400 Bad Request ('Cannot revert candidate to APPLIED stage')", "P1"),
            ("TC_HX_PIPE_005", "Verify candidate rejection from any active stage sets status to REJECTED", "Candidate in SCREENING or INTERVIEW", "Select 'Reject Candidate' with rejection note", "Status updates to REJECTED; card moved to Rejected archive/column", "P1"),
            ("TC_HX_PIPE_006", "Verify open interview hard-block when advancing to OFFER_STAGE", "Candidate has active interview in ASSIGNED or CONFIRMED status", "Attempt to advance candidate to OFFER_STAGE", "Hard-blocked: 'Open interviews must be completed or cancelled before advancing'", "P1"),
        ]
    },
    {
        "name": "AI Resume Scoring",
        "sheet": "AI Resume Scoring",
        "cases": [
            ("TC_HX_AI_001", "Verify AI resume match score is calculated upon application submission", "Candidate applies with resume PDF", "Resume containing keywords matching job skills", "Application record contains aiScore (integer between 0 and 100)", "P1"),
            ("TC_HX_AI_002", "Verify aiScore display badge on recruiter applicant card", "Applicant has aiScore: 85", "Recruiter views applicant list", "Badge displays '85% Match' with appropriate color indicator (green for high match)", "P2"),
            ("TC_HX_AI_003", "Verify system falls back to local TF-IDF when external Groq LLM API is unavailable", "Groq API key empty or offline", "Application submitted with resume", "aiScore computed via fallback TF-IDF algorithm gracefully without error", "P2"),
            ("TC_HX_AI_004", "Verify candidate ranking by aiScore in recruiter applicants list", "Multiple applicants with scores 45, 78, 92", "Sort applicants by 'AI Score (High to Low)'", "Candidates reordered with 92% first, followed by 78% and 45%", "P3"),
        ]
    },
    {
        "name": "Interview Scheduling",
        "sheet": "Interview Scheduling",
        "cases": [
            ("TC_HX_SCHED_001", "Verify recruiter can create an interview and assign an interviewer panelist", "Candidate in INTERVIEW stage", "Interviewer: Rahul Sharma, Type: VIDEO, Duration: 45 min", "Interview created with status ASSIGNED, linked to application", "P1"),
            ("TC_HX_SCHED_002", "Verify slot generation engine computes available slots based on interviewer availability", "Interviewer availability set for Mon 14:00-18:00", "POST /interviews/slots/generate", "Slots generated in 45-minute increments within the specified window", "P1"),
            ("TC_HX_SCHED_003", "Verify candidate can self-book an available interview slot", "Open slots available", "Candidate selects slot and submits POST /interviews/booking", "Slot status updates to BOOKED; interview status updates to CONFIRMED", "P1"),
            ("TC_HX_SCHED_004", "Verify atomic concurrency guard prevents double-booking of same slot", "Single open slot", "Two candidates submit booking request concurrently (50ms delta)", "First request returns 200 OK; second request returns 409 Conflict", "P1"),
            ("TC_HX_SCHED_005", "Verify interview cancellation updates slot back to AVAILABLE or CANCELLED", "Confirmed interview", "Recruiter or candidate cancels interview", "Interview status updates to CANCELLED; notification generated", "P2"),
        ]
    },
    {
        "name": "Interviewer Availability",
        "sheet": "Interviewer Availability",
        "cases": [
            ("TC_HX_AVAIL_001", "Verify interviewer can configure recurring weekly availability schedule", "Interviewer logged in on /profile?tab=availability", "Day: Tuesday, Start: 14:00, End: 18:00, Timezone: 'Asia/Kolkata', isRecurring: True", "InterviewAvailability records saved in DB for the interviewer", "P1"),
            ("TC_HX_AVAIL_002", "Verify validation prevents overlapping availability windows on same day", "Interviewer on availability settings", "Window 1: 10:00-12:00, Window 2: 11:00-13:00", "Validation error 'Availability windows cannot overlap' displayed", "P2"),
            ("TC_HX_AVAIL_003", "Verify deleting or clearing availability removes future slot generation windows", "Existing availability window", "Click delete availability slot", "Record removed from InterviewAvailability; future slots no longer generated", "P2"),
            ("TC_HX_AVAIL_004", "Verify timezone conversion is accurately reflected across candidate booking view", "Interviewer in UTC, Candidate in IST (+5:30)", "Interviewer sets 09:00 UTC", "Candidate sees 14:30 IST on booking calendar", "P2"),
        ]
    },
    {
        "name": "Feedback & Scorecards",
        "sheet": "Feedback & Scorecards",
        "cases": [
            ("TC_HX_FEED_001", "Verify interviewer can submit structured rubric scorecard ratings (1-5)", "Interview call completed", "Ratings: Coding=4, Communication=5, Architecture=4", "InterviewFeedback record created; interview status updates to COMPLETED", "P1"),
            ("TC_HX_FEED_002", "Verify Cultural Fit score validation (integer 1 to 5 required)", "Interviewer submitting feedback", "Cultural Fit Score: 5", "culturalFitScore persisted and displayed in recruiter candidate briefing", "P1"),
            ("TC_HX_FEED_003", "Verify all recommendation values are supported (STRONG_HIRE, HIRE, LEANING_HIRE, NO_HIRE)", "Interviewer on feedback form", "Select each Recommendation enum value", "Recommendation correctly persisted and styled in UI review card", "P1"),
            ("TC_HX_FEED_004", "Verify duplicate feedback prevention on completed interview", "Interview feedback already submitted", "Attempt submitting second feedback for same interview", "HTTP 400 / 409 'Feedback already submitted for this interview'", "P2"),
            ("TC_HX_FEED_005", "Verify private recruiter briefing notes are visible to interviewer but hidden from candidate", "Recruiter adds internal candidate note", "Check candidate vs interviewer view", "Interviewer can read briefing; candidate portal has zero visibility of briefing", "P1"),
        ]
    },
    {
        "name": "Meeting Integration",
        "sheet": "Meeting Integration",
        "cases": [
            ("TC_HX_MEET_001", "Verify Schedular (MeetX) video room creation upon slot booking", "Candidate confirms booking", "POST /interviews/booking", "Response includes meetingId, hostJoinUrl, and candidateJoinUrl", "P1"),
            ("TC_HX_MEET_002", "Verify URL privilege separation: Host controls on hostJoinUrl vs attendee on candidateJoinUrl", "Confirmed interview record", "Inspect generated join URLs", "hostJoinUrl contains privileged host token; candidateJoinUrl contains attendee token", "P1"),
            ("TC_HX_MEET_003", "Verify offline dev fallback when SCHEDULAR_API_KEY is not configured", "SCHEDULAR_API_KEY empty", "Slot booking executed", "System falls back to https://meet.hirex.dev/join/{meetingId} cleanly", "P2"),
            ("TC_HX_MEET_004", "Verify .ics calendar attachment generation upon booking confirmation", "Booking confirmed", "Inspect confirmation response", "Valid iCalendar (.ics) event payload returned with correct start/end timestamps", "P2"),
        ]
    },
    {
        "name": "Offer Management",
        "sheet": "Offer Management",
        "cases": [
            ("TC_HX_OFF_001", "Verify recruiter admin can generate a branded offer letter with placeholders", "Candidate in OFFER_STAGE", "Salary: '₹18 LPA', StartDate: '2026-12-01', Expiry: 7 days", "PDF generated and uploaded to Cloudflare R2; Offer created in EXTENDED status", "P1"),
            ("TC_HX_OFF_002", "Verify offer expiration timestamp calculation based on expiryDays", "Recruiter sets expiryDays: 5", "Current time + 5 days", "Offer.expiresAt equals current timestamp + 5 days (120 hours)", "P2"),
            ("TC_HX_OFF_003", "Verify hourly cron job automatically transitions expired offers to EXPIRED", "Offer in EXTENDED status with expiresAt in past", "Trigger hourly cron (@Cron('0 * * * *'))", "Offer status updates to EXPIRED; candidate cannot accept offer", "P1"),
            ("TC_HX_OFF_004", "Verify PDF offer preview is accessible via presigned Cloudflare R2 URL", "Offer generated", "Recruiter clicks 'Preview Offer'", "PDF preview modal opens and displays interpolated candidate name and salary", "P2"),
            ("TC_HX_OFF_005", "Verify recruiter member cannot generate or extend formal job offers", "Logged in as Recruiter Member", "Attempt POST /recruiters/offers/generate", "HTTP 403 Forbidden; offer generation restricted to Recruiter Admin / Hiring Manager", "P1"),
        ]
    },
    {
        "name": "Offer Acceptance",
        "sheet": "Offer Acceptance",
        "cases": [
            ("TC_HX_OFFACC_001", "Verify candidate can review and accept extended offer with digital signature", "Candidate has active EXTENDED offer", "Signature: 'Alice Candidate'", "Offer status updates to ACCEPTED; Application auto-shifts to DOCUMENT_VERIFICATION", "P1"),
            ("TC_HX_OFFACC_002", "Verify candidate can decline extended offer with optional decline reason", "Active EXTENDED offer", "Click 'Decline Offer', Reason: 'Accepted another offer'", "Offer status updates to DECLINED; Application status updates to REJECTED / DECLINED", "P1"),
            ("TC_HX_OFFACC_003", "Verify candidate cannot accept an EXPIRED offer", "Offer in EXPIRED status", "Attempt POST /candidate/offers/{id}/accept", "HTTP 400 Bad Request ('This offer has expired and can no longer be accepted')", "P1"),
            ("TC_HX_OFFACC_004", "Verify candidate cannot accept an already ACCEPTED offer (idempotency)", "Offer already ACCEPTED", "Re-submit acceptance request", "HTTP 400 / 409 'Offer has already been processed'", "P2"),
        ]
    },
    {
        "name": "Document Verification",
        "sheet": "Document Verification",
        "cases": [
            ("TC_HX_DOC_001", "Verify candidate in DOCUMENT_VERIFICATION can upload multi-file compliance documents", "Candidate on /candidate/documents", "Type: GOVERNMENT_ID, Files: front.pdf, back.pdf", "Files streamed to Cloudflare R2; Document and DocumentFile records created (PENDING)", "P1"),
            ("TC_HX_DOC_002", "Verify recruiter can verify a submitted document with audit stamps", "Document in PENDING status", "Recruiter clicks 'Verify Document'", "Document status updates to VERIFIED; verifiedAt timestamp and verifiedBy userId recorded", "P1"),
            ("TC_HX_DOC_003", "Verify recruiter can reject a document with a mandatory rejection reason", "Document in PENDING status", "Reason: 'Scan illegible or expired ID'", "Document status updates to REJECTED; rejectionReason stored and displayed to candidate", "P1"),
            ("TC_HX_DOC_004", "Verify candidate re-uploading rejected document resets status to PENDING and clears audit stamps", "Document in REJECTED status", "Candidate uploads new replacement file", "rejectionReason, verifiedBy, and verifiedAt cleared; status resets to PENDING", "P1"),
            ("TC_HX_DOC_005", "Verify file size and format validation on compliance document uploads", "Candidate uploading doc", "Upload 25MB file or .exe file", "Upload rejected with 'Maximum file size is 10MB' / 'Invalid file format'", "P2"),
        ]
    },
    {
        "name": "Final Hiring Workflow",
        "sheet": "Final Hiring Workflow",
        "cases": [
            ("TC_HX_HIRE_001", "Verify 'Finalize Hire' is locked when mandatory compliance documents are PENDING or REJECTED", "Applicant in DOCUMENT_VERIFICATION with 1 unverified doc", "Recruiter attempts to select HIRED stage", "Button disabled / API rejects: 'All mandatory documents must be verified before hiring'", "P1"),
            ("TC_HX_HIRE_002", "Verify successful transition to HIRED once all required documents are VERIFIED", "All mandatory documents VERIFIED", "Recruiter clicks 'Finalize Hire'", "Application status transitions to HIRED (Terminal stage); success modal displayed", "P1"),
            ("TC_HX_HIRE_003", "Verify hired candidate appears on recruiter /hires dashboard with complete audit trail", "Candidate status = HIRED", "Recruiter navigates to /hires", "Candidate listed with job title, hired date, offer salary, and verified documents link", "P2"),
            ("TC_HX_HIRE_004", "Verify HIRED status is terminal and cannot be reverted", "Candidate in HIRED stage", "Attempt status change to INTERVIEW or SCREENING", "HTTP 400 Bad Request ('Cannot change status of finalized hire')", "P1"),
        ]
    },
    {
        "name": "Candidate Career Page",
        "sheet": "Candidate Career Page",
        "cases": [
            ("TC_HX_CP_001", "Verify public career page loads with company branding and published jobs", "Public visitor on /careers/hirex-demo-corp", "Open URL", "Page title: 'HireX Demo Corp Careers & Opportunities', company logo, and job list render", "P1"),
            ("TC_HX_CP_002", "Verify job keyword search filters job cards in real time", "Visitor on career page", "Type 'Frontend' in search input", "Only matching jobs are displayed; non-matching jobs filtered out dynamically", "P2"),
            ("TC_HX_CP_003", "Verify work mode filter chips (All, Hybrid, Remote, On-site)", "Jobs with diverse work modes", "Click 'Remote' filter button", "List updates immediately showing only Remote opportunities", "P2"),
            ("TC_HX_CP_004", "Verify clicking job card navigates to job detail and apply page", "Job card displayed", "Click 'Frontend Developer' job card", "Navigates to job details with responsibilities, skills, and 'Apply Now' CTA", "P1"),
            ("TC_HX_CP_005", "Verify 404 / friendly error display on invalid career page slug", "Visitor on invalid slug", "Open /careers/non-existent-tenant-999", "Clean 404 'Company career page not found' page displayed", "P2"),
        ]
    },
    {
        "name": "Candidate Reg & Profile",
        "sheet": "Candidate Reg & Profile",
        "cases": [
            ("TC_HX_CAND_PROF_001", "Verify candidate registration establishes user and candidate profile", "New candidate signup", "Name: 'Priya Patel', Email: 'priya@hirex.dev', Pass: 'Password123!'", "User created with role CANDIDATE, lands on candidate dashboard", "P1"),
            ("TC_HX_CAND_PROF_002", "Verify candidate profile view displays name, email, and resume hub link", "Logged in candidate on /candidate/profile", "Inspect profile details", "User details match registered account; resume upload section accessible", "P2"),
            ("TC_HX_CAND_PROF_003", "Verify candidate resume upload to Cloudflare R2 via Resume Hub", "Candidate on /candidate/resume", "Upload valid PDF resume", "File uploaded to Cloudflare R2; Resume record created and set as active profile resume", "P1"),
            ("TC_HX_CAND_PROF_004", "Verify candidate profile update (Headline, Phone, Location)", "Candidate editing profile", "Phone: '+91 9876543210', Location: 'Bengaluru'", "Updated details saved to Candidate model and reflected across applications", "P2"),
        ]
    },
    {
        "name": "Candidate Apply Wizard",
        "sheet": "Candidate Apply Wizard",
        "cases": [
            ("TC_HX_WIZ_001", "Verify multi-step wizard navigation: Step 1 (Profile) -> Step 2 (Questions) -> Step 3 (Review)", "Candidate applying to job", "Fill Step 1 -> Click Next", "Step indicator advances; Step 2 questions render according to job schema", "P1"),
            ("TC_HX_WIZ_002", "Verify Step 2 dynamic question validation blocks invalid or missing answers", "Job has required number question", "Enter negative number or leave blank", "Inline validation error blocks progression to Step 3", "P1"),
            ("TC_HX_WIZ_003", "Verify candidate draft responses auto-save to browser localStorage", "Candidate fills Step 1 and part of Step 2", "Trigger browser refresh (F5)", "Previously entered values restored from localStorage without data loss", "P2"),
            ("TC_HX_WIZ_004", "Verify beforeunload guard warns candidate on accidental tab closure", "Candidate has unsaved inputs in wizard", "Attempt closing tab or navigating away", "Native beforeunload dialog 'You have unsaved changes' triggered", "P2"),
            ("TC_HX_WIZ_005", "Verify Step 3 final review and application submission", "Candidate on Step 3", "Review answers, attach resume, click 'Submit Application'", "Application submitted; success confirmation screen with application ID displayed", "P1"),
        ]
    },
    {
        "name": "Candidate App Tracking",
        "sheet": "Candidate App Tracking",
        "cases": [
            ("TC_HX_TRACK_001", "Verify candidate dashboard lists all submitted applications with real-time status", "Candidate with submitted applications", "Open /applications on Candidate Portal", "Cards render showing Job Title, Company, Applied Date, and status badge (APPLIED, etc.)", "P1"),
            ("TC_HX_TRACK_002", "Verify candidate sees interview scheduling banner when status transitions to INTERVIEW", "Application in INTERVIEW stage", "Candidate views application details", "'Schedule your interview' banner and action button displayed", "P1"),
            ("TC_HX_TRACK_003", "Verify candidate sees offer review prompt when status transitions to OFFER_STAGE", "Application has active EXTENDED offer", "Candidate views application details", "'Offer Letter Available - Review & Sign' call to action displayed", "P1"),
            ("TC_HX_TRACK_004", "Verify candidate sees document upload checklist when status transitions to DOCUMENT_VERIFICATION", "Application in DOCUMENT_VERIFICATION", "Candidate views application details", "Required compliance document upload checklist rendered with status indicators", "P1"),
        ]
    },
    {
        "name": "API Testing",
        "sheet": "API Testing",
        "cases": [
            ("TC_HX_API_001", "Verify GET /jobs returns public jobs array with HTTP 200 and valid schema", "Public API request", "GET https://api.dev.hire.zobay.in/jobs", "HTTP 200, JSON list of job objects with id, title, companyId, skills, status", "P1"),
            ("TC_HX_API_002", "Verify GET /jobs/:id returns single job requisition details", "Valid existing job ID", "GET /jobs/{validJobId}", "HTTP 200 with job details, company object, and screening questions", "P1"),
            ("TC_HX_API_003", "Verify GET /jobs/:id returns HTTP 404 on non-existent job ID", "Random UUID", "GET /jobs/00000000-0000-0000-0000-000000000000", "HTTP 404 Not Found with standard error response envelope", "P2"),
            ("TC_HX_API_004", "Verify Better-Auth session endpoint GET /api/auth/get-session", "Authenticated cookie provided", "GET /api/auth/get-session with cookie", "HTTP 200 with session token, expiry timestamp, and user object", "P1"),
            ("TC_HX_API_005", "Verify GET /api/auth/get-session returns null or 401 without cookie", "Unauthenticated request", "GET /api/auth/get-session without cookie", "HTTP 200 with session: null or 401 Unauthorized", "P2"),
            ("TC_HX_API_006", "Verify global search GET /search?q=test returns role-scoped results", "Authenticated recruiter request", "GET /search?q=engineer", "HTTP 200 with matching jobs and candidates", "P2"),
            ("TC_HX_API_007", "Verify aggregator feeds GET /feeds/indeed-jobs.xml returns valid XML", "Public API request", "GET /feeds/indeed-jobs.xml", "HTTP 200, Content-Type: application/xml, valid Indeed job feed XML format", "P2"),
        ]
    },
    {
        "name": "Database & Data Integrity",
        "sheet": "Database & Data Integrity",
        "cases": [
            ("TC_HX_DB_001", "Verify multi-tenant isolation: Querying jobs or applications scopes by companyId", "Tenant A and Tenant B exist", "Query recruiter jobs endpoint as Tenant A", "Only jobs belonging to Tenant A companyId are returned; zero leak of Tenant B data", "P1"),
            ("TC_HX_DB_002", "Verify foreign key cascade: ApplicationForm cascades on Job delete", "Job with custom form", "Delete Job record", "ApplicationForm and its sections/questions cascade deleted without orphan records", "P1"),
            ("TC_HX_DB_003", "Verify foreign key safety: Resume deletion sets Application.resumeId to NULL", "Application referencing resumeId", "Delete or unlink Resume", "Application.resumeId set to NULL (onDelete: SetNull); no FK violation crash", "P1"),
            ("TC_HX_DB_004", "Verify unique constraint on Company.slug and User.email", "Existing company slug and user email", "Attempt creating duplicate slug or email", "Database throws unique constraint violation; API returns 400/409 error", "P1"),
            ("TC_HX_DB_005", "Verify SlotStatus updates atomically in a single transaction on booking", "Booking slot request", "Concurrent booking simulation", "SlotStatus row locked via SELECT ... FOR UPDATE or Prisma interactive transaction", "P1"),
        ]
    },
    {
        "name": "Integration Testing",
        "sheet": "Integration Testing",
        "cases": [
            ("TC_HX_INTG_001", "Verify end-to-end integration between Recruiter Portal and Backend API", "Recruiter UI action", "Create job in UI -> Check API response", "UI triggers POST /recruiters/jobs, receives 201, and updates job table in real time", "P1"),
            ("TC_HX_INTG_002", "Verify integration between Candidate Portal and Backend API on job application", "Candidate UI action", "Submit apply wizard -> Check API response", "POST /applications succeeds, DB record created, candidate dashboard updates", "P1"),
            ("TC_HX_INTG_003", "Verify integration between Interviewer Portal and Backend API on scorecard submission", "Interviewer UI action", "Submit scorecard -> Check API response", "POST /interviews/{id}/feedback succeeds, interview COMPLETED in Recruiter view", "P1"),
            ("TC_HX_INTG_004", "Verify Cloudflare R2 integration for document upload and presigned URL access", "Document upload request", "Upload PDF file to R2", "File stored in R2 bucket hirex-test-dev; presigned download URL opens valid file", "P1"),
            ("TC_HX_INTG_005", "Verify Schedular (MeetX) integration returns separate host and candidate meeting links", "Booking confirmed", "Call meeting provider API", "Interviewer gets hostJoinUrl; candidate gets candidateJoinUrl", "P1"),
        ]
    },
    {
        "name": "Security & RBAC",
        "sheet": "Security & RBAC",
        "cases": [
            ("TC_HX_SEC_001", "Verify ADR-001 Portal Session Isolation: Candidate cookie cannot access Recruiter Portal", "Active Candidate session cookie", "Attempt GET /recruiters/jobs or visit :3002/dashboard", "HTTP 403 Forbidden / redirects to /login; employer data protected", "P1"),
            ("TC_HX_SEC_002", "Verify Candidate cookie cannot access Interviewer Portal workspace", "Active Candidate session cookie", "Attempt GET /interviews or visit :3003/dashboard", "HTTP 403 Forbidden / redirects to /login; interview queue protected", "P1"),
            ("TC_HX_SEC_003", "Verify Interviewer session cannot perform recruiter admin actions (e.g. create jobs)", "Active Interviewer session cookie", "Attempt POST /recruiters/jobs", "HTTP 403 Forbidden; recruiter actions blocked for interviewer role", "P1"),
            ("TC_HX_SEC_004", "Verify HTTP-only, Secure, and SameSite=Lax cookie flags on Better-Auth session tokens", "Login response from backend", "Inspect Set-Cookie header", "Contains HttpOnly, Secure, SameSite=Lax, Domain=.hire.zobay.in", "P1"),
            ("TC_HX_SEC_005", "Verify SQL Injection and XSS protection on search and input fields", "Public search and custom question inputs", "Payload: ' OR 1=1 -- and <script>alert(1)</script>", "Inputs sanitized and parameterized by Prisma; zero script execution or SQL error", "P1"),
            ("TC_HX_SEC_006", "Verify Rate-Limiting protection on authentication endpoints", "Sign-in endpoint", "Submit 20 failed login attempts in 10 seconds", "System throttles requests with HTTP 429 Too Many Requests", "P2"),
        ]
    },
    {
        "name": "UI & Responsive Testing",
        "sheet": "UI & Responsive Testing",
        "cases": [
            ("TC_HX_UI_001", "Verify responsive layout of Recruiter Dashboard across Desktop and Tablet viewports", "Desktop (1920x1080) and Tablet (768x1024)", "Resize viewport in Playwright", "Sidebar collapses gracefully into hamburger menu on tablet; cards stack cleanly", "P2"),
            ("TC_HX_UI_002", "Verify responsive layout of Candidate Career Page across Mobile and Desktop", "Mobile (375x812) and Desktop (1440x900)", "Resize viewport in Playwright", "Job search input, filter chips, and job cards adapt seamlessly without horizontal scroll", "P2"),
            ("TC_HX_UI_003", "Verify modal dialog behaviors (ESC key close, backdrop click, focus trap)", "Any open modal in recruiter portal", "Press ESC key or click backdrop", "Modal dismisses properly and restores focus to triggering element", "P3"),
            ("TC_HX_UI_004", "Verify loading skeletons and empty states across tables and lists", "Data fetching states", "Simulate slow network or empty dataset", "Skeleton loaders render during fetch; descriptive empty states render when 0 items", "P3"),
            ("TC_HX_UI_005", "Verify toast notifications display on successful actions and auto-dismiss", "Save job or submit application", "Observe toast notification", "Green success toast appears at top/bottom right and auto-dismisses after 4 seconds", "P3"),
        ]
    },
    {
        "name": "Smoke Testing",
        "sheet": "Smoke Testing",
        "cases": [
            ("TC_HX_SMK_001", "Verify Recruiter Portal login page loads and responds with HTTP 200", "Public internet access", "Navigate to https://dev.recruiter.hire.zobay.in/login", "Page loads under 2s, title: 'HireX Employer – Recruiter Portal', inputs present", "P1"),
            ("TC_HX_SMK_002", "Verify Interviewer Portal login page loads and responds with HTTP 200", "Public internet access", "Navigate to https://dev.interviewer.hire.zobay.in/login", "Page loads under 2s, title: 'HireX - Interviewer Portal', inputs present", "P1"),
            ("TC_HX_SMK_003", "Verify Candidate Career Page loads and responds with HTTP 200", "Public internet access", "Navigate to https://dev.candidate.hire.zobay.in/careers/hirex-demo-corp", "Page loads under 2s, title: 'HireX Demo Corp Careers & Opportunities', job list rendered", "P1"),
            ("TC_HX_SMK_004", "Verify Backend API health check endpoint returns status: ok", "Public internet access", "GET https://api.dev.hire.zobay.in", "HTTP 200, JSON payload: status = 'ok', service = 'hirex-backend'", "P1"),
            ("TC_HX_SMK_005", "Verify public jobs API endpoint returns active job requisitions", "Public internet access", "GET https://api.dev.hire.zobay.in/jobs", "HTTP 200, array of published jobs returned", "P1"),
            ("TC_HX_SMK_006", "Verify Recruiter Admin can authenticate and land on /dashboard", "Valid recruiter credentials", "Sign in via recruiter portal UI", "Successfully reaches /dashboard with company context loaded", "P1"),
            ("TC_HX_SMK_007", "Verify Interviewer can authenticate and land on /dashboard", "Valid interviewer credentials", "Sign in via interviewer portal UI", "Successfully reaches /dashboard with interview queue loaded", "P1"),
            ("TC_HX_SMK_008", "Verify Candidate can authenticate and land on /dashboard", "Valid candidate credentials", "Sign in via candidate portal UI", "Successfully reaches /dashboard with applications loaded", "P1"),
        ]
    },
    {
        "name": "Sanity Testing",
        "sheet": "Sanity Testing",
        "cases": [
            ("TC_HX_SAN_001", "Verify new job creation and immediate reflection on public career page", "Recruiter admin logged in", "Publish job 'QA Automation Engineer'", "Job immediately appears in candidate career page search results", "P1"),
            ("TC_HX_SAN_002", "Verify candidate application creates card on recruiter applicant pipeline", "Job published", "Candidate applies to job", "New candidate card appears in APPLIED column on recruiter Kanban board", "P1"),
            ("TC_HX_SAN_003", "Verify candidate status progression from APPLIED to SCREENING updates recruiter view", "Candidate in APPLIED stage", "Recruiter updates status to SCREENING", "Status reflects SCREENING across both recruiter and candidate dashboards", "P1"),
            ("TC_HX_SAN_004", "Verify interview slot generation and candidate self-booking sanity", "Candidate in INTERVIEW stage", "Generate slot -> Candidate books", "Slot booked, interview CONFIRMED, meeting room created", "P1"),
            ("TC_HX_SAN_005", "Verify offer letter generation and candidate digital signature acceptance sanity", "Candidate in OFFER_STAGE", "Generate offer -> Candidate accepts", "Offer ACCEPTED, application auto-shifts to DOCUMENT_VERIFICATION", "P1"),
        ]
    },
    {
        "name": "Regression Testing",
        "sheet": "Regression Testing",
        "cases": [
            ("TC_HX_REG_001", "Verify full pipeline state transitions from APPLIED to HIRED across changes", "Test environment", "Execute full pipeline progression", "All 6 stages transition in forward-only sequence without regression defects", "P1"),
            ("TC_HX_REG_002", "Verify multivariable job search filter combinations (Keyword + Location + Work Mode)", "Diverse jobs dataset", "Filter: 'Engineer' + 'Bengaluru' + 'Remote'", "Correct subset of jobs returned matching all active filter criteria", "P2"),
            ("TC_HX_REG_003", "Verify recruiter form builder persists custom fields and questions correctly", "Form builder with 3 sections", "Save form schema -> Verify reload", "All custom sections, question types, and required flags remain intact", "P2"),
            ("TC_HX_REG_004", "Verify interviewer weekly recurring availability persistence and slot generation", "Interviewer availability set", "Verify recurring schedule across multiple weeks", "Slots generated accurately for future weeks matching recurring windows", "P2"),
            ("TC_HX_REG_005", "Verify multi-file compliance document rejection, candidate re-upload, and verification", "Candidate in DOCUMENT_VERIFICATION", "Upload -> Reject with reason -> Re-upload -> Verify", "Workflow completes with verifiedAt audit stamps preserved", "P1"),
        ]
    },
    {
        "name": "Performance & Load",
        "sheet": "Performance & Load",
        "cases": [
            ("TC_HX_PERF_001", "Verify single-user API response latency for public GET /jobs endpoint (SLO: < 200ms)", "Live dev API", "10 consecutive GET requests to /jobs", "Median response time < 200ms, 0% error rate", "P2"),
            ("TC_HX_PERF_002", "Verify single-user API response latency for root health check (SLO: < 100ms)", "Live dev API", "10 consecutive GET requests to /", "Median response time < 100ms, 0% error rate", "P2"),
            ("TC_HX_PERF_003", "Verify browser page load time for Recruiter Login page (SLO: < 2.0s)", "Headless browser in Playwright", "Navigate to recruiter login page", "Page 'load' event fired in < 2000ms", "P2"),
            ("TC_HX_PERF_004", "Verify browser page load time for Candidate Career Page (SLO: < 2.0s)", "Headless browser in Playwright", "Navigate to candidate career page", "Page 'load' event fired in < 2000ms", "P2"),
            ("TC_HX_PERF_005", "Verify concurrent API request handling under controlled load (5 concurrent users)", "Async HTTP requests in Python", "5 concurrent users querying /jobs and /search", "Throughput > 15 req/s, 0% dropped connections, P95 < 500ms", "P2"),
        ]
    },
    {
        "name": "Webhook Testing",
        "sheet": "Webhook Testing",
        "cases": [
            ("TC_HX_WH_001", "Verify Schedular (MeetX) webhook ingestion with valid HMAC SHA-256 signature", "Active interview in CONFIRMED status", "POST /webhooks/schedular with valid x-signature and event: 'meeting.ended'", "HTTP 200 OK; interview status transitions to COMPLETED", "P1"),
            ("TC_HX_WH_002", "Verify webhook fails closed (HTTP 401/403) when HMAC signature is invalid or missing", "Inbound webhook request", "POST /webhooks/schedular with invalid signature", "HTTP 401 Unauthorized / 403 Forbidden; payload rejected", "P1"),
            ("TC_HX_WH_003", "Verify meeting.mom.ready webhook attaches Minutes of Meeting and transcript to interview", "Interview in COMPLETED status", "Webhook event: 'meeting.mom.ready'", "Interview record updated with AI transcript and extracted action items", "P2"),
            ("TC_HX_WH_004", "Verify webhook idempotency on duplicate event delivery", "Webhook event already processed", "Resend identical meeting.ended webhook payload", "HTTP 200 OK without corrupting interview state or duplicating records", "P2"),
        ]
    }
]

def create_test_cases_workbook():
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)
    
    # Validation objects
    status_dv = DataValidation(type="list", formula1='"Pass,Fail,Blocked,Not Executed"', allow_blank=True)
    priority_dv = DataValidation(type="list", formula1='"P1,P2,P3,P4"', allow_blank=True)
    
    total_cases = 0
    
    for mod in MODULE_DEFINITIONS:
        sheet_title = mod["sheet"][:31] # Excel max sheet name length is 31
        ws = wb.create_sheet(title=sheet_title)
        
        # Add validations to worksheet
        ws.add_data_validation(status_dv)
        ws.add_data_validation(priority_dv)
        
        # Specification Header (Rows 1-6)
        header_metadata = [
            ("Project Name", "HireX"),
            ("Module Name", mod["name"]),
            ("Created By", "Saifan"),
            ("Created Date", "2026-11-02"),
            ("Reviewed By", "Pending Review"),
            ("Version", "1")
        ]
        
        for r_idx, (field, val) in enumerate(header_metadata, start=1):
            cell_lbl = ws.cell(row=r_idx, column=1, value=field)
            cell_val = ws.cell(row=r_idx, column=2, value=val)
            
            cell_lbl.font = BOLD_FONT
            cell_lbl.fill = METADATA_LABEL_FILL
            cell_lbl.border = THIN_BORDER
            
            cell_val.font = REGULAR_FONT
            cell_val.border = THIN_BORDER
            cell_val.alignment = Alignment(horizontal="left")
            
        # Row 7 is empty spacing
        
        # Row 8: Table Column Headers
        table_headers = [
            "TC_ID",
            "Scenario Description",
            "Preconditions",
            "Test_Data",
            "Expected Result",
            "Actual Result",
            "Status",
            "Priority"
        ]
        
        header_row = 8
        for c_idx, h_text in enumerate(table_headers, start=1):
            cell = ws.cell(row=header_row, column=c_idx, value=h_text)
            cell.font = WHITE_FONT
            cell.fill = PURPLE_HEADER_FILL
            cell.border = HEADER_BORDER
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            
        ws.row_dimensions[header_row].height = 26
        
        # Populate Test Cases starting from Row 9
        cases = mod["cases"]
        start_row = 9
        for i, tc in enumerate(cases):
            cur_row = start_row + i
            ws.row_dimensions[cur_row].height = 36
            total_cases += 1
            
            tc_id, desc, pre, data, expected, priority = tc
            actual = "Not Executed"
            status = "Not Executed"
            
            row_data = [tc_id, desc, pre, data, expected, actual, status, priority]
            
            is_even = (i % 2 == 0)
            row_fill = ZEBRA_FILL if is_even else PatternFill(fill_type=None)
            
            for c_idx, val in enumerate(row_data, start=1):
                cell = ws.cell(row=cur_row, column=c_idx, value=val)
                cell.font = REGULAR_FONT
                cell.border = THIN_BORDER
                cell.fill = row_fill
                
                if c_idx == 1: # TC_ID
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.font = BOLD_FONT
                elif c_idx in [2, 3, 4, 5, 6]: # Descriptions & Results
                    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
                elif c_idx == 7: # Status
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    status_dv.add(cell)
                elif c_idx == 8: # Priority
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    priority_dv.add(cell)
                    
        # Apply Conditional Formatting for Status column (G)
        green_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
        green_font = Font(name="Calibri", size=10, bold=True, color="166534")
        red_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        red_font = Font(name="Calibri", size=10, bold=True, color="991B1B")
        yellow_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
        yellow_font = Font(name="Calibri", size=10, bold=True, color="92400E")
        gray_fill = PatternFill(start_color="F3F4F6", end_color="F3F4F6", fill_type="solid")
        gray_font = Font(name="Calibri", size=10, color="4B5563")

        max_row = start_row + len(cases) - 1
        status_range = f"G{start_row}:G{max_row}"
        
        ws.conditional_formatting.add(status_range, CellIsRule(operator='equal', formula=['"Pass"'], stopIfTrue=True, fill=green_fill, font=green_font))
        ws.conditional_formatting.add(status_range, CellIsRule(operator='equal', formula=['"Fail"'], stopIfTrue=True, fill=red_fill, font=red_font))
        ws.conditional_formatting.add(status_range, CellIsRule(operator='equal', formula=['"Blocked"'], stopIfTrue=True, fill=yellow_fill, font=yellow_font))
        ws.conditional_formatting.add(status_range, CellIsRule(operator='equal', formula=['"Not Executed"'], stopIfTrue=True, fill=gray_fill, font=gray_font))
        
        # Freeze Panes at Row 9, Column 2 (Keep headers & TC_ID visible on scroll)
        ws.freeze_panes = "B9"
        
        # Enable Filters on Header Row
        ws.auto_filter.ref = f"A8:H{max_row}"
        
        # Column Widths
        col_widths = {
            1: 18, # TC_ID
            2: 38, # Scenario Description
            3: 28, # Preconditions
            4: 28, # Test_Data
            5: 38, # Expected Result
            6: 28, # Actual Result
            7: 16, # Status
            8: 12  # Priority
        }
        for col_idx, width in col_widths.items():
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = width

    output_path = "HireX_Complete_Test_Cases.xlsx"
    wb.save(output_path)
    print(f"Successfully generated {output_path} with {len(MODULE_DEFINITIONS)} module worksheets and {total_cases} total test cases!")

if __name__ == "__main__":
    create_test_cases_workbook()

