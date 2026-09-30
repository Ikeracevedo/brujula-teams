"""Dominio: un turno de conversacion entre una persona y el asistente.

Solo libreria estandar (regla de app/dominio).
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