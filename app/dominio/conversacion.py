"""Turnos breves que permiten continuar una pregunta sobre la agenda.

La memoria guarda preguntas y respuestas, nunca una copia de la agenda ni
tokens de Microsoft. Su alcance se limita a un usuario y una conversación.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

Rol = Literal["usuario", "asistente"]


@dataclass(frozen=True, slots=True)
class Turno:
    rol: Rol
    texto: str
    momento: datetime


class MemoriaNoDisponibleError(Exception):
    """Mongo no pudo leer o guardar memoria; el chat puede seguir sin ella."""
