# Eliminación de Defaults - docker-compose.yml

Fecha: 13/02/2026

---

## Problema Identificado

`docker-compose.yml` tenía defaults hardcodeados (e.g., `:-voice_db`) que ignoraban las variables inyectadas por Coolify si estas no estaban explícitamente seteadas en el contexto de ejecución, causando fallback a valores incorrectos (como `Mcalderon` siendo ignorado por `voice_db`).

---

## Variables Modificadas

Se eliminaron TODOS los defaults `:-valor` para obligar a que `docker-compose` falle si la variable no está presente, garantizando que tome lo que Coolify inyecta.

### Service: app

| Variable | ANTES | DESPUÉS |
|----------|-------|---------|
| PORT | `${PORT:-8000}` | `${PORT}` |
| APP_ENV | `${APP_ENV:-development}` | `${APP_ENV}` |
| POSTGRES_USER | `${POSTGRES_USER:-postgres}` | `${POSTGRES_USER}` |
| POSTGRES_PASSWORD | `${POSTGRES_PASSWORD:-postgres}` | `${POSTGRES_PASSWORD}` |
| POSTGRES_DB | `${POSTGRES_DB:-voice_db}` | `${POSTGRES_DB}` |
| REDIS_URL | `redis://redis:6379/0` | `${REDIS_URL}` |
| API_KEY | `${API_KEY:-dev-api-key}` | `${API_KEY}` |
| SECRET_KEY | `${SECRET_KEY:-dev-secret-key}` | `${SECRET_KEY}` |
| OTRAS KEYS | `:-` (defaults vacíos o valores) | `${VAR}` (sin default) |

Comando de Healthcheck también actualizado:
Antes: `http://localhost:${PORT:-8000}/api/system/health`
Después: `http://localhost:${PORT}/api/system/health`

### Service: db

| Variable | ANTES | DESPUÉS |
|----------|-------|---------|
| POSTGRES_USER | `${POSTGRES_USER:-postgres}` | `${POSTGRES_USER}` |
| POSTGRES_PASSWORD | `${POSTGRES_PASSWORD:-postgres}` | `${POSTGRES_PASSWORD}` |
| POSTGRES_DB | `${POSTGRES_DB:-voice_db}` | `${POSTGRES_DB}` |

---

## Verificación

**Búsqueda de defaults residuales:**
`grep ":-" docker-compose.yml` -> **0 coincidencias** (Limpio).

---

## .env.example Actualizado

Se agregó advertencia explícita:
```bash
# WARNING: ALL VARIABLES ARE REQUIRED
# NO DEFAULTS IN DOCKER-COMPOSE.YML
```

---

## Impacto

**Ahora:**
- Docker Compose fallará si falta alguna variable crítica.
- Coolify tiene control total sobre la configuración inyectada.
- Se elimina el riesgo de usar bases de datos "hardcodeadas" por error.

---

## Estado

**Defaults eliminados:** ✅ SÍ
**Listo para re-deploy:** ✅ SÍ
