from __future__ import annotations

from pymongo import AsyncMongoClient

from app.dominio.conversacion import Turno


class MemoriaMongo:
    """Memoria en MongoDB: un documento por conversacion.

    {_id: conversacion_id, turnos: [...], actualizado: datetime}

    - `$slice` al insertar: el documento nunca guarda mas de `max_guardados`.
    - Indice TTL sobre `actualizado`: Mongo borra solo las conversaciones
      que llevan `ttl_dias` sin actividad.
    """

    def __init__(
        self,
        uri: str,
        base: str = "brujula",
        coleccion: str = "conversaciones",
        max_guardados: int = 40,
        ttl_dias: int = 30,
    ) -> None:
        # tz_aware=True: las fechas vuelven con zona horaria (UTC), no ingenuas.
        self._cliente = AsyncMongoClient(uri, tz_aware=True)
        self._col = self._cliente[base][coleccion]
        self._max = max_guardados
        self._ttl_segundos = ttl_dias * 86400
        self._indice_listo = False

    async def _asegurar_indice(self) -> None:
        if not self._indice_listo:
            await self._col.create_index(
                "actualizado", expireAfterSeconds=self._ttl_segundos
            )
            self._indice_listo = True

    async def turnos(self, conversacion_id: str, limite: int) -> list[Turno]:
        if limite <= 0:
            return []
        await self._asegurar_indice()
        doc = await self._col.find_one(
            {"_id": conversacion_id},
            {"turnos": {"$slice": -limite}},
        )
        if not doc:
            return []
        return [
            Turno(t["rol"], t["texto"], t["momento"])
            for t in doc.get("turnos", [])
        ]

    async def agregar(self, conversacion_id: str, nuevos: list[Turno]) -> None:
        if not nuevos:
            return
        await self._asegurar_indice()
        docs = [
            {"rol": t.rol, "texto": t.texto, "momento": t.momento}
            for t in nuevos
        ]
        await self._col.update_one(
            {"_id": conversacion_id},
            {
                "$push": {"turnos": {"$each": docs, "$slice": -self._max}},
                "$set": {"actualizado": nuevos[-1].momento},
            },
            upsert=True,
        )

    async def olvidar(self, conversacion_id: str) -> None:
        await self._col.delete_one({"_id": conversacion_id})