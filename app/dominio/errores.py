from __future__ import annotations


class BrujulaError(Exception):
    """
    Raiz de todos los errores propios

    Permite capturar el dominio entero sin arapar por accidente
    ValueError o KeyError ajeno, que son bugs y deben explotar
    """


class FuenteNoDisponibleError(BrujulaError):
    """
    Una fuente no pudo ser consultada. NO significa 'sin pendientes'.
    """

    def __init__(self, nombre_fuente: str, motivo: str) -> None:
        # Se guardan como atributis no solo dentro del texto del mensaje
        # El servicio los lee para construir FuenteFallida
        self.nombre_fuente = nombre_fuente
        self.motivo = motivo
        super().__init__(f"No se pudo consultar '{nombre_fuente}': {motivo}")


class ConfiguracionInvalidaError(BrujulaError):
    """Falta una variable de entorno obligatoria o tiene un valor imposible."""
