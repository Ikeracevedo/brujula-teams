"""DATOS FALSOS. NO SALEN DE MICROSOFT GRAPH.

Este modulo existe para que la demo del spike muestre la FORMA de la respuesta
sin depender todavia de Graph (OT-05 / F3). Es un `stub`: la misma tecnica que
el plan usa para que Iker no quede bloqueado esperando el paquete de Julian.

Al conectar Graph, este modulo se borra y su lugar lo toma un adaptador que
implementa el puerto `TaskSource`. La firma que consume la capa de presentacion
NO cambia: `-> list[Pendiente]`. Eso es exactamente lo que promete el ADR-004.
"""

from datetime import datetime, timedelta

from dominio import FuentePendiente, Pendiente

_HOY = datetime.now()


def pendientes_de_la_semana() -> list[Pendiente]:
    """Devuelve datos de ejemplo. Firma identica a la del futuro TaskSource."""
    return [
        Pendiente(
            id="plan-001",
            titulo="Entregar checkpoint 1 - Proyecto en TIC 1",
            fuente=FuentePendiente.PLANNER,
            vence=_HOY + timedelta(days=2),
            url_origen="https://tasks.office.com/ejemplo/task/plan-001",
            confianza=1.0,
            contexto="Plan: Proyecto TIC 1 / Bucket: Entregas",
        ),
        Pendiente(
            id="cal-002",
            titulo="Sustentacion parcial con el docente",
            fuente=FuentePendiente.CALENDARIO,
            vence=_HOY + timedelta(days=4, hours=3),
            url_origen="https://outlook.office.com/calendar/ejemplo/cal-002",
            confianza=1.0,
            contexto="Sala 3-204 - 45 min",
        ),
        Pendiente(
            id="todo-003",
            titulo="Leer capitulo 4 de arquitectura hexagonal",
            fuente=FuentePendiente.TODO,
            vence=_HOY + timedelta(days=5),
            url_origen="https://to-do.office.com/tasks/ejemplo/todo-003",
            confianza=1.0,
            contexto=None,
        ),
        # --- El caso interesante: NO es un hecho, es una inferencia ---
        Pendiente(
            id="msg-004",
            titulo="Subir el avance del backend antes del viernes",
            fuente=FuentePendiente.MENSAJE,
            vence=_HOY + timedelta(days=3),
            url_origen="https://teams.microsoft.com/l/message/ejemplo/msg-004",
            confianza=0.72,
            contexto='Mensaje del docente en el canal General: "no olviden subir '
                     'el avance del backend antes del viernes"',
        ),
    ]
