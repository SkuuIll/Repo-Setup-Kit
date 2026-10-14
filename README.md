# Repo Setup Kit

**Un comando para preparar cada repositorio nuevo de GitHub para trabajar con IA.** Compatible con **Windows y Linux**, sin Docker obligatorio, sin claves dentro del repositorio y sin reescribir tu aplicación.

> Versión 0.2 (14/10/2026). Código y pruebas incluidos. Las integraciones externas se instalan en *tu* equipo cuando ejecutás el comando `--full`; no se activan dentro de ChatGPT.com automáticamente.

## 1. Instalación inicial (solo una vez)

Descargá y descomprimí este kit. Abrí una terminal **en la carpeta del kit**.

**Windows — PowerShell:**

```powershell
.\install.ps1
```

Si Windows bloquea scripts, podés utilizar `powershell -ExecutionPolicy Bypass -File .\install.ps1` para esa ejecución.

**Linux — terminal:**

```bash
sh ./install.sh
```

Necesitás **Python 3.10 o superior y Git**. Para GitNexus, necesitás Node.js/npm. Cerrá y volvé a abrir la terminal si todavía no reconoce `repo-setup`.

## 2. Preparar un proyecto (un comando)

Cloná o descargá un repositorio, entrá a su carpeta Git y ejecutá:

```bash
repo-setup . --full
```

O pasá una ruta, sin entrar a la carpeta:

**Windows:**

```powershell
repo-setup "C:\Proyectos\mi-app" --full
```

**Linux:**

```bash
repo-setup "$HOME/proyectos/mi-app" --full
```

`--full` equivale a `--install-tools --hooks --ci`: **instala las herramientas globales que faltan, analiza el código, genera instrucciones/skills, incorpora hooks de Git y crea CI inicial cuando aún no existe**. Si el proyecto ya tiene Husky o una CI propia, se conserva. Se puede repetir el comando después de hacer un `git pull`.

**Revisar antes de tocar nada:** `repo-setup . --full --dry-run`  
**Diagnóstico de herramientas:** `repo-setup . --doctor`  
**Ahorro reportado por RTK:** `rtk gain`

## 3. Publicar este kit en tu GitHub **privado**

Este ZIP no crea un repositorio por sí mismo. Para hacerlo desde tu computadora, necesitás [GitHub CLI (`gh`)](https://cli.github.com/) y haber iniciado sesión una sola vez:

```bash
gh auth login
```

Después ejecutá **una sola instrucción desde la carpeta del kit**:

**Windows:**

```powershell
.\scripts\publish-private.ps1
```

**Linux:**

```bash
sh ./scripts/publish-private.sh
```

El script crea `repo-setup-kit` **privado**, sube los archivos de este kit, lee la visibilidad en GitHub y muestra su URL. Si detecta un `origin` existente, no modifica ese remoto. Requiere identidad Git (`git config user.name` y `user.email`) para crear el primer commit. La privacidad se fija usando el flag oficial `gh repo create --private`.

### Cuando el repositorio privado ya exista

Para instalar en otra computadora que tenga acceso a tu GitHub privado:

```bash
gh repo clone repo-setup-kit
cd repo-setup-kit
```

Luego ejecutá `install.ps1` en Windows o `sh install.sh` en Linux, como en el paso 1.

## Qué prepara cada vez

| Capa | Qué hace |
|---|---|
| **RTK** | Reduce texto redundante en salidas compatibles de terminal; configura hook de Codex cuando está instalado; `rtk gain` muestra estadísticas de comandos. |
| **GitNexus** | Indexa relaciones del repositorio (`gitnexus analyze --skills`); instala skills y configura su MCP para Codex si está disponible. |
| **Engram** | Memoria persistente de decisiones técnicas basada en SQLite; configura memoria MCP de Codex si está disponible. |
| **MCP de GitHub** | Registra servidor remoto oficial **solo** si detecta `GITHUB_PAT_TOKEN` en el entorno; no copia ni guarda el token. |
| **AGENTS.md + skill** | Guía breve para que el agente use el grafo y la memoria y no cargue todo el código a la vez. |
| **Git hooks** | Comprueba whitespace y posibles archivos sensibles antes de commitear. Respeta Husky, pre-commit y hooks existentes. |
| **Pull requests / CI / Dependabot** | Agrega plantilla, CI inicial cuando falta y actualizaciones semanales limitadas; no modifica otras pipelines. |

**No instala herramientas redundantes por defecto.** Se evita instalar Context Mode u otro compresor MCP junto a RTK hasta medir si aporta una mejora en tu entorno.

## Archivos que genera en el proyecto destino

- `AGENTS.md`: incorpora una sección propia sin borrar instrucciones anteriores.
- `.agent-bootstrap/project-map.md`: índice de rutas y tecnologías detectadas.
- `.agent-bootstrap/state.json`: estado local, excluido de Git.
- `.agents/skills/repo-onboarding/SKILL.md`: instrucciones para el agente.
- `.github/PULL_REQUEST_TEMPLATE.md`: guía para revisar un PR, si no existe.
- `.githooks/pre-commit` y `git config core.hooksPath`: solo cuando se solicita y no existen hooks propios.
- `.github/workflows/agent-quality.yml`: solo cuando el proyecto todavía no posee workflows.
- `.github/dependabot.yml`: plan semanal de actualizaciones, solo si no existe uno.

> **El mapa no sustituye la revisión del código real:** registra rutas detectadas, no analiza todos los secretos, ni reemplaza controles de seguridad especializados. Los índices grandes de GitNexus se mantienen fuera del control de versiones.

## Seguridad y límites

- El comando `--full` descarga binarios de GitHub Releases y puede ejecutar instalación de npm de terceros. Revisá primero los repositorios desconocidos y las dependencias que ya tienen.
- Intenta verificar los hashes SHA-256 publicados por GitHub; si una release no publica un digest, informa de la ausencia de esa verificación.
- No hace push ni merge en los proyectos que preparás. **La única excepción es `scripts/publish-private`, cuyo propósito explícito es crear y subir este kit.**
- No se garantiza un porcentaje fijo de tokens. `rtk gain` refleja salidas optimizadas de comandos, **no** el gasto total de la IA. Para evaluar rendimiento real, compará tareas equivalentes con las mismas condiciones.
- Si una descarga o integración falla, verificá el mensaje y el resultado de `repo-setup . --doctor`. Algunos componentes requieren reiniciar Codex o la terminal.
- La configuración automática del MCP remoto de GitHub con Codex requiere un PAT en `GITHUB_PAT_TOKEN` con permisos mínimos. No guardes ese secreto en archivos del repositorio.

## Pruebas del kit

```bash
python -m unittest discover -s tests -v
```

Más información de las herramientas: [RTK](https://github.com/rtk-ai/rtk) · [GitNexus](https://github.com/abhigyanpatwari/GitNexus) · [Engram](https://github.com/Gentleman-Programming/engram) · [GitHub MCP](https://github.com/github/github-mcp-server).
