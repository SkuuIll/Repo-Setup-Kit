# Repo Setup Kit

**Un comando para preparar repositorios GitHub para trabajar con Codex y agentes de IA.**

Compatible con **Windows y Linux**. Sin Docker ni dependencias de Python adicionales. Requiere **Git** y **Python 3.10+**; para GitNexus, también **Node.js con npx**.

## 1. Instalar una sola vez

### Windows — PowerShell

```powershell
git clone https://github.com/SkuuIll/Repo-Setup-Kit.git
cd Repo-Setup-Kit
.\install.ps1
```

### Linux / VPS

```bash
git clone https://github.com/SkuuIll/Repo-Setup-Kit.git
cd Repo-Setup-Kit
sh install.sh
```

Volvé a abrir la terminal si todavía no reconoce `repo-setup`. En Windows, si PowerShell bloquea el script, ejecutá `powershell -ExecutionPolicy Bypass -File .\install.ps1` desde la carpeta del kit.

## 2. Preparar cualquier proyecto nuevo

Entrá en el repositorio Git que quieras preparar y ejecutá:

```bash
repo-setup . --full
```

Comandos adicionales:

```bash
repo-setup . --full --dry-run  # Previsualizar sin modificar nada
repo-setup . --doctor          # Revisar herramientas y entorno
rtk gain                       # Ver ahorro estimado de salidas de comandos
```

También podés indicar una ruta: `repo-setup /ruta/al/proyecto --full`.

## Qué configura automáticamente

| Herramienta | Qué aporta |
|---|---|
| [RTK](https://github.com/rtk-ai/rtk) | Comprime salidas de terminal; si Codex está instalado, intenta configurar su hook global. |
| [GitNexus](https://github.com/abhigyanpatwari/GitNexus) | Indexa relaciones entre funciones, dependencias y módulos; genera skills. Usa el CLI existente o `npx` (sin instalación global obligatoria). |
| [Engram](https://github.com/Gentleman-Programming/engram) | Memoria persistente SQLite; integra MCP con Codex si está instalado. |
| GitHub MCP | Opcional: se configura si existe `GITHUB_PAT_TOKEN` y Codex está instalado. No almacena el token. |
| AGENTS.md + skill | Contexto inicial breve y pautas para no cargar todo el proyecto innecesariamente. |
| Git hooks, CI y Dependabot | Verificaciones básicas para commits y pull requests; respeta configuraciones existentes. |

El comando genera `AGENTS.md`, `.agent-bootstrap/project-map.md`, `.agents/skills/repo-onboarding/SKILL.md`, plantilla de PR y, cuando corresponda, hooks, workflows de CI y Dependabot. El estado local se excluye de Git.

**No hace push, merge ni despliegues del proyecto destino.** Si un componente no puede configurarse, lo informa y el comando termina con aviso de preparación parcial.

## Seguridad y ahorro de tokens

- `--full` puede descargar binarios oficiales y ejecutar un paquete npm mediante `npx`; inspeccioná repositorios no confiables antes de ejecutar scripts de terceros.
- Los hooks y la CI inicial son controles básicos, no una auditoría de seguridad completa.
- RTK mide estimaciones de tokens en las salidas que procesa; **no garantiza un porcentaje de ahorro del consumo total de Codex**.
- Podés repetir el comando: preserva instrucciones, hooks y workflows existentes cuando corresponde.
- Las integraciones de Codex no se activan automáticamente dentro de ChatGPT.com y deben instalarse en cada máquina donde quieras utilizarlas.

## Pruebas del propio kit

```bash
python -m unittest discover -s tests -v
python -m py_compile repo_setup.py
```

Los tests se ejecutan mediante GitHub Actions en Ubuntu y Windows: [ver ejecuciones](https://github.com/SkuuIll/Repo-Setup-Kit/actions).

## Actualizar

Desde la carpeta del kit: `git pull` y luego volvé a ejecutar `install.ps1` (Windows) o `sh install.sh` (Linux).

Los scripts `scripts/publish-private.*` son auxiliares para crear una copia privada separada; **no los ejecutes para actualizar este repositorio público**.
