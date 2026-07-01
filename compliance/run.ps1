<#
.SYNOPSIS
    Aeglero compliance engine - PowerShell entrypoint (Windows CI & scheduled tasks).

.DESCRIPTION
    Runs the Python engine, then reads the resulting SPRS score and fails
    (non-zero exit) if it drops below a threshold. This is the "compliance gate"
    for Windows-hosted scheduled runs, mirroring run.sh.

.EXAMPLE
    ./compliance/run.ps1
    $env:COMPLIANCE_MIN_SPRS = 100; ./compliance/run.ps1
#>
[CmdletBinding()]
param(
    [int] $MinSprs = $(if ($env:COMPLIANCE_MIN_SPRS) { [int]$env:COMPLIANCE_MIN_SPRS } else { 90 })
)

$ErrorActionPreference = 'Stop'
$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$StatusJson = Join-Path $ScriptDir 'output/status.json'

# Pick an available Python (Windows PowerShell 5.1 compatible - no ?? operator).
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $py) { Write-Error 'python not found on PATH'; exit 2 }

Write-Host '>> Running Aeglero compliance engine...'
& $py.Source (Join-Path $ScriptDir 'run.py')

if (-not (Test-Path $StatusJson)) { Write-Error "$StatusJson was not produced"; exit 2 }

$report = Get-Content $StatusJson -Raw | ConvertFrom-Json
$score  = [int] $report.summary.sprs_score

Write-Host ">> SPRS score: $score (gate: >= $MinSprs)"
if ($score -lt $MinSprs) {
    Write-Error "FAIL: SPRS $score is below the required minimum $MinSprs."
    exit 1
}
Write-Host 'PASS: compliance posture meets the gate.'
