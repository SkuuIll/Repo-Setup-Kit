#!/usr/bin/env python3
"""Repo Setup Kit: zero-dependency, cross-platform bootstrap for AI-assisted development.

Deliberately does not push, deploy, touch secrets or modify existing workflows.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
START = '<!-- repo-setup:begin -->'
END = '<!-- repo-setup:end -->'
OMIT = {'.git','node_modules','.venv','venv','dist','build','.next','.gitnexus','vendor','target','.cache','coverage','__pycache__'}
PROVIDERS = {
    'rtk': ('rtk-ai','rtk'),
    'engram': ('Gentleman-Programming','engram'),
}


def command(name):
    p = shutil.which(name)
    if not p and os.name == 'nt':
        p = shutil.which(name + '.cmd')
    if not p:
        for b in (Path.home()/'.local/bin', Path(os.environ.get('LOCALAPPDATA',str(Path.home()))) / 'repo-setup' / 'bin'):
            probe = b / (name + ('.exe' if os.name == 'nt' else ''))
            if probe.exists():
                return str(probe)
    return p


def run(args, cwd=None, timeout=180):
    print('+', ' '.join(map(str,args)))
    try:
        p = subprocess.run([str(x) for x in args], cwd=str(cwd) if cwd else None, timeout=timeout,
                           text=True, encoding='utf-8', errors='replace', capture_output=True, check=False)
        if p.returncode:
            print('  ERROR:', p.stderr.strip()[:500] or p.stdout.strip()[:500])
        elif p.stdout.strip():
            print(' ', p.stdout.strip()[:400])
        return p.returncode == 0
    except (OSError, subprocess.TimeoutExpired) as exc:
        print('  ERROR:', exc)
        return False


def git_files(project):
    try:
        out = subprocess.run(['git','-C',str(project),'ls-files','--cached','--others','--exclude-standard','-z'],
                             capture_output=True, check=True, timeout=30).stdout
        return sorted({Path(x.decode('utf-8',errors='replace')).as_posix() for x in out.split(b'\0') if x})
    except (OSError, subprocess.SubprocessError):
        return []


def project_type(project, files):
    filenames = set(files)
    return {
        'javascript': 'package.json' in filenames,
        'python': any(x in filenames for x in ('pyproject.toml','requirements.txt','Pipfile','setup.py')),
        'rust': 'Cargo.toml' in filenames,
        'go': 'go.mod' in filenames,
        'dotnet': any(x.endswith(('.sln','.csproj','.fsproj')) for x in filenames),
        'docker': any(Path(x).name in ('Dockerfile','compose.yaml','docker-compose.yml') for x in filenames),
    }


def safe_paths(files, max_count=90):
    result = []
    for f in files:
        bits = Path(f).parts
        if any(p in OMIT for p in bits):
            continue
        if f.startswith(('.env','.npmrc','.pypirc')) or 'secret' in f.lower() or 'credential' in f.lower():
            continue
        if f.endswith(('.lock','.map','.svg','.png','.jpg','.jpeg','.pdf','.zip','.db','.sqlite')):
            continue
        result.append(f)
    return result[:max_count]


def atomic_write(path, text, dry_run=False):
    if path.exists() and path.read_text(encoding='utf-8') == text:
        return 'unchanged'
    if dry_run:
        print('  WOULD WRITE', path)
        return 'planned'
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='\n',dir=path.parent,delete=False) as tmp:
        tmp.write(text)
        temporary = Path(tmp.name)
    temporary.replace(path)
    return 'written'


def write_if_missing(path, text, dry_run):
    return 'preserved' if path.exists() else atomic_write(path,text,dry_run)


def build_map(project, files, detected):
    scripts = {}
    if detected['javascript']:
        try:
            p = json.loads((project/'package.json').read_text(encoding='utf-8'))
            scripts = {k: '<comando omitido por seguridad>' for k,v in p.get('scripts',{}).items() if isinstance(v,str)}
        except (OSError,ValueError,TypeError):
            pass
    leaders = [x for x in ('README.md','README.MD','AGENTS.md','package.json','pyproject.toml','go.mod','Cargo.toml','docker-compose.yml','compose.yaml') if x in files]
    lines = [
        '# Mapa breve del proyecto (generado)',
        '',
        'Usar como índice inicial, NO como sustituto de comprobar el código vigente.',
        'No contiene el contenido de archivos ni credenciales.',
        '',
        '**Stacks detectados:** ' + (', '.join(k for k,v in detected.items() if v) or 'sin identificar'),
        '',
        '**Archivos de entrada:** ' + (', '.join(leaders) or 'por identificar'),
        '',
        '## Scripts declarados',
    ]
    if scripts:
        lines.extend(f'- `{k}`: `{v}`' for k,v in sorted(scripts.items()))
    else:
        lines.append('- No se detectaron scripts npm en la raíz.')
    lines.extend(['','## Rutas visibles (máximo 90; sin binarios ni archivos sensibles)',''])
    lines.extend('- `'+x+'`' for x in safe_paths(files))
    lines.extend(['','## Próximo paso para el agente','','Usar GitNexus/MCP para dependencias y Engram para recuperar decisiones antes de leer grandes bloques de código.',''])
    return '\n'.join(lines)


def instructions():
    return '''## Entorno de desarrollo asistido por IA (repo-setup)

- Al iniciar, leer `.agent-bootstrap/project-map.md` (índice corto, puede estar desactualizado).
- Preferir GitNexus para localizar símbolos, dependencias e impacto antes de leer módulos completos.
- Consultar Engram para decisiones previas relevantes y guardar solo hechos técnicos duraderos; nunca guardar secretos.
- Usar RTK para salidas largas de terminal **solo cuando esté disponible y conserve la información necesaria**; ampliar la salida sin filtrar si falla algo.
- Búsquedas por símbolo/ruta y lectura focalizada; nunca cargar todo el repositorio como contexto inicial.
- Antes de editar, revisar `git status`; conservar cambios existentes y convenciones; no ejecutar scripts de repos externos sin inspección.
- Antes de proponer PR: ejecutar tests/lint del stack, `git diff --check`, analizar impacto y resumir cambios y riesgos.
- No hacer push, merge, despliegue ni alterar políticas remotas sin orden explícita.
- Las cifras de ahorro requieren métricas del cliente/RTK; no inventar ahorros ni degradar la calidad para ahorrar tokens.
'''


def sync_agents(path, dry_run):
    content = path.read_text(encoding='utf-8') if path.exists() else ''
    block = START+'\n'+instructions()+END+'\n'
    if START in content and END in content:
        modified = content[:content.index(START)] + block + content[content.index(END)+len(END):].lstrip('\n')
    elif content:
        modified = content.rstrip()+'\n\n'+block
    else:
        modified = '# Instrucciones para agentes\n\n'+block
    return atomic_write(path,modified,dry_run)


def ignore_generated(project, dry_run):
    path = project/'.gitignore'
    old = path.read_text(encoding='utf-8') if path.exists() else ''
    additions = ['.gitnexus/','.agent-bootstrap/state.json','.agent-bootstrap/*.log']
    pending = [i for i in additions if i not in old.splitlines()]
    if not pending:
        return 'unchanged'
    return atomic_write(path,old.rstrip()+('\n\n' if old.strip() else '')+'# repo-setup: índices y estado local\n'+'\n'.join(pending)+'\n',dry_run)


def install_github_binary(tool, dry_run):
    owner,repo = PROVIDERS[tool]
    system = platform.system().lower()
    arch0 = platform.machine().lower()
    arch = 'arm64' if arch0 in ('arm64','aarch64') else 'amd64' if arch0 in ('x86_64','amd64','x64') else None
    if system not in ('windows','linux') or not arch:
        print('  No hay binario preconfigurado para',system,arch0)
        return False
    if dry_run:
        print(f'  WOULD DOWNLOAD {owner}/{repo} latest stable release for {system}/{arch}')
        return True
    request = urllib.request.Request(f'https://api.github.com/repos/{owner}/{repo}/releases/latest',headers={'Accept':'application/vnd.github+json','User-Agent':'repo-setup-kit/1.0'})
    try:
        with urllib.request.urlopen(request,timeout=20) as response:
            release = json.load(response)
        assets = release.get('assets',[])
        if tool == 'engram':
            prefix = f'engram_{release["tag_name"].lstrip("v")}_{system}_{arch}'
            matches = [a for a in assets if a['name'].startswith(prefix) and a['name'].endswith(('.zip','.tar.gz'))]
        else:
            cpu = {'amd64':'x86_64','arm64':'aarch64'}[arch]
            suffix = ('pc-windows-msvc' if system=='windows' else 'unknown-linux-musl' if arch=='amd64' else 'unknown-linux-gnu')
            matches = [a for a in assets if a['name'].startswith('rtk-') and f'{cpu}-{suffix}' in a['name'] and a['name'].endswith(('.zip','.tar.gz'))]
        if len(matches)!=1:
            print(f'  No se encontró un artefacto único para {tool} {system}/{arch}; revisar releases oficiales.')
            return False
        asset = matches[0]
        u = urllib.request.Request(asset['browser_download_url'],headers={'User-Agent':'repo-setup-kit/1.0'})
        with urllib.request.urlopen(u,timeout=70) as response:
            payload=response.read(80*1024*1024+1)
        if len(payload)>80*1024*1024: raise ValueError('Artifact too large')
        checksum = asset.get('digest')
        if checksum and checksum.startswith('sha256:'):
            if hashlib.sha256(payload).hexdigest()!=checksum.partition(':')[2]:
                raise ValueError('Checksum SHA256 inválido')
        else:
            print('  Aviso: release sin digest SHA256 verificable por API; transporte TLS y repositorio oficial.')
        suffix = '.exe' if system=='windows' else ''
        expected = tool + suffix
        if asset['name'].endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(payload)) as f:
                members=[m for m in f.infolist() if Path(m.filename).name == expected and not m.is_dir()]
                if len(members)!=1: raise ValueError('Executable not found uniquely in zip')
                exe=f.read(members[0])
        else:
            with tarfile.open(fileobj=io.BytesIO(payload),mode='r:gz') as f:
                members=[m for m in f.getmembers() if Path(m.name).name == expected and m.isfile()]
                if len(members)!=1: raise ValueError('Executable not found uniquely in tar')
                stream=f.extractfile(members[0]); assert stream
                exe=stream.read()
        target = (Path(os.environ.get('LOCALAPPDATA',str(Path.home()))) / 'repo-setup' / 'bin' if system=='windows' else Path.home()/'.local/bin') / expected
        target.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='wb',dir=target.parent,delete=False) as tmp:
            tmp.write(exe); stage=Path(tmp.name)
        if system!='windows': stage.chmod(0o755)
        stage.replace(target)
        print('  Instalado:',target)
        return True
    except (OSError,ValueError,KeyError,urllib.error.URLError,zipfile.BadZipFile,tarfile.TarError) as exc:
        print(f'  Falló instalación de {tool}: {exc}')
        return False


def configure_tools(project, detected, dry_run, install_tools, no_context_mode):
    results={}
    def state(found):
        if found == 'planned': return 'planificado (dry-run)'
        if found: return 'disponible'
        return 'pendiente/error' if install_tools else 'sin instalar'
    print('\nHERRAMIENTAS GLOBALES')
    for t in ('rtk','engram'):
        present=command(t)
        if not present and install_tools:
            ok=install_github_binary(t,dry_run)
            present=command(t) if ok and not dry_run else ('planned' if ok else None)
        results[t]=state(present)
    # Prefer the cached npx runner rather than a global npm installation,
    # which often requires administrator permissions on Linux.
    gn=command('gitnexus')
    npx=command('npx')
    if gn:
        gitnexus_base=[gn]
        results['gitnexus']='disponible (CLI global)'
    elif npx and install_tools:
        gitnexus_base=[npx,'--yes','gitnexus@latest']
        results['gitnexus']='disponible vía npx' if not dry_run else 'planificado (npx)'
    else:
        gitnexus_base=None
        results['gitnexus']='sin instalar (instalar Node.js + npm)' if not install_tools else 'pendiente/error'
    codex=command('codex')
    # Only initialize agent hooks/config when requested and supported.
    if install_tools and codex:
        if results['rtk']=='disponible':
            ok = run([command('rtk'),'init','-g','--codex'],timeout=45) if not dry_run else True
            results['rtk_codex']='disponible' if ok else 'pendiente/error'
        if results['engram']=='disponible':
            ok = run([command('engram'),'setup','codex'],timeout=90) if not dry_run else True
            results['engram_codex']='disponible' if ok else 'pendiente/error'
    if install_tools and codex:
        # GitHub's official remote MCP is useful for PRs, issues and Actions.
        # Configure only if a token env var already exists. Never persist the token itself.
        if os.environ.get('GITHUB_PAT_TOKEN'):
            if dry_run:
                print('  WOULD register GitHub official remote MCP (environment-based authentication)')
            else:
                ok = run([codex, 'mcp', 'add', 'github', '--url', 'https://api.githubcopilot.com/mcp/',
                          '--bearer-token-env-var', 'GITHUB_PAT_TOKEN'], timeout=60)
                results['github_mcp']='disponible' if ok else 'pendiente/error'
        else:
            print('  GitHub MCP: faltó GITHUB_PAT_TOKEN; configuración omitida sin pedir ni guardar secretos.')
    if install_tools and gitnexus_base:
        ok = run(gitnexus_base+['analyze','--skills'],cwd=project,timeout=600) if not dry_run else True
        results['gitnexus_index']='disponible' if ok and not dry_run else 'planificado (dry-run)' if dry_run else 'pendiente/error'
        if ok and codex:
            ok_setup = run(gitnexus_base+['setup','-c','codex'],cwd=project,timeout=120) if not dry_run else True
            results['gitnexus_codex']='disponible' if ok_setup and not dry_run else 'planificado (dry-run)' if dry_run else 'pendiente/error'
    # Context Mode is deliberately not installed by default: overlapping routing with RTK.
    results['context-mode']='no instalado (evita hooks de compresión duplicados)' if no_context_mode else 'opt-in, no instalado'
    return results


def precommit_script():
    return '''#!/bin/sh
# Generated by repo-setup. Lightweight and cross-platform with Git Bash.
set -eu
git diff --cached --check
# Prevent accidental staging of conventional secret files (not a full secret scanner).
if git diff --cached --name-only --diff-filter=ACM | grep -Ei '(^|/)(\\.env($|\\.)|id_rsa$|id_ed25519$|.*\\.(pem|p12|key)$)' >/dev/null; then
  echo 'ERROR: posible archivo sensible staged (revisar antes del commit).' >&2
  exit 1
fi
'''


def ci_workflow(detected):
    steps = [
        'name: Agent quality baseline',
        'on:',
        '  pull_request:',
        '  workflow_dispatch:',
        'permissions:',
        '  contents: read',
        'concurrency:',
        '  group: quality-${{ github.workflow }}-${{ github.ref }}',
        '  cancel-in-progress: true',
        'jobs:',
        '  checks:',
        '    runs-on: ubuntu-latest',
        '    steps:',
        '      - uses: actions/checkout@v4',
        '        with:',
        '          fetch-depth: 0',
        '      - name: Whitespace validation of the PR',
        '        env:',
        '          BASE_SHA: ${{ github.event.pull_request.base.sha }}',
        '        run: |',
        '          if [ -n "$BASE_SHA" ]; then git diff --check "$BASE_SHA" HEAD; else git diff --check; fi',
    ]
    if detected['javascript']:
        steps += [
            '      - uses: actions/setup-node@v4',
            '        with:',
            '          node-version: 22',
            '          cache: npm',
            '        if: ${{ hashFiles(\'package-lock.json\') != \'\' }}',
            '      - name: Node checks (when npm lockfile exists)',
            '        if: ${{ hashFiles(\'package-lock.json\') != \'\' }}',
            '        run: |',
            '          npm ci --ignore-scripts',
            '          npm run lint --if-present',
            '          npm run typecheck --if-present',
            '          npm run test --if-present',
        ]
    if detected['python']:
        steps += [
            '      - uses: actions/setup-python@v5',
            '        with:',
            '          python-version: "3.12"',
            '      - name: Python syntax check (tracked files)',
            '        run: |',
            '          python - <<\'PYCODE\'',
            '          import pathlib, subprocess, ast',
            '          files = subprocess.check_output(["git", "ls-files", "*.py"]).decode().splitlines()',
            '          for p in files: ast.parse(pathlib.Path(p).read_text(encoding="utf-8-sig"), filename=p)',
            '          print(f"Checked {len(files)} Python files")',
            '          PYCODE',
        ]
    return '\n'.join(steps)+'\n'



def dependabot_config(detected):
    ecosystems = [('github-actions', '/')]
    for key, ecosystem in (('javascript','npm'),('python','pip'),('rust','cargo'),('go','gomod')):
        if detected[key]:
            ecosystems.append((ecosystem, '/'))
    lines = ['# Generated by repo-setup: Dependency update pull requests', 'version: 2', 'updates:']
    for ecosystem, directory in ecosystems:
        lines.extend([
            f'  - package-ecosystem: "{ecosystem}"',
            f'    directory: "{directory}"',
            '    schedule:',
            '      interval: "weekly"',
            '    open-pull-requests-limit: 3',
        ])
    return '\n'.join(lines)+'\n'


def existing_hooks_path(project):
    try:
        proc = subprocess.run(['git', '-C', str(project), 'config', '--local', '--get', 'core.hooksPath'],
                              capture_output=True, text=True, timeout=15)
        return proc.returncode == 0 and bool(proc.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        return False


def bootstrap(args):
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir(): raise SystemExit('La carpeta indicada no existe.')
    if not (project/'.git').exists():
        raise SystemExit('Se requiere un repositorio Git existente; no se modifica una carpeta arbitraria.')
    print(f'PROYECTO: {project}')
    print(f'SISTEMA: {platform.system()} {platform.machine()}')
    files = git_files(project)
    tech = project_type(project,files)
    print('STACK:', ', '.join(k for k,v in tech.items() if v) or 'genérico')
    if not args.dry_run:
        print('Preservando cambios previos y políticas existentes (sin push ni merge).')
    write_if_missing(project/'.github'/'PULL_REQUEST_TEMPLATE.md', '''## Resumen

## Cambios

## Validaciones ejecutadas
- [ ] Tests/Lint del proyecto
- [ ] `git diff --check`
- [ ] Análisis de impacto GitNexus (si está disponible)

## Riesgos y plan de reversión
''', args.dry_run)
    sync_agents(project/'AGENTS.md',args.dry_run)
    ignore_generated(project,args.dry_run)
    atomic_write(project/'.agent-bootstrap'/'project-map.md',build_map(project,files,tech),args.dry_run)
    if args.hooks:
        if (project/'.githooks/pre-commit').exists():
            print('Hooks existentes preservados; no sobrescribir.')
        elif existing_hooks_path(project):
            print('Hooks ya configurados en Git; no cambiar core.hooksPath.')
        elif (project/'.husky').exists() or (project/'.pre-commit-config.yaml').exists():
            print('Husky/pre-commit detectado: se respeta su configuración; no crear hooks duplicados.')
        else:
            hook=project/'.githooks/pre-commit'
            atomic_write(hook,precommit_script(),args.dry_run)
            if not args.dry_run:
                hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                run(['git','-C',str(project),'config','--local','core.hooksPath','.githooks'])
    workflows=list((project/'.github/workflows').glob('*.yml'))+list((project/'.github/workflows').glob('*.yaml'))
    if args.ci:
        write_if_missing(project/'.github/dependabot.yml', dependabot_config(tech), args.dry_run)
        if workflows:
            print('CI existente detectada: se conserva sin cambios.')
        else:
            atomic_write(project/'.github/workflows/agent-quality.yml',ci_workflow(tech),args.dry_run)
    skill_src=ROOT/'skills/repo-onboarding/SKILL.md'
    if skill_src.exists():
        write_if_missing(project/'.agents/skills/repo-onboarding/SKILL.md',skill_src.read_text(encoding='utf-8'),args.dry_run)
    results=configure_tools(project,tech,args.dry_run,args.install_tools,True)
    if not args.dry_run:
        state={'date_utc':datetime.now(timezone.utc).isoformat(), 'stack':tech,'tools':results,
               'notes':'No hay medición de tokens totales del agente; rtk gain refleja solo los comandos interceptados.'}
        atomic_write(project/'.agent-bootstrap/state.json',json.dumps(state,ensure_ascii=False,indent=2)+'\n')
    print('\nLISTO: estructura básica preparada; resultados de herramientas:',results)
    if command('rtk'):
        print('Medición local disponible: rtk gain (no equivale al total de tokens del agente)')
    if not args.install_tools:
        print('Para instalar RTK, Engram y GitNexus: repetir con --full')
    elif not args.dry_run:
        failures=[name for name,status in results.items() if status == 'pendiente/error']
        if failures:
            print('PREPARACIÓN PARCIAL: comprobá y reintentá estas integraciones: '+', '.join(failures), file=sys.stderr)
            raise SystemExit(2)


def doctor(project):
    """Quick, read-only diagnostic (no network requests or secrets)."""
    print('REPO SETUP — DIAGNÓSTICO')
    print('Plataforma:', platform.system(), platform.machine())
    print('Proyecto:', project)
    for name in ('python', 'git', 'node', 'npm', 'codex', 'gh', 'rtk', 'gitnexus', 'engram'):
        print(f'  {name:<12} ' + (command(name) or 'no disponible en PATH'))
    state = project / '.agent-bootstrap' / 'state.json'
    print('Estado anterior:', state if state.exists() else 'no configurado')
    print('Tokens: `rtk gain` informa ahorros estimados de salidas compatibles; no el gasto total.')


def main():
    parser=argparse.ArgumentParser(description='Bootstrap seguro de proyectos para agentes de IA, Windows y Linux.')
    parser.add_argument('project',nargs='?',default='.',help='Ruta de repo Git (por defecto: carpeta actual)')
    parser.add_argument('--full',action='store_true',help='Preparar todo: herramientas, hooks y CI en una ejecución')
    parser.add_argument('--doctor',action='store_true',help='Diagnóstico rápido sin modificar archivos')
    parser.add_argument('--dry-run',action='store_true',help='Mostrar y no escribir ni instalar')
    parser.add_argument('--install-tools',action='store_true',help='Instala herramientas globales de releases oficiales; requiere Internet')
    parser.add_argument('--ci',action='store_true',help='Crear CI mínima solo si no existe CI')
    parser.add_argument('--hooks',action='store_true',help='Configurar pre-commit liviano solo si no existen hooks')
    args=parser.parse_args()
    if args.doctor:
        doctor(Path(args.project).expanduser().resolve())
        return
    if args.full:
        args.install_tools = True
        args.hooks = True
        args.ci = True
    bootstrap(args)

if __name__=='__main__':
    main()
