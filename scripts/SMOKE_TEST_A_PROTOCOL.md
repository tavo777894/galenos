# SMOKE TEST A PROTOCOL - PROFESSIONAL RUNBOOK

**Document Version:** 1.0  
**Last Updated:** 2026-01-13  
**System:** Galenos - Historia Clínica Electrónica  
**Script:** `D:\galenos\scripts\smoke_test_a.ps1`  
**PowerShell Version:** 5.1+  
**Test Coverage:** 36 test cases across 7 phases

---

## 1. PURPOSE & SCOPE

### What This Test Validates

The Smoke Test A is a **rapid validation suite** that proves the FastAPI backend is functional and demo-ready. It validates:

-  **Authentication & Authorization**  Admin and Doctor login, JWT token handling, 401/403 enforcement
-  **CRUD Operations**  Create, Read, Update, Delete for Encounters, Templates, Snippets
-  **Favorites System**  Add/remove favorites, filter by favorites, idempotent operations
-  **PDF Generation**  WeasyPrint integration, patient cards, document storage
-  **Data Relationships**  Patient-Encounter links, Template-Encounter associations, Attachment queries
-  **API Health**  `/health`, `/docs`, OpenAPI spec accessibility
-  **Error Handling**  404 for missing resources, proper HTTP status codes

