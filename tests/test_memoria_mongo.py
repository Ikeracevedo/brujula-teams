"""Mongo conserva el límite de usuario en lectura, escritura y borrado."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.adaptadores.memoria_mongo import MemoriaMongo
from app.dominio.conversacion import Turno


class ColeccionDoble:
    def __init__(self) -> None:
        self.filtros: list[dict[str, str]] = []
        self.indices: list[tuple[object, dict[str, object]]] = []

    async def create_index(self, keys: object, **kwargs: object) -> None:
        self.indices.append((keys, kwargs))

    async def find_one(
        self, filtro: dict[str, str], proyeccion: dict[str, object]
    ) -> dict[str, Any] | None:
        self.filtros.append(filtro)
        return None

    async def update_one(
        self, filtro: dict[str, str], cambio: dict[str, object], **kwargs: object
    ) -> None:
        self.filtros.append(filtro)

    async def delete_one(self, filtro: dict[str, str]) -> None:
        self.filtros.append(filtro)


async def test_cada_operacion_filtra_por_usuario_y_conversacion() -> None:
    col = ColeccionDoble()
    memoria = MemoriaMongo("mongodb://prueba", _coleccion=col)
    ahora = datetime(2026, 10, 9, tzinfo=UTC)

    await memoria.turnos("usuario-a", "chat-1", 10)
    await memoria.agregar("usuario-a", "chat-1", [Turno("usuario", "hola", ahora)])
    await memoria.olvidar("usuario-a", "chat-1")

    assert len(col.filtros) == 3
    assert all(
        filtro == {"usuario_id": "usuario-a", "conversacion_id": "chat-1"} for filtro in col.filtros
    )
    assert any(opciones.get("unique") is True for _, opciones in col.indices)
    assert any("expireAfterSeconds" in opciones for _, opciones in col.indices)
