param(
    [string]$BaseUrl = "http://localhost:8000"
)

$ErrorActionPreference = "Stop"

if (-not $BaseUrl.StartsWith("http")) {
    throw "BaseUrl must start with http or https: $BaseUrl"
}

$ApiBase = "$BaseUrl/api/v1"
$Cleanup = $true

$TmpDir = Join-Path -Path $PSScriptRoot -ChildPath "..\tmp\smoke"
$TmpPath = Resolve-Path -Path $TmpDir -ErrorAction SilentlyContinue
if ($TmpPath) {
    $TmpDir = $TmpPath.Path
} else {
    $TmpDir = (New-Item -ItemType Directory -Force -Path $TmpDir).FullName
}

$Total = 0
$Passed = 0
$Failed = 0
$CreatedArtifacts = @()

function Write-Result {
    param(
        [string]$Status,
        [string]$Name,
        [string]$Detail = ""
    )
    if ($Detail) {
        Write-Host ("{0}: {1} - {2}" -f $Status, $Name, $Detail)
    } else {
        Write-Host ("{0}: {1}" -f $Status, $Name)
    }
}

function Print-FailDetails {
    param(
        [string]$Name,
        [string]$Detail,
        $ErrorRecord = $null
    )
    Write-Result "FAIL" $Name $Detail
    if ($ErrorRecord) {
        $status = Get-ErrorStatus $ErrorRecord
        $content = Get-ErrorContent $ErrorRecord
        if ($content -and $content.Length -gt 1500) {
            $content = $content.Substring(0, 1500)
        }
        if ($status) {
            Write-Host ("HTTP Status: {0}" -f $status)
        }
        if ($content) {
            Write-Host ("HTTP Body: {0}" -f $content)
        }
    }
}

function Fail-Now {
    param(
        [string]$Name,
        [string]$Detail,
        $ErrorRecord = $null
    )
    Print-FailDetails -Name $Name -Detail $Detail -ErrorRecord $ErrorRecord
    throw "Test failed: $Name"
}

function Pass-Now {
    param([string]$Name)
    $global:Passed++
    Write-Result "PASS" $Name
}

function Run-Test {
    param(
        [string]$Name,
        [scriptblock]$Action,
        [bool]$Critical = $true
    )
    $global:Total++
    try {
        & $Action
        Pass-Now $Name
    } catch {
        $global:Failed++
        Fail-Now -Name $Name -Detail $_.Exception.Message -ErrorRecord $_
    }
}

function Invoke-Json {
    param(
        [string]$Method,
        [string]$Url,
        [hashtable]$Headers = @{},
        $Body = $null,
        [string]$ContentType = "application/json",
        [int]$TimeoutSec = 0
    )

    $params = @{
        Method = $Method
        Uri = $Url
        Headers = $Headers
        ErrorAction = "Stop"
        MaximumRedirection = 0
    }

    if ($Body -ne $null) {
        if ($ContentType -eq "application/json" -and -not ($Body -is [string])) {
            $params.Body = ($Body | ConvertTo-Json -Depth 8)
        } else {
            $params.Body = $Body
        }
        $params.ContentType = $ContentType
    }

    if ($TimeoutSec -gt 0) {
        $params.TimeoutSec = $TimeoutSec
    }

    return Invoke-RestMethod @params
}

function Get-ErrorStatus {
    param($ErrorRecord)
    try {
        return [int]$ErrorRecord.Exception.Response.StatusCode
    } catch {
        return $null
    }
}

function Get-ErrorContent {
    param($ErrorRecord)
    try {
        # PowerShell 5.1+ stores error response in ErrorDetails
        if ($ErrorRecord.ErrorDetails -and $ErrorRecord.ErrorDetails.Message) {
            return $ErrorRecord.ErrorDetails.Message
        }
        # Fallback to reading response stream
        $stream = $ErrorRecord.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        return $reader.ReadToEnd()
    } catch {
        return ""
    }
}

function Invoke-ExpectError {
    param(
        [string]$Method,
        [string]$Url,
        [int[]]$ExpectedStatus,
        [hashtable]$Headers = @{},
        $Body = $null,
        [string]$ContentType = "application/json"
    )

    try {
        $null = Invoke-Json -Method $Method -Url $Url -Headers $Headers -Body $Body -ContentType $ContentType
        return @{ Status = 200; Content = "" }
    } catch {
        $status = Get-ErrorStatus $_
        if ($status -eq 307 -or $status -eq 308) {
            throw "Redirect $status (Trailing slash mismatch): $Url"
        }
        $content = Get-ErrorContent $_
        if ($ExpectedStatus -contains $status) {
            return @{ Status = $status; Content = $content }
        }
        throw "Unexpected HTTP status $status"
    }
}