**Test Duration:** ~1530 seconds (depending on hardware)  
**Environment:** Local development (http://localhost:8000)

### What This Is NOT

-  NOT a replacement for unit tests
-  NOT integration testing
-  NOT load/performance testing
-  NOT security penetration testing
-  NOT a CI/CD gate (yet)

### Test Phases

| Phase | Focus Area | Test Count |
|------:|------------|-----------:|
| F0 | Health & Authentication | 6 |
| F1 | Encounters (SOAP) | 6 |
| F2 | Templates | 5 |
| F3 | Snippets | 5 |
| F4 | Favorites | 6 |
| F5 | Documents/PDF | 5 |
| F6 | Attachments | 1 |
| F7 | Negative Cases | 2 |
| **Total** | | **36** |

---

## 2. PRECONDITIONS

Before running the smoke test, ensure the following conditions are met.

### Backend Service Running

Start uvicorn from project root:

```powershell
cd D:\galenos
.\venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

---

## 3. RUN COMMANDS

### Standard Execution

    cd D:\galenos
    powershell -ExecutionPolicy Bypass -File .\scripts\smoke_test_a.ps1

### With Log Capture (recommended for CI/CD)

    cd D:\galenos
    powershell -ExecutionPolicy Bypass -File .\scripts\smoke_test_a.ps1 2>&1 | Tee-Object -FilePath .\tmp\smoke\smoke_test_output.log

### Summary Only (quick validation)

    cd D:\galenos
    powershell -ExecutionPolicy Bypass -File .\scripts\smoke_test_a.ps1 2>&1 | Select-String -Pattern "(PASS|FAIL|Summary):"

### Validate Environment Before Testing

    $PSVersionTable.PSVersion
    Invoke-RestMethod -Uri "http://localhost:8000/health"
    Test-Path D:\galenos\tmp\smoke

---

## 4. EXPECTED OUTPUT

### Success Output (example)

    SMOKE TEST A
    PASS: F0 /health
    PASS: F0 /docs
    PASS: F0 /openapi.json
    PASS: F0 login admin
    PASS: F0 login doctor
    ...
    Summary: Total=36 Passed=36 Failed=0

### Failure Output (example)

    FAIL: F1 POST /encounters - Validation error
    HTTP Status: 422
    Response Body: {"detail":[{"loc":["body","specialty"],"msg":"field required"}]}

### Artifact Locations

Generated PDFs are saved to: D:\galenos\tmp\smoke\

Expected files:
- preview_{document_id}.pdf
- download_{document_id}.pdf
- patient_1_card.pdf

Verify artifacts:

    Get-ChildItem D:\galenos\tmp\smoke\*.pdf | Select-Object Name, Length, LastWriteTime

---

## 5. FASTAPI ROUTING & TRAILING SLASH RULES

### The Trailing Slash Problem

FastAPI enforces strict URL matching. A request to the wrong URL triggers a **307 Temporary Redirect**. PowerShells `Invoke-RestMethod` follows redirects but can drop the `Authorization` header, causing false 401 errors.

### Routing Rules

| Route Type | Example | Trailing Slash? |
|-----------|---------|-----------------|
| Collection endpoint | `/api/v1/templates/` | YES |
| Resource by ID | `/api/v1/templates/1` | NO |
| Nested resource | `/api/v1/patients/1/encounters` | NO |
| Query params (collection) | `/api/v1/templates/?only_favorites=true` | YES (keep slash before `?`) |

### Evidence pattern (logs)

---

## 6. POWERSHELL 5.1 PITFALLS & FIXES

### Pitfall #1: Single-item array unwrapping

Problem: When an API returns a JSON array with exactly one element, PowerShell may unwrap it to a scalar PSCustomObject. Count behaves unexpectedly.

Fix pattern: Always force arrays with @(...)

    $list = @(Normalize-Array $resp)
    if ($list.Count -lt 1) { throw "favorites empty" }

### Pitfall #2: JSON errors in ErrorDetails.Message

PowerShell 5.1 can place JSON error bodies in $ErrorRecord.ErrorDetails.Message.

    function Get-ErrorContent {
        param($ErrorRecord)
        try {
            if ($ErrorRecord.ErrorDetails -and $ErrorRecord.ErrorDetails.Message) {
                return $ErrorRecord.ErrorDetails.Message
            }
            $stream = $ErrorRecord.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($stream)
            return $reader.ReadToEnd()
        } catch { return "" }
    }

### Pitfall #3: Invoke-WebRequest -OutFile header loss

When using -OutFile, PowerShell may not populate headers reliably.
Fix: request first, validate headers, then save bytes.

---

## 7. TROUBLESHOOTING GUIDE

| Symptom | Likely Cause | Fix |
|--------|--------------|-----|
| Cannot connect to API | backend not running | start uvicorn, verify /health |
| 401 after redirect | missing trailing slash | ensure collection endpoints use / |
| 401 on first test | bad credentials / seed missing | re-run scripts/seed_clinical.py |
| 404 Patient id=1 | missing seed data | seed DB |
| 422 field required | payload schema mismatch | check error body and payload |
| favorites empty | array unwrap | ensure @() wrapper |
| PDF too small | WeasyPrint runtime issue | check backend logs for GTK/Pango |
| Missing Content-Disposition | -OutFile behavior | download without -OutFile then save |
| Connection refused DB | postgres down | start docker postgres |
| Template id=1 missing | seed incomplete | seed DB |

Verbose diagnostics:

    $VerbosePreference = "Continue"
    .\scripts\smoke_test_a.ps1

---

## 8. DEMO RUNBOOK

### Pre-demo setup (5 minutes before)

1) Start PostgreSQL (if using Docker)

```powershell
docker start galenos-postgres
Start-Sleep -Seconds 3
docker exec galenos-postgres pg_isready -U galenos

---

## 9. ACCEPTANCE CHECKLIST

- 3 consecutive runs pass (no flakiness)
- Idempotent behavior (re-runs dont break)
- Cleanup works (resources deactivated/deleted as expected)
- PDFs generated and size reasonable (> 1000 bytes)
- Graceful failure when API is down
- Script completes < 60 seconds or fails fast with clear message
- PowerShell 5.1 compatible
- No admin privileges required

Quick verification:

    for ($i=1; $i -le 3; $i++) {
      Write-Host "Run $i of 3..."
      .\scripts\smoke_test_a.ps1 2>&1 | Select-String "Summary:"
    }

---

## 10. APPENDIX

Quick reference:
- Script: D:\galenos\scripts\smoke_test_a.ps1
- Artifacts: D:\galenos\tmp\smoke\
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs
- OpenAPI: http://localhost:8000/openapi.json

---

## CHANGE LOG

v1.0 (2026-01-13)  Initial professional release

- 36 test cases across phases F0F7
- PowerShell 5.1 compatibility
- Trailing slash rules (FastAPI 307 -> auth header drop risk)
- PS pitfalls: single-item arrays, ErrorDetails.Message, OutFile header loss
- Troubleshooting guide + demo runbook + acceptance checklist

---
END OF RUNBOOK

