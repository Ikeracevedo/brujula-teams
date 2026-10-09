"""Dominio: un archivo adjunto a un mensaje.

Solo libreria estandar (regla de app/dominio).
"""

from __future__ import annotations

from dataclasses import dataclass

MAX_BYTES_ADJUNTO = 10 * 1024 * 1024  # 10 MB por archivo


class AdjuntoNoSoportadoError(Exception):
    """El archivo no se puede leer. El mensaje es apto para mostrar al usuario."""


@dataclass(frozen=True, slots=True)
class Adjunto:
    nombre: str
    mime: str
    datos: bytes