function Invoke-Expect204 {
    param(
        [string]$Method,
        [string]$Url,
        [hashtable]$Headers = @{}
    )

    $resp = Invoke-WebRequest -Method $Method -Uri $Url -Headers $Headers -ErrorAction Stop
    if ($resp.StatusCode -ne 204) {
        throw "Expected 204 got $($resp.StatusCode)"
    }
}

function Normalize-Array {
    param($Response)
    if ($Response -is [System.Array]) { return $Response }
    if ($Response -and $Response.items) { return $Response.items }
    if ($Response -and $Response.data) { return $Response.data }
    return @()
}

function Invoke-DownloadPdfAndValidate {
    param(
        [string]$Url,
        [string]$OutFile,
        [hashtable]$Headers = @{},
        [switch]$ExpectAttachment
    )

    # Get response without -OutFile to access headers
    $resp = Invoke-WebRequest -Uri $Url -Headers $Headers -ErrorAction Stop

    # Validate Content-Disposition header if expected
    if ($ExpectAttachment) {
        $cd = $resp.Headers["Content-Disposition"]
        if (-not $cd -or $cd -notmatch "attachment") {
            throw "Missing or invalid Content-Disposition: attachment"
        }
    }

    # Save content to file
    [System.IO.File]::WriteAllBytes($OutFile, $resp.Content)

    # Validate PDF format
    $bytes = [System.IO.File]::ReadAllBytes($OutFile)
    if ($bytes.Length -lt 1000) {
        throw "PDF too small: $($bytes.Length) bytes"
    }
    $head = [System.Text.Encoding]::ASCII.GetString($bytes[0..3])
    if ($head -ne "%PDF") {
        throw "Invalid PDF header: $head"
    }
}

function Get-AuthHeaders {
    param([string]$Token)
    return @{ Authorization = "Bearer $Token" }
}

function Invoke-IdempotentFavorite {
    param(
        [string]$Method,
        [string]$Url,
        [hashtable]$Headers = @{}
    )

    try {
        $resp = Invoke-WebRequest -Method $Method -Uri $Url -Headers $Headers -ErrorAction Stop
        if ($resp.StatusCode -lt 200 -or $resp.StatusCode -ge 300) {
            throw "Unexpected HTTP status $($resp.StatusCode)"
        }
    } catch {
        $status = Get-ErrorStatus $_
        $content = Get-ErrorContent $_
        if ($Method -eq "POST") {
            if ($status -eq 400 -and $content -match "already") { return }
            throw "Unexpected favorite error: $status $content"
        }
        if ($Method -eq "DELETE") {
            if (($status -eq 400 -or $status -eq 404) -and $content -match "not found|not in favorites") { return }
            throw "Unexpected unfavorite error: $status $content"
        }
        throw "Unexpected favorite method: $Method"
    }
}

Write-Host "SMOKE TEST A"
Write-Host "Preflight: START"
Write-Host ("PowerShell: {0}" -f $PSVersionTable.PSVersion)
Write-Host ("BaseUrl: {0}" -f $BaseUrl)
Write-Host ("ApiBase: {0}" -f $ApiBase)
Write-Host ("Cleanup: {0}" -f $Cleanup)
Write-Host ("TmpDir: {0}" -f $TmpDir)

try {
    $null = Invoke-Json -Method "GET" -Url "$BaseUrl/health" -TimeoutSec 5
} catch {
    Write-Host "Preflight: FAIL - Cannot reach API."
    Write-Host "Start backend:"
    Write-Host "  .\\venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    exit 1
}

Write-Host "Preflight: OK"

# Phase 0
Run-Test "F0 /health" {
    $resp = Invoke-Json -Method "GET" -Url "$BaseUrl/health"
    if (-not $resp -or $resp.status -ne "healthy") { throw "Health not healthy" }
}

Run-Test "F0 /docs" {
    $resp = Invoke-WebRequest -Uri "$BaseUrl/docs" -ErrorAction Stop
    if ($resp.StatusCode -ne 200) { throw "Docs not 200" }
    if ($resp.Content -notmatch "swagger-ui") { throw "Docs swagger-ui missing" }
}

Run-Test "F0 /openapi.json" {
    $resp = Invoke-Json -Method "GET" -Url "$BaseUrl/openapi.json"
    if (-not $resp.openapi) { throw "openapi missing" }
    if (-not $resp.info) { throw "info missing" }
    if (-not $resp.paths) { throw "paths missing" }
}

