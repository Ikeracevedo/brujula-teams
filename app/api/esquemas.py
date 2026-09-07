from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.dominio.agenda import Agenda
from app.dominio.pendiente import Pendiente


class PendienteDTO(BaseModel):
    id: str
    titulo: str
    fuente: str
    url_origen: str = Field(description="Enlace al origen. Trazabilidad obligatoria.")
    vence: datetime | None
    confianza: float
    es_inferido: bool
    contexto: str | None

    @classmethod
    def desde_dominio(cls, p: Pendiente) -> PendienteDTO:
        # Traduccion explicita, campo por campo. No hay magia de "copiar
        # el objeto": si Pendiente gana un campo interno manana, este
        # metodo NO lo expone solo hasta que alguien decida hacerlo.
        return cls(
            id=p.id,
            titulo=p.titulo,
            fuente=str(p.fuente),
            url_origen=p.url_origen,
            vence=p.vence,
            confianza=p.confianza,
            es_inferido=p.es_inferido,
            contexto=p.contexto,
        )


class FuenteFallidaDTO(BaseModel):
    nombre: str
    motivo: str


class AgendaDTO(BaseModel):
    total: int
    esta_completa: bool = Field(
        description="False si alguna fuente no pudo consultarse. El cliente DEBE avisarlo."
    )
    fuentes_consultadas: list[str]
    fuentes_fallidas: list[FuenteFallidaDTO]
    pendientes: list[PendienteDTO]

    @classmethod
    def desde_dominio(cls, agenda: Agenda) -> AgendaDTO:
        return cls(
            total=agenda.total,
            esta_completa=agenda.esta_completa,
            fuentes_consultadas=list(agenda.fuentes_consultadas),
            fuentes_fallidas=[
                FuenteFallidaDTO(nombre=f.nombre, motivo=f.motivo)
                for f in agenda.fuentes_fallidas
            ],
            pendientes=[PendienteDTO.desde_dominio(p) for p in agenda.pendientes],
        )


class SaludDTO(BaseModel):
    estado: str
    version: str
    entorno: str
