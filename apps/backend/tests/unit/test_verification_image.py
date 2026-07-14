"""
Pruebas unitarias de la validacion de imagenes de carnet.

Nivel:   Unitaria
Tipo:    Funcional
Tecnica: Caja Blanca
Objetivo: garantizar que, tras relajar la verificacion, cualquier imagen legible
          de un tipo aceptado (JPEG/PNG) se acepte sin importar su calidad
          (resolucion/nitidez), y que se sigan rechazando los casos NO validos:
          tipo/formato no permitido, archivo ilegible y tamano excesivo.

Bajo prueba: app/modules/verification/service.py::_validate_image_quality
"""
from io import BytesIO

from fastapi import HTTPException
from PIL import Image

from app.core.config import settings
from app.modules.verification.service import _validate_image_quality


def _image_bytes(fmt: str, size=(10, 10), color=(120, 120, 120)) -> bytes:
    """Genera una imagen solida (nitidez ~0) y pequena (baja resolucion)."""
    buf = BytesIO()
    Image.new("RGB", size, color).save(buf, format=fmt)
    return buf.getvalue()


def test_imagen_pequena_y_borrosa_se_acepta():
    """Antes se rechazaba por 'Resolucion demasiado baja' / 'La imagen esta borrosa'.

    Una imagen 10x10 de color solido tiene resolucion minima y nitidez ~0; ahora
    debe aceptarse y devolver las metricas (para metadata del admin).
    """
    metrics = _validate_image_quality(_image_bytes("JPEG"), "image/jpeg")
    assert metrics["width"] == 10
    assert metrics["height"] == 10
    assert isinstance(metrics["quality_score"], float)


def test_png_pequeno_se_acepta():
    metrics = _validate_image_quality(_image_bytes("PNG"), "image/png")
    assert metrics["width"] == 10 and metrics["height"] == 10


def test_tipo_mime_no_permitido_se_rechaza():
    try:
        _validate_image_quality(_image_bytes("JPEG"), "image/gif")
        assert False, "deberia rechazar un content_type no permitido"
    except HTTPException as exc:
        assert exc.status_code == 400
        assert "Tipo de archivo no permitido" in exc.detail


def test_formato_real_no_permitido_se_rechaza():
    """content_type aceptado pero bytes de otro formato (GIF) -> se rechaza."""
    gif = _image_bytes("GIF")
    try:
        _validate_image_quality(gif, "image/png")
        assert False, "deberia rechazar un formato real no permitido"
    except HTTPException as exc:
        assert exc.status_code == 400
        assert "Formato de imagen no permitido" in exc.detail


def test_archivo_ilegible_se_rechaza():
    try:
        _validate_image_quality(b"esto no es una imagen", "image/png")
        assert False, "deberia rechazar bytes ilegibles"
    except HTTPException as exc:
        assert exc.status_code == 400
        assert "No se pudo leer la imagen" in exc.detail


def test_supera_tamano_maximo_se_rechaza():
    """El limite de tamano (guarda de seguridad, no calidad) sigue vigente."""
    data = _image_bytes("JPEG")
    original = settings.VERIFICATION_MAX_FILE_SIZE_BYTES
    try:
        settings.VERIFICATION_MAX_FILE_SIZE_BYTES = len(data) - 1
        _validate_image_quality(data, "image/jpeg")
        assert False, "deberia rechazar un archivo que supera el tamano maximo"
    except HTTPException as exc:
        assert exc.status_code == 400
        assert "supera el tamano permitido" in exc.detail
    finally:
        settings.VERIFICATION_MAX_FILE_SIZE_BYTES = original
