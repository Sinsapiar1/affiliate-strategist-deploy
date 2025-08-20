# Informe técnico: problemas actuales y soluciones propuestas

Este documento resume los problemas observados en producción (Railway) y propone soluciones robustas.

## 1) Resumen
- Despliegue OK, estáticos con WhiteNoise, PDF y vistas base funcionan.
- Pendiente: registro falla con mensaje genérico y límites (anónimo/autenticado) no se respetan en Railway.

## 2) Problemas

### P1. Registro falla (“Error al crear la cuenta…”) 
- Causa probable: validación o excepción oculta (usuario/email duplicado, error DB) sin logging detallado.

### P2. Límite de anónimo (2/día) no se respeta
- En Railway/Gunicorn hay múltiples workers. Con cache en memoria (LocMem), cada worker lleva su propio contador → no es global.

### P3. Límite mensual por plan (free 5/mes) inconsistente
- Posibles causas: falta de `UserProfile` en algunos flujos, contadores sin transacción (condiciones de carrera), reseteo mensual no invocado antes de verificar.

## 3) Soluciones ya aplicadas
- Fallback DB a SQLite si no hay `PG*`/`DATABASE_URL`.
- Señales `post_save` + creación defensiva de `UserProfile` (registro y home).
- Rate limit solo para anónimos; clave `rate_limit:<ip>:<fecha>`.
- Orden middleware: `Authentication` antes de `RateLimit`.
- PDF con enlace directo y `<uuid:>`.

## 4) Soluciones recomendadas (producción)

### S1. Cache compartido (Redis)
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

### S3. Límite mensual autenticado con transacción
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

### S4. Logging detallado en registro
Registrar la excepción real (`logger.exception`) y mostrar mensajes específicos de colisión (username/email).

### S5. Base de datos
- Recomendado: Postgres en Railway para persistencia. Si no, SQLite es solo para demo y no persistirá entre réplicas.

### S6. Workers
- Sin Redis temporalmente: usar `--workers 1` en Gunicorn para que el rate limit (LocMem) funcione consistentemente.

## 5) Plan de acción (prioridad)
1) Añadir servicio Redis y variable `REDIS_URL`.
2) Implementar `incr` atómico en middleware.
3) Usar transacciones para contadores mensuales.
4) Mejorar logging en registro y mostrar errores claros.
5) Activar Postgres para persistencia real.

## 6) Alternativa si no se usa Redis
Implementar rate limit anónimo en DB con `select_for_update()` (más carga en DB, pero consistente).