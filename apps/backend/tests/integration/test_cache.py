"""
Pruebas de integración del cacheo con Redis.

Nivel:   Integración
Tipo:    No Funcional (Rendimiento)
Técnica: Caja Blanca
Objetivo: verificar hit/miss, TTL por endpoint e invalidación de cache.

Bajo prueba: app/utils/cache.py

TODO: implementar con un Redis de prueba (o fakeredis).
"""
import pytest

pytestmark = pytest.mark.skip(reason="Pendiente de implementación")


class TestCache:
    async def test_miss_then_hit(self):
        """La primera lectura es miss; la segunda, hit desde cache."""

    async def test_ttl_expiry(self):
        """La entrada expira según el TTL configurado."""

    async def test_invalidation(self):
        """Una escritura relacionada invalida la entrada cacheada."""
