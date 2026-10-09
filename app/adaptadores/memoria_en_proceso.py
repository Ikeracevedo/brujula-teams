"""Memoria temporal para desarrollo y pruebas sin MongoDB.

Las claves incluyen usuario y conversación. El historial desaparece al
reiniciar el proceso; producción usa MemoriaMongo cuando hay URI.
"""

from __future__ import annotations

from collections import deque

from app.dominio.conversacion import Turno


class MemoriaEnProceso:
    def __init__(self, max_guardados: int = 40) -> None:
        self._max = max_guardados
        self._datos: dict[tuple[str, str], deque[Turno]] = {}

    async def turnos(self, usuario_id: str, conversacion_id: str, limite: int) -> list[Turno]:
        if limite <= 0:
            return []
        return list(self._datos.get((usuario_id, conversacion_id), ()))[-limite:]

    async def agregar(self, usuario_id: str, conversacion_id: str, nuevos: list[Turno]) -> None:
        if not nuevos:
            return
        cola = self._datos.setdefault((usuario_id, conversacion_id), deque(maxlen=self._max))
        cola.extend(nuevos)

    async def olvidar(self, usuario_id: str, conversacion_id: str) -> None:
        self._datos.pop((usuario_id, conversacion_id), None)
