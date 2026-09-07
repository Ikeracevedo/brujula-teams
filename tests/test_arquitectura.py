

from __future__ import annotations

import ast
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
STDLIB = set(sys.stdlib_module_names)


def _arbol(archivo: Path) -> ast.Module:
    return ast.parse(archivo.read_text(encoding="utf-8"), filename=str(archivo))


def _modulos_raiz(archivo: Path) -> set[str]:
    """Primer segmento de cada modulo importado. 'fastapi.responses' -> 'fastapi'."""
    modulos: set[str] = set()
    for nodo in ast.walk(_arbol(archivo)):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                modulos.add(alias.name.split(".")[0])
        elif isinstance(nodo, ast.ImportFrom) and nodo.level == 0 and nodo.module:
            modulos.add(nodo.module.split(".")[0])
    return modulos


def _imports_internos(archivo: Path) -> set[str]:
    """Modulos 'app.*' importados, con su ruta completa."""
    internos: set[str] = set()
    for nodo in ast.walk(_arbol(archivo)):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                if alias.name.startswith("app."):
                    internos.add(alias.name)
        elif (
            isinstance(nodo, ast.ImportFrom)
            and nodo.level == 0
            and nodo.module is not None
            and nodo.module.startswith("app.")
        ):
            internos.add(nodo.module)
    return internos


def _archivos_de(paquete: str) -> list[Path]:
    return sorted((RAIZ / "app" / paquete).rglob("*.py"))


def test_hay_archivos_que_revisar() -> None:
    """Guardia: sin esto, un renombre de carpeta dejaria todos los
    demas tests iterando sobre listas vacias y pasando en verde."""
    assert _archivos_de("dominio"), "No se encontraron archivos en app/dominio"
    assert _archivos_de("puertos"), "No se encontraron archivos en app/puertos"
    assert _archivos_de("servicios"), "No se encontraron archivos en app/servicios"


def test_dominio_solo_importa_libreria_estandar() -> None:
    """REGLA DE ORO (ADR-004): el dominio no conoce a nadie."""
    for archivo in _archivos_de("dominio"):
        for modulo in _modulos_raiz(archivo):
            permitido = modulo in STDLIB or modulo == "app"
            assert permitido, (
                f"{archivo.relative_to(RAIZ)} importa '{modulo}', que no es "
                f"libreria estandar. app/dominio/ no puede depender de nada externo."
            )


def test_dominio_no_importa_otras_capas() -> None:
    """Dentro de app, el dominio solo puede importar app.dominio."""
    for archivo in _archivos_de("dominio"):
        for modulo in _imports_internos(archivo):
            assert modulo.startswith("app.dominio"), (
                f"{archivo.relative_to(RAIZ)} importa '{modulo}'. "
                f"El dominio no puede depender de otras capas."
            )


def test_puertos_solo_conoce_el_dominio() -> None:
    """Los puertos son contratos: stdlib + app.dominio, nada mas."""
    for archivo in _archivos_de("puertos"):
        for modulo in _imports_internos(archivo):
            assert modulo.startswith("app.dominio"), (
                f"{archivo.relative_to(RAIZ)} importa '{modulo}'. "
                f"Un puerto solo puede conocer el dominio."
            )


def test_servicios_no_conoce_adaptadores_ni_api() -> None:
    """Los casos de uso dependen de PUERTOS, nunca de implementaciones.

    Es la D de SOLID (inversion de dependencias) verificada por una
    maquina en vez de por la buena voluntad del programador.
    """
    prohibidos = ("app.adaptadores", "app.api")
    for archivo in _archivos_de("servicios"):
        for modulo in _imports_internos(archivo):
            assert not modulo.startswith(prohibidos), (
                f"{archivo.relative_to(RAIZ)} importa '{modulo}'. "
                f"Un servicio depende de puertos, no de implementaciones."
            )


def test_servicios_no_importa_frameworks_web() -> None:
    """Un caso de uso no sabe que existe FastAPI."""
    prohibidos = {"fastapi", "starlette", "uvicorn", "pymongo", "httpx"}
    for archivo in _archivos_de("servicios"):
        contaminantes = _modulos_raiz(archivo) & prohibidos
        assert not contaminantes, (
            f"{archivo.relative_to(RAIZ)} importa {contaminantes}. "
            f"servicios/ debe ser testeable sin red ni servidor."
        )
