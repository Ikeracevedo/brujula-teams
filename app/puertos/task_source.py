from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from app.dominio.pendiente import Pendiente


@runtime_checkable
class TaskSource(Protocol):
    """
    Cualquier objeto con estos 2 miembros es un TaskSource

    Protocol, no ABC: el adaptador no hereda ni importa esta interfaz.
    mypy lo acepta si tiene la forma correcta (tipado ESTRUCTURAL,
    como el 'duck typing' de Python en tiempo de ejecucion, pero
    verificado de forma estatica).
    """

    @property
    def nombre(self) -> str:
        """Nombre legible de la fuente. Aparece en Agenda.fuentes_fallidas"""

    async def obtener_pendientes(
        self,
        desde: datetime,
        hasta: datetime,
    ) -> list[Pendiente]:
        """Pendientes en la ventana [desde, hasta].

        Contrato de errores
        - sin pendientes -> lista vacia
        - no se pudo consultar -> FuenteNoDisponibleError

        Nunca devolver [] para senalar un fallo.
        """
