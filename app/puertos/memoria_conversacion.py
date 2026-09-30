"""Puerto: contrato de la memoria de conversaciones.

Implementaciones:
  - MemoriaEnProceso -> diccionario en RAM. Tests y desarrollo.
  - MemoriaMongo     -> MongoDB con expiracion automatica (TTL).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.dominio.conversacion import Turno


@runtime_checkable
class MemoriaConversacion(Protocol):
    async def turnos(self, conversacion_id: str, limite: int) -> list[Turno]:
        """Ultimos `limite` turnos, del mas antiguo al mas reciente."""
        ...

    async def agregar(self, conversacion_id: str, nuevos: list[Turno]) -> None:
        """Anade turnos al final de la conversacion."""
        ...

    async def olvidar(self, conversacion_id: str) -> None:
        """Borra toda la conversacion."""
        ...