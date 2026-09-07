from __future__ import annotations

from functools import lru_cache

from app.adaptadores.fuente_ejemplo import FuenteEjemplo
from app.puertos.task_source import TaskSource
from app.servicios.servicio_agenda import ServicioAgenda


@lru_cache
def obtener_servicio_agenda() -> ServicioAgenda:
    fuentes: list[TaskSource] = [FuenteEjemplo()]
    return ServicioAgenda(fuentes)