$adminToken = $null
$doctorToken = $null

Run-Test "F0 login admin" {
    $body = "username=admin&password=admin123"
    $resp = Invoke-Json -Method "POST" -Url "$ApiBase/auth/login" -Body $body -ContentType "application/x-www-form-urlencoded"
    if (-not $resp.access_token) { throw "Missing access_token" }
    $global:adminToken = $resp.access_token
}

Run-Test "F0 login doctor" {
    $body = "username=doctor&password=doctor123"
    $resp = Invoke-Json -Method "POST" -Url "$ApiBase/auth/login" -Body $body -ContentType "application/x-www-form-urlencoded"
    if (-not $resp.access_token) { throw "Missing access_token" }
    $global:doctorToken = $resp.access_token
}

Run-Test "F0 /patients no token 401" {
    $res = Invoke-ExpectError -Method "GET" -Url "$ApiBase/patients/" -ExpectedStatus @(401)
    if ($res.Status -ne 401) { throw "Expected 401" }
}

# Phase 1 Encounters
$encounterId = $null
Run-Test "F1 GET /encounters" {
    $resp = Invoke-Json -Method "GET" -Url "$ApiBase/encounters/" -Headers (Get-AuthHeaders $doctorToken)
    $list = @(Normalize-Array $resp)
}

Run-Test "F1 POST /encounters" {
    $body = @{ patient_id = 1; specialty = "CARDIOLOGIA"; subjective = "[SMOKE TEST] initial"; objective = ""; assessment = ""; plan = "" }
    $resp = Invoke-Json -Method "POST" -Url "$ApiBase/encounters/" -Headers (Get-AuthHeaders $doctorToken) -Body $body
    if (-not $resp.id) { throw "Missing encounter id" }
    $global:encounterId = $resp.id
}

Run-Test "F1 GET /encounters/{id}" {
    $resp = Invoke-Json -Method "GET" -Url "$ApiBase/encounters/$encounterId" -Headers (Get-AuthHeaders $doctorToken)
    if ($resp.subjective -notmatch "\[SMOKE TEST\]") { throw "Subjective missing tag" }
}

Run-Test "F1 PUT /encounters/{id}" {
    $body = @{ assessment = "[SMOKE TEST] updated" }
    $resp = Invoke-Json -Method "PUT" -Url "$ApiBase/encounters/$encounterId" -Headers (Get-AuthHeaders $doctorToken) -Body $body
}

Run-Test "F1 PATCH /encounters/{id}/status" {
    $resp = Invoke-Json -Method "PATCH" -Url "$ApiBase/encounters/$encounterId/status?new_status=SIGNED" -Headers (Get-AuthHeaders $doctorToken)
    if ($resp.status -ne "SIGNED") { throw "Status not SIGNED" }
}

Run-Test "F1 GET /encounters?patient_id=1" {
    $resp = Invoke-Json -Method "GET" -Url "$ApiBase/encounters/?patient_id=1" -Headers (Get-AuthHeaders $adminToken)
    $list = @(Normalize-Array $resp)
    if (-not ($list | Where-Object { $_.id -eq $encounterId })) { throw "Encounter not found" }
}

# Phase 2 Templates
$templateId = $null
Run-Test "F2 GET /templates" {
    $resp = Invoke-Json -Method "GET" -Url "$ApiBase/templates/" -Headers (Get-AuthHeaders $adminToken)
    $list = @(Normalize-Array $resp)
    foreach ($item in $list) {
        if (-not $item.PSObject.Properties.Name -contains "requires_photo") { throw "requires_photo missing" }
    }
}

Run-Test "F2 GET /templates/1" {
    $resp = Invoke-Json -Method "GET" -Url "$ApiBase/templates/1" -Headers (Get-AuthHeaders $doctorToken)
    if (-not $resp.PSObject.Properties.Name -contains "requires_photo") { throw "requires_photo missing" }
}

Run-Test "F2 POST /templates" {
    $body = @{ title = "[SMOKE TEST] template"; specialty = "DERMATOLOGIA"; description = "[SMOKE TEST]"; requires_photo = 0; is_active = 1 }
    $resp = Invoke-Json -Method "POST" -Url "$ApiBase/templates/" -Headers (Get-AuthHeaders $doctorToken) -Body $body
    if (-not $resp.id) { throw "Missing template id" }
    $global:templateId = $resp.id
}

