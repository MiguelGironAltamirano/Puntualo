"""
Pruebas unitarias del bundle TLS del fetcher de UNMSM.

Nivel:   Unitaria
Tipo:    Funcional
Técnica: Caja Blanca
Objetivo: garantizar que el intermediate CA que UNMSM omite en su cadena TLS
          esté empaquetado, sea un PEM válido y cargue en un SSLContext. Es una
          guardia de regresión (sin red) para el fix de "unable to get local
          issuer certificate" al scrapear sistemas.unmsm.edu.pe.

Bajo prueba: app/services/professor_validation/sources/unmsm_directory.py
"""
import ssl
from pathlib import Path

from app.services.professor_validation.sources import unmsm_directory


def test_ca_bundle_existe_y_es_pem():
    """El bundle debe existir y contener un certificado PEM."""
    path = Path(unmsm_directory._UNMSM_CA_BUNDLE)
    assert path.exists(), f"falta el bundle CA: {path}"
    contents = path.read_text()
    assert "-----BEGIN CERTIFICATE-----" in contents
    assert "-----END CERTIFICATE-----" in contents


def test_ca_bundle_carga_en_sslcontext():
    """`load_verify_locations` debe aceptar el bundle (parse guard).

    Si el PEM se corrompe o el encabezado de comentarios rompe el parseo, esto
    falla antes de llegar a producción.
    """
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.load_verify_locations(cafile=unmsm_directory._UNMSM_CA_BUNDLE)
    # El intermediate quedó cargado como cert conocido en el store del contexto.
    assert ctx.cert_store_stats()["x509"] >= 1


def test_ca_bundle_es_el_intermediate_esperado():
    """El bundle debe ser exactamente el intermediate de Sectigo que UNMSM omite."""
    full = Path(unmsm_directory._UNMSM_CA_BUNDLE).read_text()
    # El archivo lleva un encabezado de comentarios; aislamos el bloque PEM,
    # que es lo que PEM_cert_to_DER_cert espera recibir (debe empezar en BEGIN).
    begin = "-----BEGIN CERTIFICATE-----"
    end = "-----END CERTIFICATE-----"
    block = full[full.index(begin): full.index(end) + len(end)] + "\n"
    der = ssl.PEM_cert_to_DER_cert(block)
    # El CN del subject aparece codificado en el DER; basta comprobar su presencia.
    assert b"Sectigo Public Server Authentication CA OV R36" in der
