#!/usr/bin/env sh
# Creates and pushes this folder only as a *private* repository.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
command -v gh >/dev/null 2>&1 || { echo 'Falta GitHub CLI: https://cli.github.com/' >&2; exit 1; }
command -v git >/dev/null 2>&1 || { echo 'Falta Git: https://git-scm.com/' >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo 'Iniciá sesión con: gh auth login' >&2; exit 1; }
cd "$HERE"
if [ ! -d .git ]; then git init -b main; fi
if git remote | grep -Fx origin >/dev/null 2>&1; then
  echo 'Ya hay un remoto origin. No se creará otro repositorio por seguridad.' >&2
  exit 1
fi
# Stage only source controlled by this kit, never arbitrary untracked files.
git add -- README.md repo_setup.py install.sh install.ps1 .gitignore .github tests skills scripts
if ! git diff --cached --quiet; then
  git commit -m 'feat: bootstrap privado para agentes de IA'
fi
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
  echo 'No existe un commit que se pueda publicar.' >&2
  exit 1
fi
# `--private` explicitly sets repo visibility. Do not remove this flag.
gh repo create repo-setup-kit --private --description 'Bootstrap multiplataforma para proyectos de IA y GitHub' --source . --remote origin --push
VISIBILITY=$(gh repo view --json visibility --jq '.visibility')
if [ "$VISIBILITY" != PRIVATE ]; then
  echo "ALERTA: visibilidad inesperada: $VISIBILITY. Revisá el repositorio inmediatamente." >&2
  exit 2
fi
echo 'Repositorio privado creado y verificado:'
gh repo view --json url --jq '.url'
