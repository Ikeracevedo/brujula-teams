from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from app.dominio.pendiente import Pendiente


@runtime_checkable
class PendientesRepository(Protocol):
    """Contrato de escritura para pendientes creados dentro de Brujula.

    Complementa TaskSource (lectura). Mismo principio: el servicio
    depende de este contrato, no de la implementacion concreta (Mongo,
    SQLite, memoria). Cambiar el motor de persistencia es cambiar el
    adaptador, no el servicio.
    """

    async def guardar(
        self,
        usuario_id: str,
        titulo: str,
        vence: datetime | None,
    ) -> Pendiente:
        """Persiste un pendiente propio y lo devuelve con su ID asignado.

        usuario_id es el AAD Object ID del usuario, nunca el correo.
        Si falla el almacenamiento: FuenteNoDisponibleError.
        Nunca devolver None ni lanzar silenciosamente.
        """