Run-Test "F2 PUT /templates/{id}" {
    $body = @{ description = "[SMOKE TEST] updated"; is_active = 1 }
    $null = Invoke-Json -Method "PUT" -Url "$ApiBase/templates/$templateId" -Headers (Get-AuthHeaders $adminToken) -Body $body
}

Run-Test "F2 DELETE /templates/{id}" {
    Invoke-Expect204 -Method "DELETE" -Url "$ApiBase/templates/$templateId" -Headers (Get-AuthHeaders $doctorToken)
}

# Phase 3 Snippets
$snippetId = $null
Run-Test "F3 GET /snippets" {
    $resp = Invoke-Json -Method "GET" -Url "$ApiBase/snippets/" -Headers (Get-AuthHeaders $doctorToken)
    $list = @(Normalize-Array $resp)
    foreach ($item in $list) {
        if (-not $item.PSObject.Properties.Name -contains "specialty") { throw "specialty missing" }
    }
}

Run-Test "F3 GET /snippets/1" {
    $resp = Invoke-Json -Method "GET" -Url "$ApiBase/snippets/1" -Headers (Get-AuthHeaders $adminToken)
    if ($resp.usage_count -lt 1) { throw "usage_count < 1" }
}

Run-Test "F3 POST /snippets" {
    $body = @{ title = "[SMOKE TEST] snippet"; content = "[SMOKE TEST]"; category = "EXAMEN"; specialty = "NEUROLOGIA"; is_active = 1 }
    $resp = Invoke-Json -Method "POST" -Url "$ApiBase/snippets/" -Headers (Get-AuthHeaders $doctorToken) -Body $body
    if (-not $resp.id) { throw "Missing snippet id" }
    $global:snippetId = $resp.id
}

Run-Test "F3 GET /snippets?category=EXAMEN" {
    $resp = Invoke-Json -Method "GET" -Url "$ApiBase/snippets/?category=EXAMEN" -Headers (Get-AuthHeaders $doctorToken)
    $list = @(Normalize-Array $resp)
}

Run-Test "F3 DELETE /snippets/{id}" {
    Invoke-Expect204 -Method "DELETE" -Url "$ApiBase/snippets/$snippetId" -Headers (Get-AuthHeaders $adminToken)
}

# Phase 4 Favorites
Run-Test "F4 POST /favorites/templates/1" {
    Invoke-IdempotentFavorite -Method "POST" -Url "$ApiBase/favorites/templates/1" -Headers (Get-AuthHeaders $doctorToken)
}

Run-Test "F4 GET /templates/1 is_favorite" {
    $resp = Invoke-Json -Method "GET" -Url "$ApiBase/templates/1" -Headers (Get-AuthHeaders $doctorToken)
    if (-not $resp.is_favorite) { throw "is_favorite false" }
}

Run-Test "F4 GET /templates?only_favorites=true" {
    $resp = Invoke-Json -Method "GET" -Url "$ApiBase/templates/?only_favorites=true" -Headers (Get-AuthHeaders $doctorToken)
    $list = @(Normalize-Array $resp)  # Force array for PowerShell single-item quirk
    if ($list.Count -lt 1) { throw "favorites empty" }
}

Run-Test "F4 DELETE /favorites/templates/1" {
    Invoke-IdempotentFavorite -Method "DELETE" -Url "$ApiBase/favorites/templates/1" -Headers (Get-AuthHeaders $doctorToken)
}

Run-Test "F4 POST /favorites/snippets/1" {
    Invoke-IdempotentFavorite -Method "POST" -Url "$ApiBase/favorites/snippets/1" -Headers (Get-AuthHeaders $adminToken)
}

Run-Test "F4 GET /snippets?only_favorites=true" {
    $resp = Invoke-Json -Method "GET" -Url "$ApiBase/snippets/?only_favorites=true" -Headers (Get-AuthHeaders $adminToken)
    $list = @(Normalize-Array $resp)  # Force array for PowerShell single-item quirk
    if ($list.Count -lt 1) { throw "favorites empty" }
}

# Phase 5 Documents/PDF
$documentId = $null
Run-Test "F5 POST /patients/1/generate-card" {
    $resp = Invoke-Json -Method "POST" -Url "$ApiBase/patients/1/generate-card" -Headers (Get-AuthHeaders $doctorToken)
    if (-not $resp.document_id) { throw "Missing document_id" }
    $global:documentId = $resp.document_id
}

Run-Test "F5 GET /documents includes document_id" {
    $resp = Invoke-Json -Method "GET" -Url "$ApiBase/documents/" -Headers (Get-AuthHeaders $adminToken)
    $list = @(Normalize-Array $resp)
    if (-not ($list | Where-Object { $_.id -eq $documentId })) { throw "document_id not found" }
}

