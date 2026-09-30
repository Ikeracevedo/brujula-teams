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
        """Pendientes vigentes, con la ventana [desde, hasta] como filtro de FECHA.

        Que entra:
          - lo que vence dentro de la ventana
          - lo que NO tiene fecha de vencimiento y sigue abierto

        Un pendiente sin fecha no esta "fuera de la ventana": esta sin
        fechar, que no es lo mismo. Suele ser ademas el que mas se olvida.
        ServicioAgenda._ordenar ya los coloca al final, asi que el
        dominio siempre conto con ellos.

        Que NO entra:
          - lo ya completado. Traducir "completado" es trabajo del
            adaptador: Planner usa percentComplete, To Do usa status.
            El nucleo no conoce el vocabulario de Microsoft.

        Contrato de errores:
          - sin pendientes -> lista vacia
          - no se pudo consultar -> FuenteNoDisponibleError

        Nunca devolver [] para senalar un fallo.
        """
