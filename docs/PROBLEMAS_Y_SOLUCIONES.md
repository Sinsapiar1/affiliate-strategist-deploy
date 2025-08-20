# Informe técnico: problemas actuales y soluciones propuestas

Este documento resume los problemas observados en producción (Railway) y propone soluciones robustas.

## 1) Resumen (estado actual)
- Despliegue OK, estáticos con WhiteNoise, PDF y vistas base funcionan.
- Registro e inicio de sesión: funcionando.
- Límite mensual (auth): se aplica en backend (bloquea >5 en plan free), pero el contador visual a veces muestra incongruencia temporal hasta refrescar.
- Límite anónimo: aún no efectivo en algunos escenarios; se detecta tráfico ilimitado sin registro.

## 2) Problemas

### P1. Registro fallaba (“Error al crear la cuenta…”) — RESUELTO
- Causas: login dentro de block `atomic`, creación duplicada de `UserProfile` (colisión UNIQUE).
- Fix: sacar `login()` del bloque, confiar en signal `post_save` para `UserProfile` y usar `get_or_create` en las señales.

### P2. Límite de anónimo (2/día) NO se respeta
- Causas: múltiples workers, backend de cache no compartido, IP detrás de proxy.
- Estado: se añadió control por DB + fallback por sesión; aún se observan casos ilimitados.

### P3. Límite mensual por plan (free 5/mes) inconsistente visualmente
- Backend: se bloquea correctamente al superar el límite.
- UI: tras navegar a Historial y volver, se observó duplicación del contador (1 → 2) sin realizar un nuevo análisis.
- Causas probables: doble POST o re-ejecución en navegación/retroceso o latencia de refresco de UI.

## 3) Soluciones ya aplicadas
- Registro estable: fuera de `atomic`, conflicto UNIQUE resuelto.
- Señales `post_save` robustas con `get_or_create`.
- Contador mensual atómico: `select_for_update`, tope antes de incrementar, incremento solo en éxito.
- Idempotencia de análisis: clave efímera (20s) por usuario/IP+parámetros para evitar doble envío/doble conteo.
- Rate limit anónimo: uso de modelo `AnonymousUsageTracker` + fallback por sesión.
- Orden middleware: `Authentication` antes de `RateLimit`.

## 4) Soluciones recomendadas (producción)

### S1. Cache compartido (Redis) — PRIORIDAD ALTA
Configurar Redis en Railway para que el rate limit sea global y confiable.

Ejemplo de settings:
```python
if os.getenv('REDIS_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': os.getenv('REDIS_URL'),
            'OPTIONS': {'socket_timeout': 5},
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': str(BASE_DIR / 'cache'),
            'TIMEOUT': 300,
        }
    }
```

### S2. Rate limit anónimo con operaciones atómicas
Con Redis usar `cache.add` + `cache.incr` atómico y TTL de 24h. Bloquear cuando `count > 2`.

### S3. Límite mensual autenticado con transacción (Implementado)
En POST `/` envolver verificación/incremento:
```python
from django.db import transaction
with transaction.atomic():
    profile = UserProfile.objects.select_for_update().get(user=request.user)
    profile.reset_monthly_counter_if_needed()
    if not profile.can_analyze():
        # retornar 429
    profile.add_analysis_count()
```

### S4. Logging detallado en registro (Implementado)
Registrar la excepción real (`logger.exception`) y mostrar mensajes específicos de colisión (username/email).

### S5. Base de datos
- Recomendado: Postgres en Railway para persistencia. Si no, SQLite es solo para demo y no persistirá entre réplicas.

### S6. Workers
- Sin Redis temporalmente: usar `--workers 1` en Gunicorn para que el rate limit (LocMem) funcione consistentemente.

## 7) Acciones inmediatas siguientes
1) Confirmar el header de IP real en Railway/Proxy (X-Forwarded-For vs CF-Connecting-IP) y ajustar `get_client_ip` en middleware.
2) Conectar Redis gestionado y mover rate limit anónimo a Redis con `incr` atómico + TTL 24h (global entre workers).
3) En UI, ya se refresca banner tras POST; considerar invalidar caché/estado al volver de Historial para evitar duplicaciones visuales.
4) Monitoreo: activar logs de `MIDDLEWARE` y `can_make_request` para trazar decisiones.

## 5) Plan de acción (prioridad)
1) Añadir servicio Redis y variable `REDIS_URL`.
2) Implementar `incr` atómico en middleware.
3) Usar transacciones para contadores mensuales.
4) Mejorar logging en registro y mostrar errores claros.
5) Activar Postgres para persistencia real.

## 6) Alternativa si no se usa Redis
Implementar rate limit anónimo en DB con `select_for_update()` (más carga en DB, pero consistente).