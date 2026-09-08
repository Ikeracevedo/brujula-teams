from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

# Por debajo de este umbral el pendiente no vino de un
# sistema estructurado lo dedujo un modelo de lenguaje
UMBRAL_CONFIANZA_ALTA = 0.99


class FuentePendiente(StrEnum):
    """
    De donde salio el pendiente

    StrEnum hace que cada miembreo sea un str asi que serializa a JSON
    Sin conversion manual y se compara con cadenas directamente. Sigue siendo un tipo cerrado:
    mypy rechaza cualquier valor que no este en la lista.
    """

    PLANNER = "PLANNER"
    TODO = "TODO"
    CALENDARIO = "CALENDARIO"
    MENSAJE = "MENSAJE"


@dataclass(frozen=True, slots=True)
class Pendiente:
    """
    Un compromiso del usuario, normalizado desde cualqueir fuente

    frozen=true -> inumtable
    slots=true -> menos memoria y bloquea atributos inventados

    Campos obligatorios primero opciones despues los exige el dataclass
    """

    id: str
    titulo: str
    fuente: FuentePendiente
    url_origen: str
    vence: datetime | None = None
    confianza: float = 1.0
    contexto: str | None = None

    def __post_init__(self) -> None:
        """
        Valida los invariantes. Un pendiente invalido no llega a existir
        """

        if not self.id.strip():
            raise ValueError("Pendiente.id no puede estar vacio")
        if not self.titulo.strip():
            raise ValueError("Pendiente.titulo no puede estar vacio")
        if not self.url_origen.strip():
            raise ValueError("Pendiente.url_origen no puede estar vacio")
        if not 0.0 <= self.confianza <= 1.0:
            raise ValueError("Pendiente.confianza debe estar entre 0 y 1")
        if self.contexto is not None and not self.contexto.strip():
            raise ValueError("Pendiente.contexto no puede estar vacio")

    @property
    def es_inferido(self) -> bool:
        """
        True si lo dedujo un LLM en vez de vernir de un sistema de microsoft
        """
        return self.confianza < UMBRAL_CONFIANZA_ALTA
