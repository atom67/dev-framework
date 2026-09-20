<#
.SYNOPSIS
    Windows entry point for the portable Python installer (Python 3.10+).
.EXAMPLE
    .\install.ps1 -Target D:\DEV\NewProject -ProjectName 'New Project' -DryRun
.EXAMPLE
    .\install.ps1 -Target D:\DEV\NewProject -Update -DryRun
.EXAMPLE
    .\install.ps1 -SelfTest
#>
[CmdletBinding()]
param(
    [string]$Target,
    [string]$ProjectName,
    [string]$ScaleTarget,
    [ValidateSet('generic', 'personal-desktop', 'service')][string]$Profile,
    [switch]$Force,
    [switch]$Update,
    [Alias('WhatIf')][switch]$DryRun,
    [switch]$Recover,
    [switch]$SelfTest,
    [switch]$Devlog,
    [switch]$NoDevlog,
    [string]$PythonCommand = 'python'
)

$ErrorActionPreference = 'Stop'
if ($SelfTest) {
    & $PythonCommand -B (Join-Path $PSScriptRoot 'scripts/verify.py')
    exit $LASTEXITCODE
}
if (-not $Target) { throw '-Target is required (or use -SelfTest)' }
$installArgs = @('-B', (Join-Path $PSScriptRoot 'scripts/install.py'), '--target', $Target)
if ($ProjectName) { $installArgs += @('--name', $ProjectName) }
if ($ScaleTarget) { $installArgs += @('--scale', $ScaleTarget) }
if ($Profile) { $installArgs += @('--profile', $Profile) }
if ($Force) { $installArgs += '--force' }
if ($Update) { $installArgs += '--update' }
if ($DryRun) { $installArgs += '--dry-run' }
if ($Recover) { $installArgs += '--recover' }
if ($Devlog) { $installArgs += '--devlog' }
if ($NoDevlog) { $installArgs += '--no-devlog' }
& $PythonCommand @installArgs
exit $LASTEXITCODE
