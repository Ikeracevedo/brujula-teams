"""Capa de PRESENTACION: traduce list[Pendiente] -> Adaptive Card de Teams.

Es el unico modulo del demo que conoce el SDK de Teams. El dominio no sabe que
existe Teams; este modulo no sabe de donde salieron los Pendientes. Esa frontera
ES la arquitectura hexagonal (ADR-004), demostrada en 60 lineas.
"""

from datetime import datetime

from microsoft_teams.cards import (
    ActionSet,
    AdaptiveCard,
    Container,
    Fact,
    FactSet,
    OpenUrlAction,
    TextBlock,
)

from dominio import FuentePendiente, Pendiente

_ICONO = {
    FuentePendiente.PLANNER: "[Planner]",
    FuentePendiente.TODO: "[To Do]",
    FuentePendiente.CALENDARIO: "[Calendario]",
    FuentePendiente.MENSAJE: "[Mensaje]",
}


def _fecha(v: datetime | None) -> str:
    if v is None:
        return "Sin fecha"
    dias = (v.date() - datetime.now().date()).days
    etiqueta = {0: "hoy", 1: "manana"}.get(dias, f"en {dias} dias")
    return f"{v.strftime('%d/%m %H:%M')} ({etiqueta})"


def _bloque(p: Pendiente) -> Container:
    hechos = [
        Fact(title="Fuente", value=_ICONO[p.fuente]),
        Fact(title="Vence", value=_fecha(p.vence)),
    ]

    # El corazon del diseno: un HECHO y una INFERENCIA no se presentan igual.
    if p.es_hecho:
        hechos.append(Fact(title="Confianza", value="Confirmado (dato estructurado)"))
        color, estilo = "Good", "good"
    else:
        pct = int(p.confianza * 100)
        hechos.append(Fact(title="Confianza", value=f"{pct}% - inferido de un mensaje"))
        color, estilo = "Warning", "warning"

    items = [
        TextBlock(text=p.titulo, weight="Bolder", size="Medium", wrap=True, color=color),
        FactSet(facts=hechos),
    ]

    if p.contexto:
        items.append(TextBlock(text=p.contexto, wrap=True, is_subtle=True, size="Small"))

    if not p.es_hecho:
        items.append(
            TextBlock(
                text="Brujula no confirma este pendiente. Verificalo en el origen.",
                wrap=True,
                size="Small",
                color="Warning",
            )
        )

    # Trazabilidad OBLIGATORIA: toda afirmacion enlaza a su fuente.
    items.append(
        ActionSet(actions=[OpenUrlAction(title="Ver origen", url=p.url_origen)])
    )

    return Container(items=items, style=estilo, show_border=True, spacing="Medium")


def tarjeta_semana(pendientes: list[Pendiente]) -> AdaptiveCard:
    """Construye la tarjeta de 'que tengo esta semana'."""
    hechos = sum(1 for p in pendientes if p.es_hecho)
    inferidos = len(pendientes) - hechos

    cuerpo = [
        TextBlock(text="Tu semana", size="Large", weight="Bolder", wrap=True),
        TextBlock(
            text=f"{len(pendientes)} pendientes - {hechos} confirmados, "
                 f"{inferidos} inferidos de conversaciones",
            is_subtle=True,
            wrap=True,
            spacing="None",
        ),
    ]
    cuerpo += [_bloque(p) for p in sorted(pendientes, key=lambda p: (p.vence is None, p.vence))]
    cuerpo.append(
        TextBlock(
            text="DEMO OT-02A - datos de ejemplo. Sin conexion a Microsoft Graph.",
            size="Small",
            is_subtle=True,
            wrap=True,
            spacing="Large",
        )
    )
    return AdaptiveCard(body=cuerpo)
