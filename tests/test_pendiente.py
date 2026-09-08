from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta

import pytest

from app.dominio.pendiente import FuentePendiente, Pendiente

AHORA = datetime(2026, 9, 7, 10, 0, 0)


def _pendiente_valido(**cambios: object) -> Pendiente:
    base: dict[str, object] = {
        "id": "p-1",
        "titulo": "Entregar informe",
        "fuente": FuentePendiente.PLANNER,
        "url_origen": "https://teams.microsoft.com/l/entity/x",
        "vence": AHORA + timedelta(days=1),
        "confianza": 1.0,
    }
    base.update(cambios)
    return Pendiente(**base)  # type: ignore[arg-type]


# --- Camino feliz -----------------------------------------------------


def test_construye_un_pendiente_valido() -> None:
    p = _pendiente_valido()
    assert p.titulo == "Entregar informe"
    assert p.fuente is FuentePendiente.PLANNER


def test_pendiente_estructurado_no_es_inferido() -> None:
    assert _pendiente_valido(confianza=1.0).es_inferido is False


def test_pendiente_de_baja_confianza_es_inferido() -> None:
    assert _pendiente_valido(confianza=0.72).es_inferido is True


# --- Invariantes: casos de error --------------------------------------


def test_rechaza_titulo_vacio() -> None:
    with pytest.raises(ValueError, match="titulo"):
        _pendiente_valido(titulo="   ")


def test_rechaza_url_origen_vacia() -> None:
    """Trazabilidad obligatoria: sin origen no hay Pendiente."""
    with pytest.raises(ValueError, match="url_origen"):
        _pendiente_valido(url_origen="")


def test_rechaza_confianza_fuera_de_rango() -> None:
    with pytest.raises(ValueError, match="confianza"):
        _pendiente_valido(confianza=1.5)
    with pytest.raises(ValueError, match="confianza"):
        _pendiente_valido(confianza=-0.1)


def test_rechaza_contexto_vacio_cuando_se_proporciona() -> None:
    """Regla tuya, no del contrato original: si hay contexto, que no
    sea basura en blanco. La agregamos porque es una regla real y
    una regla sin test es una regla que cualquiera puede borrar sin
    que nadie se entere."""
    with pytest.raises(ValueError, match="contexto"):
        _pendiente_valido(contexto="   ")


# --- Casos borde ------------------------------------------------------


def test_acepta_pendiente_sin_fecha_de_vencimiento() -> None:
    """Una tarea de To Do sin fecha es valida."""
    assert _pendiente_valido(vence=None).vence is None


def test_confianza_en_los_limites_exactos() -> None:
    assert _pendiente_valido(confianza=0.0).confianza == 0.0
    assert _pendiente_valido(confianza=1.0).confianza == 1.0


def test_es_inmutable() -> None:
    """frozen=True: un Pendiente es un value object, no se muta.
    Se espera FrozenInstanceError concreto, no un Exception generico:
    pytest.raises(Exception) pasaria tambien si el objeto explotara
    por un motivo distinto al que el test dice estar probando."""
    p = _pendiente_valido()
    with pytest.raises(FrozenInstanceError):
        p.titulo = "otro"  # type: ignore[misc]
