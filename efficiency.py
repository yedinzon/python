"""
efficiency.py — Cálculo de eficiencia térmica para cada tipo de experimento.

Fórmulas:
  Calentamiento:
    η = [ (mAguaInicial − mOlla) · Cp · ΔT  +  (mAguaInicial - mAguaFin) · Hv ] · 100
        ─────────────────────────────────────────────────────────────────────────────
                         (mButanoInicial - mButanoFin) · PCI

  Evaporación:
    η = (mAguaInicial - mAguaFin) · Hv · 100
        ────────────────────────────────────────
        (mButanoInicial - mButanoFin) · PCI

Todas las masas están en kg y los coeficientes en kJ/kg → resultado en %.
"""
import math

import config
from models import ExperimentData, MassData


def _safe_div(numerator: float, denominator: float) -> float:
    """División segura: retorna NaN si el denominador es cero."""
    if denominator == 0.0:
        return float("nan")
    return numerator / denominator


def calc_calentamiento(masses: MassData, delta_t: float) -> float:
    """
    Eficiencia de calentamiento.
    masa_olla se lee de config.MASA_OLLA_G y se convierte a kg aquí.
    """
    masa_olla_kg = config.MASA_OLLA_G / 1000.0
    numerator = (
        (masses.m_agua_inicial_kg - masa_olla_kg) * config.CP * delta_t
        + (masses.m_agua_inicial_kg - masses.m_agua_fin_kg) * config.HV
    ) * 100.0
    denominator = (masses.m_butano_inicial_kg - masses.m_butano_fin_kg) * config.PCI
    return _safe_div(numerator, denominator)


def calc_evaporacion(masses: MassData) -> float:
    """Eficiencia de evaporación."""
    numerator = (masses.m_agua_inicial_kg - masses.m_agua_fin_kg) * config.HV * 100.0
    denominator = (masses.m_butano_inicial_kg - masses.m_butano_fin_kg) * config.PCI
    return _safe_div(numerator, denominator)


def calculate_eficiencia(exp: ExperimentData) -> float:
    """Despacha la fórmula correcta según el tipo del experimento."""
    if exp.tipo == config.FOLDER_CALENTAMIENTO:
        return calc_calentamiento(exp.masses, exp.delta_t)
    if exp.tipo == config.FOLDER_EVAPORACION:
        return calc_evaporacion(exp.masses)
    raise ValueError(f"Tipo de experimento desconocido: '{exp.tipo}'")


def apply_eficiencias(experiments: list[ExperimentData]) -> None:
    """Calcula y asigna la eficiencia a cada experimento de la lista."""
    for exp in experiments:
        exp.eficiencia = calculate_eficiencia(exp)
