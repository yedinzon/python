"""
cleaner.py — Depuración de registros con saltos bruscos.

Algoritmo: recorre de inicio a fin comparando cada valor con el anterior.
Se descartan los registros cuya diferencia absoluta con el anterior sea
mayor o igual a DIFF_THRESHOLD.
"""
import config
from models import ExperimentData


def clean_jumps(values: list[float], threshold: float | None = None) -> list[float]:
    """
    Recorre la serie de inicio a fin y descarta todo registro cuya diferencia
    absoluta con el registro anterior sea >= threshold.
    Retorna una nueva lista sin modificar la original.
    """
    if threshold is None:
        threshold = config.DIFF_THRESHOLD

    if not values:
        return []

    cleaned = [values[0]]
    for current in values[1:]:
        if abs(current - cleaned[-1]) < threshold:
            cleaned.append(current)
    return cleaned


def apply_cleaning(exp: ExperimentData) -> None:
    """
    Aplica la depuración de saltos a un ExperimentData en su lugar.
    También calcula delta_t como último registro − primer registro.
    """
    exp.clean_values = clean_jumps(exp.raw_values)
    if len(exp.clean_values) >= 2:
        exp.delta_t = exp.clean_values[-1] - exp.clean_values[0]
    elif len(exp.clean_values) == 1:
        exp.delta_t = 0.0
    else:
        exp.delta_t = 0.0
