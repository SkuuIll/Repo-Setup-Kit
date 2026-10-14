#!/usr/bin/env sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON=$(command -v python3 || command -v python || true)
if [ -z "$PYTHON" ]; then echo 'ERROR: Instalar Python 3.10+ primero.' >&2; exit 1; fi
"$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' || { echo 'ERROR: Se requiere Python 3.10+' >&2; exit 1; }
DEST="$HOME/.local/share/repo-setup-kit"
BIN="$HOME/.local/bin"
mkdir -p "$DEST/skills/repo-onboarding" "$BIN"
cp "$HERE/repo_setup.py" "$DEST/repo_setup.py"
cp "$HERE/skills/repo-onboarding/SKILL.md" "$DEST/skills/repo-onboarding/SKILL.md"
cat > "$BIN/repo-setup" <<EOF
#!/usr/bin/env sh
exec "$PYTHON" "\$HOME/.local/share/repo-setup-kit/repo_setup.py" "\$@"
EOF
chmod +x "$BIN/repo-setup"
echo "Instalado: $BIN/repo-setup"
case ":$PATH:" in
  *":$BIN:"*) : ;;
  *)
    if ! grep -F 'export PATH="$HOME/.local/bin:$PATH" # repo-setup-kit' "$HOME/.profile" >/dev/null 2>&1; then
      printf '\nexport PATH="$HOME/.local/bin:$PATH" # repo-setup-kit\n' >> "$HOME/.profile"
    fi
    echo "PATH configurado en ~/.profile (aplicable al abrir sesión nueva)"
    ;;
esac
echo 'Uso: repo-setup /ruta/mi-proyecto --full'
