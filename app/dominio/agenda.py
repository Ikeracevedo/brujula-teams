"""Resultado agregado de una consulta de pendientes."""

from __future__ import annotations

from dataclasses import dataclass

from app.dominio.pendiente import Pendiente


@dataclass(frozen=True, slots=True)
class FuenteFallida:
    """Una fuente que no se pudo consultar, y por que."""

    nombre: str
    motivo: str


@dataclass(frozen=True, slots=True)
class Agenda:
    """Lo que se encontro, y lo que no se pudo mirar.

    fuentes_fallidas no es un detalle de logging: es parte de la
    respuesta al usuario. Una Agenda que oculta que Planner fallo
    esta mintiendo por omision.
    """

    # tuple, no list: frozen=True con una list adentro es inmutable
    # solo por fuera -- la lista interna se podria seguir mutando.
    # La inmutabilidad tiene que ser completa o no es inmutabilidad.
    pendientes: tuple[Pendiente, ...]
    fuentes_consultadas: tuple[str, ...]
    fuentes_fallidas: tuple[FuenteFallida, ...] = ()

    @property
    def esta_completa(self) -> bool:
        """True si todas las fuentes respondieron."""
        return len(self.fuentes_fallidas) == 0

    @property
    def total(self) -> int:
        return len(self.pendientes)