"""Entidad de dominio `Pendiente` (ADR-005) - ENSAYO dentro del spike.

REGLA HEXAGONAL VERIFICABLE (ADR-004): este modulo NO importa nada fuera de la
libreria estandar. Ni el SDK de Teams, ni FastAPI, ni Mongo, ni Graph.
Si algun dia se cuela un import externo aqui, la arquitectura ya se rompio.

Este archivo es un ENSAYO desechable. La version permanente vive en
`app/domain/pendiente.py` y se escribe en la OT-02B.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class FuentePendiente(str, Enum):
    """De donde salio el pendiente. Define su nivel de confianza base."""

    PLANNER = "Planner"
    TODO = "To Do"
    CALENDARIO = "Calendario"
    MENSAJE = "Mensaje"


@dataclass(frozen=True)
class Pendiente:
    """Un compromiso del usuario, normalizado desde cualquier fuente.

    `confianza` es el campo clave del diseno (ADR-005):
      1.0  -> HECHO. Vino de un sistema estructurado (Planner, To Do, Calendario).
      <1.0 -> INFERENCIA. Un LLM lo dedujo de texto libre. Puede estar mal.

    Brujula NUNCA presenta una inferencia como si fuera un hecho. Esa distincion
    es la respuesta a "y si el modelo alucina una fecha de entrega?".
    """

    id: str
    titulo: str
    fuente: FuentePendiente
    vence: datetime | None
    url_origen: str          # trazabilidad OBLIGATORIA: toda afirmacion enlaza a su origen
    confianza: float
    contexto: str | None = None

    @property
    def es_hecho(self) -> bool:
        return self.confianza >= 1.0
