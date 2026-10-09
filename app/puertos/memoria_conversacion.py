"""Contrato de memoria acotada por usuario y conversación.

El servicio no conoce MongoDB ni el canal Teams. Ambos identificadores son
obligatorios para evitar que un chat compartido mezcle datos de personas.
"""

from __future__ import annotations

from typing import Protocol

from app.dominio.conversacion import Turno


class MemoriaConversacion(Protocol):
    async def turnos(self, usuario_id: str, conversacion_id: str, limite: int) -> list[Turno]: ...

    async def agregar(self, usuario_id: str, conversacion_id: str, nuevos: list[Turno]) -> None: ...

    async def olvidar(self, usuario_id: str, conversacion_id: str) -> None: ...