Run-Test "F5 GET /documents/{id}/preview" {
    $out = Join-Path $TmpDir "preview_$documentId.pdf"
    Invoke-DownloadPdfAndValidate -Url "$ApiBase/documents/$documentId/preview" -OutFile $out -Headers (Get-AuthHeaders $doctorToken)
    $global:CreatedArtifacts += $out
}

Run-Test "F5 GET /documents/{id}/download" {
    $out = Join-Path $TmpDir "download_$documentId.pdf"
    Invoke-DownloadPdfAndValidate -Url "$ApiBase/documents/$documentId/download" -OutFile $out -Headers (Get-AuthHeaders $adminToken) -ExpectAttachment
    $global:CreatedArtifacts += $out
}

Run-Test "F5 GET /patients/1/card-pdf" {
    $out = Join-Path $TmpDir "patient_1_card.pdf"
    Invoke-DownloadPdfAndValidate -Url "$ApiBase/patients/1/card-pdf" -OutFile $out -Headers (Get-AuthHeaders $doctorToken)
    $global:CreatedArtifacts += $out
}

# Phase 6 Attachments
Run-Test "F6 GET /attachments/encounters/{id}/attachments" {
    $resp = Invoke-Json -Method "GET" -Url "$ApiBase/attachments/encounters/$encounterId/attachments" -Headers (Get-AuthHeaders $doctorToken)
    $list = @(Normalize-Array $resp)
}

# Phase 7 Negatives
Run-Test "F7 invalid token 401" {
    $headers = Get-AuthHeaders "invalid"
    $res = Invoke-ExpectError -Method "GET" -Url "$ApiBase/templates/" -ExpectedStatus @(401) -Headers $headers
    if ($res.Status -ne 401) { throw "Expected 401" }
}

Run-Test "F7 GET /encounters/99999 404" {
    $res = Invoke-ExpectError -Method "GET" -Url "$ApiBase/encounters/99999" -ExpectedStatus @(404) -Headers (Get-AuthHeaders $doctorToken)
    if ($res.Status -ne 404) { throw "Expected 404" }
}

# Cleanup
if ($Cleanup) {
    Write-Host "Cleanup: START"

    if ($encounterId) {
        try {
            $null = Invoke-Json -Method "DELETE" -Url "$ApiBase/encounters/$encounterId" -Headers (Get-AuthHeaders $doctorToken)
            Write-Host "Cleanup: encounter deleted"
        } catch {
            Write-Host "Cleanup: encounter delete not available"
        }
    }

    if ($templateId) {
        try {
            $null = Invoke-Json -Method "PUT" -Url "$ApiBase/templates/$templateId" -Headers (Get-AuthHeaders $adminToken) -Body @{ is_active = 0; description = "[SMOKE TEST] cleaned" }
            Write-Host "Cleanup: template deactivated"
        } catch {
            Write-Host "Cleanup: template deactivate not available"
        }
    }

    if ($snippetId) {
        try {
            $null = Invoke-Json -Method "PUT" -Url "$ApiBase/snippets/$snippetId" -Headers (Get-AuthHeaders $adminToken) -Body @{ is_active = 0; content = "[SMOKE TEST] cleaned"; category = "EXAMEN"; specialty = "NEUROLOGIA" }
            Write-Host "Cleanup: snippet deactivated"
        } catch {
            Write-Host "Cleanup: snippet deactivate not available"
        }
    }

    Write-Host "Cleanup: END"
}

# Manual SQL fallback if no cleanup endpoints exist:
# UPDATE encounters SET is_active = 0 WHERE subjective LIKE '%[SMOKE TEST]%';
# UPDATE templates SET is_active = 0 WHERE title LIKE '%[SMOKE TEST]%';
# UPDATE snippets SET is_active = 0 WHERE title LIKE '%[SMOKE TEST]%';

Write-Host "Created Artifacts:"
if ($CreatedArtifacts.Count -eq 0) {
    Write-Host "  (none)"
} else {
    foreach ($artifact in $CreatedArtifacts) {
        if (Test-Path $artifact) {
            $size = (Get-Item $artifact).Length
            Write-Host ("  {0} ({1} bytes)" -f $artifact, $size)
        } else {
            Write-Host ("  {0} (missing)" -f $artifact)
        }
    }
}

Write-Host "Summary: Total=$Total Passed=$Passed Failed=$Failed"
Write-Host "Run: powershell -ExecutionPolicy Bypass -File .\\scripts\\smoke_test_a.ps1"
