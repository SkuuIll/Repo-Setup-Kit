$ErrorActionPreference = 'Stop'
$Source = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Get-Command py -ErrorAction SilentlyContinue
if (-not $Python) { $Python = Get-Command python -ErrorAction SilentlyContinue }
if (-not $Python) { throw 'Instalá Python 3.10+ y repetí.' }
$VersionArgs = if ($Python.Name -eq 'py.exe') { @('-3') } else { @() }
& $Python.Source @VersionArgs -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)'
if ($LASTEXITCODE -ne 0) { throw 'Se requiere Python 3.10+' }
$Destination = Join-Path $env:LOCALAPPDATA 'repo-setup'
$Bin = Join-Path $Destination 'bin'
New-Item -ItemType Directory -Force $Bin, (Join-Path $Destination 'skills/repo-onboarding') | Out-Null
Copy-Item (Join-Path $Source 'repo_setup.py') (Join-Path $Destination 'repo_setup.py') -Force
Copy-Item (Join-Path $Source 'skills/repo-onboarding/SKILL.md') (Join-Path $Destination 'skills/repo-onboarding/SKILL.md') -Force
$Launcher = Join-Path $Bin 'repo-setup.cmd'
$Prefix = if ($Python.Name -eq 'py.exe') { 'py -3' } else { 'python' }
@"
@echo off
$Prefix "$Destination\repo_setup.py" %*
"@ | Set-Content -Encoding ascii $Launcher
$PathUser = [Environment]::GetEnvironmentVariable('Path','User')
if (($PathUser -split ';') -notcontains $Bin) {
    [Environment]::SetEnvironmentVariable('Path', ($PathUser.TrimEnd(';')+';'+$Bin).TrimStart(';'),'User')
}
if (($env:Path -split ';') -notcontains $Bin) { $env:Path += ";$Bin" }
Write-Host "Instalado: $Launcher"
Write-Host 'Abrí una terminal nueva. Uso: repo-setup C:\ruta\repo --full'
