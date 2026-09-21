"""Composición de las implementaciones concretas de Brújula."""

from __future__ import annotations

from typing import Any

from app.adaptadores.fuente_ejemplo import FuenteEjemplo
from app.adaptadores.gemini_provider import GeminiProvider
from app.adaptadores.graph_calendario import FuenteCalendarioGraph
from app.config import Configuracion
from app.puertos.llm_provider import LLMProvider
from app.puertos.task_source import TaskSource
from app.servicios.servicio_agenda import ServicioAgenda


def servicio_de_ejemplo() -> ServicioAgenda:
    """Modo demo: datos fijos, sin red y sin usuario."""
    fuentes: list[TaskSource] = [FuenteEjemplo()]
    return ServicioAgenda(fuentes)


def servicio_para_usuario(cliente_graph: Any) -> ServicioAgenda:
    """Modo real: las fuentes de ESTE usuario, con SU cliente de Graph."""
    fuentes: list[TaskSource] = [FuenteCalendarioGraph(cliente_graph)]
    return ServicioAgenda(fuentes)


def proveedor_gemini(config: Configuracion) -> LLMProvider:
    """Construye el proveedor de Gemini."""
    return GeminiProvider(config)