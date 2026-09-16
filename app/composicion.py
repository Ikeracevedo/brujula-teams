"""Composicion: que fuentes se consultan, y para quien.

Vive en la raiz de `app/`, NO en `app/servicios/`. Primer intento lo puso
alli y `test_servicios_no_conoce_adaptadores_ni_api` lo rechazo al
instante: un servicio depende de puertos, nunca de implementaciones.
Ensamblar implementaciones concretas es trabajo del composition root.

Antes de OT-04 el sistema tenia UN juego de fuentes para todo el mundo,
construido una sola vez (`lru_cache`). Con datos reales eso deja de ser
valido: las fuentes de Iker no son las de otro usuario, porque llevan
SU token. El servicio pasa a construirse por peticion.

> Regla general: un singleton solo es correcto mientras el objeto no
> tenga estado propio del usuario. En cuanto lo tiene, cachearlo deja de
> ser una optimizacion y pasa a ser una fuga de datos entre usuarios.
"""

from __future__ import annotations

from typing import Any

from app.adaptadores.fuente_ejemplo import FuenteEjemplo
from app.adaptadores.graph_calendario import FuenteCalendarioGraph
from app.puertos.task_source import TaskSource
from app.servicios.servicio_agenda import ServicioAgenda


def servicio_de_ejemplo() -> ServicioAgenda:
    """Modo demo: datos fijos, sin red y sin usuario. Lo usa el canal HTTP."""
    fuentes: list[TaskSource] = [FuenteEjemplo()]
    return ServicioAgenda(fuentes)


def servicio_para_usuario(cliente_graph: Any) -> ServicioAgenda:
    """Modo real: las fuentes de ESTE usuario, con SU cliente de Graph.

    En OT-05 esta lista crece con Planner y To Do. El resto del sistema
    no se entera: es una linea mas aqui.
    """
    fuentes: list[TaskSource] = [FuenteCalendarioGraph(cliente_graph)]
    return ServicioAgenda(fuentes)
