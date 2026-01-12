<#
.SYNOPSIS
    Runner de tests para validaciÃ³n de WeasyPrint y generaciÃ³n de PDFs.

.DESCRIPTION
    Ejecuta en secuencia todos los scripts de prueba de PDF:
    - verify_venv.py: Verifica venv y DLL setup
    - print_versions.py: DiagnÃ³stico de versiones de paquetes
    - test_dll_loading.py: Test de carga de DLLs con ctypes
    - test_weasyprint_minimal.py: Test bÃ¡sico de WeasyPrint
    - test_patient_card_pdf.py: Test completo de ficha de paciente

.PARAMETER Python
    Ruta al ejecutable de Python del venv.
    Default: .\venv\Scripts\python.exe (relativo a raÃ­z del repo)

.EXAMPLE
    .\scripts\run_pdf_tests.ps1

.EXAMPLE
    .\scripts\run_pdf_tests.ps1 -Python "D:\galenos\venv\Scripts\python.exe"
#>

param(
    [string]$Python = ".\venv\Scripts\python.exe"
)

$ErrorActionPreference = "Stop"

# Cambiar a la raÃ­z del repo (parent de scripts/)
$scriptRoot = Split-Path -Parent $PSScriptRoot
Set-Location $scriptRoot

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "PDF TESTS RUNNER" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "Python executable: $Python" -ForegroundColor Gray
Write-Host "Working directory: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

# Lista de scripts a ejecutar en orden
$tests = @(
    @{Name="verify_venv.py"; Description="Verifying venv and imports"},
    @{Name="print_versions.py"; Description="Checking package versions"},
    @{Name="test_dll_loading.py"; Description="Testing DLL loading (ctypes)"},
    @{Name="test_weasyprint_minimal.py"; Description="Testing WeasyPrint minimal PDF"},
    @{Name="test_patient_card_pdf.py"; Description="Testing patient card PDF generation"}
)

$testNumber = 1
$totalTests = $tests.Count

foreach ($test in $tests) {
    $scriptPath = ".\scripts\$($test.Name)"

    Write-Host "-" * 70 -ForegroundColor Yellow
    Write-Host "TEST $testNumber/$totalTests : $($test.Description)" -ForegroundColor Yellow
    Write-Host "Running: $scriptPath" -ForegroundColor Gray
    Write-Host "-" * 70 -ForegroundColor Yellow
    Write-Host ""

    # Ejecutar el script Python
    $py = (Resolve-Path $Python).Path
    $sp = (Resolve-Path $scriptPath).Path
    $output = cmd /c "`"$py`" `"$sp`" 2>&1"
    $exitCode = $LASTEXITCODE

    $output | ForEach-Object {
        $line = $_.ToString()
        if ($line -notmatch 'GLib-(GObject-)?CRITICAL') {
            Write-Host $line
        }
    }

    # Verificar exit code
    if ($exitCode -ne 0) {
        Write-Host ""
        Write-Host "? FAILED: $($test.Name) exited with code $exitCode" -ForegroundColor Red
        exit $exitCode
    }

    Write-Host ""
    $testNumber++
}

# Todos los tests pasaron
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "run_pdf_tests: SUCCESS" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
Write-Host ""
Write-Host "✓ All $totalTests tests passed successfully" -ForegroundColor Green
