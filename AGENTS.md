# Instrucciones de mantenimiento de Repo Setup Kit

- El objetivo es un bootstrap Python 3.10+ sin dependencias de terceros.
- No cambiar el comportamiento existente de proyectos preparados sin agregar tests de regresión.
- Mantener compatibilidad Windows/Linux, con rutas seguras y scripts idempotentes.
- No copiar credenciales, tokens de GitHub, ni contenido sensible a ningún archivo generado.
- Priorizar instalaciones desde fuentes oficiales; no usar `curl | sh` en el código automatizado.
- Ejecutar `python -m unittest discover -s tests -v` y `python -m py_compile repo_setup.py` antes de PR.
- El ahorro de tokens debe expresarse como estimación medida, no garantía global.
