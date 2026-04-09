"""
cleaner.py — Depuración de la cola de registros ruidosos.

Algoritmo: recorre de atrás hacia adelante comparando cada valor con el anterior.
Si la diferencia supera el umbral configurado, elimina ese registro final y repite;
se detiene en cuanto la diferencia entre los dos últimos es aceptable.
"""
import config
from models import ExperimentData


def clean_tail(values: list[float], threshold: float | None = None) -> list[float]:
    """
    Elimina registros del final de la serie cuyos saltos consecutivos
    superen `threshold`.  Retorna una nueva lista sin modificar la original.
    """
    if threshold is None:
        threshold = config.DIFF_THRESHOLD

    cleaned = list(values)
    while len(cleaned) >= 2:
        if abs(cleaned[-1] - cleaned[-2]) >= threshold:
            cleaned.pop()
        else:
            break
    return cleaned


def apply_cleaning(exp: ExperimentData) -> None:
    """
    Aplica la depuración de cola a un ExperimentData en su lugar.
    También calcula delta_t (max − min) sobre los valores limpios.
    """
    exp.clean_values = clean_tail(exp.raw_values)
    if exp.clean_values:
        exp.delta_t = max(exp.clean_values) - min(exp.clean_values)
    else:
        exp.delta_t = 0.0
