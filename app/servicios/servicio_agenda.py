from __future__ import annotations

import asyncio
from collections.abc import Sequence
from datetime import datetime, timedelta

from app.dominio.agenda import Agenda, FuenteFallida
from app.dominio.errores import FuenteNoDisponibleError
from app.dominio.pendiente import Pendiente
from app.puertos.task_source import TaskSource

DIAS_DE_LA_VENTANA = 7


class ServicioAgenda:
    """Consulta todas las fuentes registradas y unifica el resultado."""

    def __init__(self, fuentes: Sequence[TaskSource]) -> None:
        # Inyeccion de dependencias por constructor: el servicio no CREA
        # sus fuentes, las RECIBE. Por eso en los tests le pasamos dobles
        # y en produccion adaptadores reales, sin tocar esta clase (D de SOLID).
        self._fuentes = list(fuentes)

    async def pendientes_de_la_semana(self, ahora: datetime) -> Agenda:
        """Pendientes de los proximos 7 dias, de todas las fuentes.

        Ahora se recibe como parametro, NO se llama datetime.now() aqui
        dentro. Una funcion que lee el reloj del sistema es imposible de
        testear de forma determinista -- inyectar el tiempo es inyectar
        una dependencia, igual que el FakeLLMProvider.

        """
        desde = ahora
        hasta = ahora + timedelta(days=DIAS_DE_LA_VENTANA)

        # return_exceptions=True: si una fuente falla, las demas siguen.
        # Sin esto, el primer fallo cancela TODAS las tareas del grupo.
        resultados = await asyncio.gather(
            *(fuente.obtener_pendientes(desde, hasta) for fuente in self._fuentes),
            return_exceptions=True,
        )

        pendientes: list[Pendiente] = []
        consultadas: list[str] = []
        fallidas: list[FuenteFallida] = []

        for fuente, resultado in zip(self._fuentes, resultados, strict=True):
            if isinstance(resultado, FuenteNoDisponibleError):
                # Fallo previsto (permisos, red): se reporta al usuario.
                fallidas.append(FuenteFallida(fuente.nombre, resultado.motivo))
            elif isinstance(resultado, BaseException):
                # Cualquier otra excepcion es un BUG propio, no una fuente
                # caida. Si se atrapara igual que la de arriba, cada bug
                # del proyecto se disfrazaria de "fuente caida" y nunca
                # te enterarias. Se re-lanza para que explote visiblemente.
                raise resultado
            else:
                pendientes.extend(resultado)
                consultadas.append(fuente.nombre)

        return Agenda(
            pendientes=tuple(self._ordenar(pendientes)),
            fuentes_consultadas=tuple(consultadas),
            fuentes_fallidas=tuple(fallidas),
        )

    @staticmethod
    def _ordenar(pendientes: list[Pendiente]) -> list[Pendiente]:
        """Primero lo que vence antes. Sin fecha, al final.
        A igual fecha, primero lo mas confiable."""
        return sorted(
            pendientes,
            key=lambda p: (
                p.vence is None,          # False (0) antes que True (1)
                p.vence or datetime.max,  # desempate por fecha
                -p.confianza,             # mas confiable primero
            ),
        )