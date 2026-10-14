---
name: repo-onboarding
description: Prepara un repositorio Git para agentes con indexación, memoria, ahorro de tokens, validaciones y PR sin sobrescribir la configuración existente.
---

# Onboarding de repositorios

Cuando se abra un repositorio desconocido:

1. Comprobar `git status` y leer primero `AGENTS.md` y `.agent-bootstrap/project-map.md` si existen.
2. Navegar con GitNexus (símbolos, llamadas, impacto) antes de abrir directorios enteros. Si el grafo está desactualizado, ejecutar `gitnexus analyze` cuando sea posible.
3. Recuperar decisiones relevantes desde Engram usando búsquedas específicas; no guardar salidas grandes ni credenciales.
4. Usar RTK para resultados ruidosos de terminal cuando esté correctamente integrado; repetir sin compresión cuando falten detalles.
5. Priorizar scripts y verificaciones propias del proyecto. Antes de PR: `git diff --check`, tests pertinentes, revisión de impacto y riesgos.
6. No inventar ahorro en tokens, no realizar despliegues y no hacer push/merge sin permiso.
