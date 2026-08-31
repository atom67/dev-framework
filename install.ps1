<#
.SYNOPSIS
    Lay the DEV Framework template into a target repository.

.DESCRIPTION
    Copies everything under template/ into -Target, substituting {{PROJECT_NAME}} and
    {{SCALE_TARGET}}. Existing files are never overwritten without -Force: clobbering a
    project's own CLAUDE.md is data loss, and this script is usually run against a repo
    that already has content.

.EXAMPLE
    .\install.ps1 -Target D:\DEV\NewProject -ProjectName "New Project"

.EXAMPLE
    .\install.ps1 -SelfTest
#>
[CmdletBinding()]
param(
    [string]$Target,
    [string]$ProjectName,
    [string]$ScaleTarget = '10,000 users',
    [switch]$Force,
    [switch]$SelfTest
)

$ErrorActionPreference = 'Stop'
$TemplateRoot = Join-Path $PSScriptRoot 'template'

function Install-Template {
    param($Source, $Dest, $Name, $Scale, $Overwrite)

    if (-not (Test-Path $Source)) { throw "Template directory not found: $Source" }
    if (-not (Test-Path $Dest)) { New-Item -ItemType Directory -Path $Dest -Force | Out-Null }

    $written = @()
    $skipped = @()

    foreach ($file in Get-ChildItem -Path $Source -Recurse -File) {
        $relative = $file.FullName.Substring($Source.Length).TrimStart('\', '/')
        $destPath = Join-Path $Dest $relative

        if ((Test-Path $destPath) -and -not $Overwrite) {
            $skipped += $relative
            continue
        }

        $destDir = Split-Path $destPath -Parent
        if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }

        $content = [System.IO.File]::ReadAllText($file.FullName)
        $content = $content.Replace('{{PROJECT_NAME}}', $Name).Replace('{{SCALE_TARGET}}', $Scale)
        # UTF8Encoding($false): no BOM. A BOM in a markdown file shows up as a stray
        # character in every tool that reads it as plain text.
        [System.IO.File]::WriteAllText($destPath, $content, (New-Object System.Text.UTF8Encoding($false)))
        $written += $relative
    }

    return @{ Written = $written; Skipped = $skipped }
}

function Invoke-SelfTest {
    # One runnable check: the smallest thing that fails if the substitution or the
    # do-not-clobber logic breaks. Both have a real cost when wrong - a leftover
    # {{PROJECT_NAME}} ships as a placeholder, and a clobbered file is lost work.
    $tmp = Join-Path $PSScriptRoot ('temp\selftest-' + [Guid]::NewGuid().ToString('N').Substring(0, 8))
    $failures = @()
    try {
        $r1 = Install-Template $TemplateRoot $tmp 'Demo Project' '5,000 devices' $false

        $agents = Join-Path $tmp 'AGENTS.md'
        if (-not (Test-Path $agents)) { $failures += 'AGENTS.md was not written' }
        else {
            $text = [System.IO.File]::ReadAllText($agents)
            if ($text -notmatch 'Demo Project')  { $failures += 'project name was not substituted' }
            if ($text -notmatch '5,000 devices') { $failures += 'scale target was not substituted' }
            if ($text -match '\{\{')             { $failures += 'an unsubstituted placeholder remains' }
        }
        if (-not (Test-Path (Join-Path $tmp 'docs\REQUIREMENTS.md'))) { $failures += 'docs/ was not copied' }
        if ($r1.Written.Count -lt 8) { $failures += ("expected at least 8 files, got " + $r1.Written.Count) }

        # Second pass over an existing file must preserve it, not overwrite it.
        $claude = Join-Path $tmp 'CLAUDE.md'
        [System.IO.File]::WriteAllText($claude, 'SENTINEL')
        $r2 = Install-Template $TemplateRoot $tmp 'Demo Project' '5,000 devices' $false
        if ([System.IO.File]::ReadAllText($claude) -ne 'SENTINEL') { $failures += 'an existing file was overwritten without -Force' }
        if ($r2.Skipped -notcontains 'CLAUDE.md') { $failures += 'the existing file was not reported as skipped' }
    }
    finally {
        if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
    }

    if ($failures.Count -gt 0) {
        Write-Host "SELF-TEST FAILED" -ForegroundColor Red
        $failures | ForEach-Object { Write-Host ("  - " + $_) -ForegroundColor Red }
        return 1
    }
    Write-Host "SELF-TEST PASSED" -ForegroundColor Green
    return 0
}

if ($SelfTest) { exit (Invoke-SelfTest) }

if (-not $Target)      { throw "-Target is required (or use -SelfTest)" }
if (-not $ProjectName) { throw "-ProjectName is required" }

# Resolve-Path fails on a path that does not exist yet, so create first, resolve second.
# An absolute destination matters: the relative path of each copied file is computed by
# trimming the template root off the source path, and a mixed relative/absolute pair
# silently produces wrong names.
if (-not (Test-Path $Target)) { New-Item -ItemType Directory -Path $Target -Force | Out-Null }
$TargetFull = (Resolve-Path $Target).Path

$result = Install-Template $TemplateRoot $TargetFull $ProjectName $ScaleTarget $Force.IsPresent

Write-Host ""
Write-Host ("Installed into " + $Target)
Write-Host ("  written: " + $result.Written.Count)
$result.Written | ForEach-Object { Write-Host ("    + " + $_) }
if ($result.Skipped.Count -gt 0) {
    Write-Host ("  kept (already present, use -Force to replace): " + $result.Skipped.Count)
    $result.Skipped | ForEach-Object { Write-Host ("    = " + $_) }
}

Write-Host ""
Write-Host "Next:"
Write-Host "  1. Fill in CLAUDE.md - stack, structure, data locations, build commands."
Write-Host "  2. Set the current schema version in docs/ARCHITECTURE.md."
Write-Host "  3. Confirm the scale target in AGENTS.md section 5 is the one you mean."
Write-Host "  4. Read LESSONS.md in the framework repo once. It is why the rules say what they say."
