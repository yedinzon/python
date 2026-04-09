"""
models.py — Modelos de datos para el analizador de experimentos.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MassData:
    """Masas de agua y butano de un experimento, almacenadas en kg."""
    m_agua_inicial_kg: float
    m_agua_fin_kg: float
    m_butano_inicial_kg: float
    m_butano_fin_kg: float

    def __str__(self) -> str:
        return (
            f"mAguaIni={self.m_agua_inicial_kg*1000:.2f}g  "
            f"mAguaFin={self.m_agua_fin_kg*1000:.2f}g  "
            f"mButIni={self.m_butano_inicial_kg*1000:.2f}g  "
            f"mButFin={self.m_butano_fin_kg*1000:.2f}g"
        )


@dataclass
class ExperimentData:
    """Datos completos de un archivo de experimento individual."""
    malla: str                          # p.e. "malla1"
    tipo: str                           # "calentamiento" | "evaporacion"
    nombre: str                         # p.e. "exp1"
    raw_values: list[float]             # valores originales de la columna Value
    clean_values: list[float]           # valores tras depuración de cola
    masses: MassData                    # masas en kg
    delta_t: float = 0.0                # max(clean_values) - min(clean_values)
    eficiencia: Optional[float] = None  # resultado del cálculo [%]

    # ── propiedades de conveniencia ──────────────────────────────────────────

    @property
    def label(self) -> str:
        """Etiqueta legible: malla/tipo/nombre."""
        return f"{self.malla}/{self.tipo}/{self.nombre}"

    @property
    def registros_depurados(self) -> int:
        """Cantidad de registros eliminados en la depuración."""
        return len(self.raw_values) - len(self.clean_values)
