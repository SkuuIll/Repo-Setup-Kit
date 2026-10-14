# Creates/pushes only as a PRIVATE GitHub repository.
$ErrorActionPreference = 'Stop'
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'Instalá GitHub CLI: https://cli.github.com/' }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Instalá Git: https://git-scm.com/' }
gh auth status | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Primero ejecutá gh auth login' }
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Push-Location $Root
try {
    if (-not (Test-Path .git)) { git init -b main; if ($LASTEXITCODE -ne 0) { throw 'git init falló' } }
    $Remotes = @(git remote)
    if ($Remotes -contains 'origin') { throw 'Ya existe origin. No cambiar el remoto automáticamente.' }
    git add -- README.md repo_setup.py install.sh install.ps1 .gitignore .github tests skills scripts
    if ($LASTEXITCODE -ne 0) { throw 'git add falló' }
    git diff --cached --quiet
    if ($LASTEXITCODE -ne 0) {
        git commit -m 'feat: bootstrap privado para agentes de IA'
        if ($LASTEXITCODE -ne 0) { throw 'git commit falló. Revisá git config user.name/user.email.' }
    }
    git rev-parse --verify HEAD | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'No hay commit para publicar.' }
    gh repo create repo-setup-kit --private --description 'Bootstrap multiplataforma para proyectos de IA y GitHub' --source . --remote origin --push
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear o subir el repositorio privado.' }
    $Visibility = (gh repo view --json visibility --jq '.visibility').Trim()
    if ($LASTEXITCODE -ne 0 -or $Visibility -ne 'PRIVATE') { throw "Visibilidad no confirmada como PRIVATE: $Visibility" }
    Write-Host 'Repositorio privado creado y verificado:'
    gh repo view --json url --jq '.url'
} finally { Pop-Location }
