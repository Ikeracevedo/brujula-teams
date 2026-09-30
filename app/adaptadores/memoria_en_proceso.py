from __future__ import annotations

from collections import deque

from app.dominio.conversacion import Turno


class MemoriaEnProceso:
    """Memoria en RAM. Se pierde al reiniciar; sirve para tests y desarrollo."""

    def __init__(self, max_guardados: int = 40) -> None:
        self._max = max_guardados
        self._datos: dict[str, deque[Turno]] = {}

    async def turnos(self, conversacion_id: str, limite: int) -> list[Turno]:
        if limite <= 0:
            return []
        return list(self._datos.get(conversacion_id, ()))[-limite:]

    async def agregar(self, conversacion_id: str, nuevos: list[Turno]) -> None:
        cola = self._datos.setdefault(conversacion_id, deque(maxlen=self._max))
        cola.extend(nuevos)

    async def olvidar(self, conversacion_id: str) -> None:
        self._datos.pop(conversacion_id, None)