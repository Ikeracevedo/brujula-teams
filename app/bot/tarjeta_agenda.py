from __future__ import annotations

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

from app.dominio.agenda import Agenda
from app.dominio.pendiente import FuentePendiente, Pendiente

_ETIQUETA_FUENTE: dict[FuentePendiente, str] = {
    FuentePendiente.PLANNER: "Planner",
    FuentePendiente.TODO: "To Do",
    FuentePendiente.CALENDARIO: "Calendario",
    FuentePendiente.MENSAJE: "Mensaje de Teams",
}


def _texto_fecha(vence: datetime | None, ahora: datetime) -> str:
    if vence is None:
        return "Sin fecha"
    dias = (vence.date() - ahora.date()).days
    relativo = {0: "hoy", 1: "mañana"}.get(dias)
    if relativo is None:
        relativo = f"en {dias} días" if dias > 0 else f"hace {abs(dias)} días"
    return f"{vence.strftime('%d/%m %H:%M')} ({relativo})"


def _bloque_pendiente(p: Pendiente, ahora: datetime) -> Container:
    """Un pendiente. El contraste visual ES la tesis del proyecto."""
    hechos = [
        Fact(title="Fuente", value=_ETIQUETA_FUENTE[p.fuente]),
        Fact(title="Vence", value=_texto_fecha(p.vence, ahora)),
    ]

    if p.es_inferido:
        hechos.append(Fact(title="Confianza", value=f"{int(p.confianza * 100)}% — inferido"))
        color, estilo = "Warning", "warning"
    else:
        hechos.append(Fact(title="Confianza", value="Confirmado (dato estructurado)"))
        color, estilo = "Good", "good"

    items: list[object] = [
        TextBlock(text=p.titulo, weight="Bolder", size="Medium", wrap=True, color=color),
        FactSet(facts=hechos),
    ]

    if p.contexto:
        items.append(TextBlock(text=p.contexto, wrap=True, is_subtle=True, size="Small"))

    if p.es_inferido:
        items.append(
            TextBlock(
                text="Brújula no confirma este pendiente. Verifícalo en el origen.",
                wrap=True,
                size="Small",
                color="Warning",
            )
        )

    # Trazabilidad toda afirmacion enlaza a su fuente.
    items.append(ActionSet(actions=[OpenUrlAction(title="Ver origen", url=p.url_origen)]))

    return Container(items=items, style=estilo, show_border=True, spacing="Medium")


def _aviso_fuentes_fallidas(agenda: Agenda) -> Container:
    """Declara en la tarjeta lo que Brujula NO pudo consultar.

    Este bloque es la razon de existir del campo `fuentes_fallidas`. Sin el, una agenda
    incompleta se veria identica a una agenda vacia, y
    Brujula estaria mintiendo por omision.
    """
    nombres = ", ".join(f.nombre for f in agenda.fuentes_fallidas)
    return Container(
        items=[
            TextBlock(
                text=f"⚠ No pude consultar: {nombres}",
                weight="Bolder",
                wrap=True,
                color="Attention",
            ),
            TextBlock(
                text=(
                    "Esta lista está incompleta. No significa que no tengas pendientes ahí: "
                    "significa que no pude preguntar."
                ),
                wrap=True,
                size="Small",
                is_subtle=True,
            ),
        ],
        style="attention",
        show_border=True,
        spacing="Medium",
    )


def _encabezado(agenda: Agenda) -> list[object]:
    confirmados = sum(1 for p in agenda.pendientes if not p.es_inferido)
    inferidos = agenda.total - confirmados
    return [
        TextBlock(text="Tu semana", size="Large", weight="Bolder", wrap=True),
        TextBlock(
            text=(
                f"{agenda.total} pendientes — {confirmados} confirmados, "
                f"{inferidos} inferidos de conversaciones"
            ),
            is_subtle=True,
            wrap=True,
            spacing="None",
        ),
    ]


def tarjeta_agenda(agenda: Agenda, ahora: datetime) -> AdaptiveCard:
    """Construye la tarjeta de "¿que tengo esta semana?".

    `ahora` se recibe como parametro y no se lee del reloj, por el mismo
    motivo que en ServicioAgenda: una funcion que consulta el reloj del
    sistema no se puede testear de forma determinista.
    """
    cuerpo: list[object] = _encabezado(agenda)

    if not agenda.esta_completa:
        cuerpo.append(_aviso_fuentes_fallidas(agenda))

    if agenda.total == 0 and agenda.esta_completa:
        cuerpo.append(
            TextBlock(
                text="No tienes pendientes en los próximos 7 días.",
                wrap=True,
                spacing="Medium",
            )
        )

    cuerpo += [_bloque_pendiente(p, ahora) for p in agenda.pendientes]

    cuerpo.append(
        TextBlock(
            text=(
                "Fuentes consultadas: " + (", ".join(agenda.fuentes_consultadas) or "ninguna") + "."
            ),
            size="Small",
            is_subtle=True,
            wrap=True,
            spacing="Large",
        )
    )
    return AdaptiveCard(body=cuerpo)
