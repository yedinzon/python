"""
display.py — Funciones de presentación por consola.
"""
import math
import config
from models import ExperimentData

# ── Helpers de formato ────────────────────────────────────────────────────────

WIDTH = 88

def _sep(char: str = "═", width: int = WIDTH) -> str:
    return char * width

def _fmt(value: float | None, decimals: int = 4) -> str:
    """Formatea un float; muestra 'N/A' si es None o NaN."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "N/A"
    return f"{value:.{decimals}f}"

def _header(title: str) -> None:
    print()
    print(_sep())
    print(f"  {title}")
    print(_sep())

def _subheader(title: str) -> None:
    print()
    print(f"  ── {title} " + "─" * (WIDTH - len(title) - 6))


# ── Visualización de resultados ───────────────────────────────────────────────

_COL_HEADER = (
    f"  {'#':>3}  {'Experimento':<8}  {'Tipo':<15}  "
    f"{'ΔT (°C)':>8}  {'Puntos':>11}  {'η (%)':>10}  {'Masas (g)'}"
)

def _experiment_row(idx: int, exp: ExperimentData) -> None:
    """Imprime una fila de resultado para un experimento."""
    pts = f"{len(exp.clean_values)}/{len(exp.raw_values)}"
    dep = f"  (-{exp.registros_depurados})" if exp.registros_depurados else ""
    print(
        f"  {idx:>3}. {exp.nombre:<8}  {exp.tipo:<15}  "
        f"{_fmt(exp.delta_t, 2):>8}  {pts:>9}{dep:<6}  "
        f"{_fmt(exp.eficiencia, 2):>10}  {exp.masses}"
    )


def display_results(experiments: list[ExperimentData]) -> None:
    """Muestra todos los resultados agrupados por malla."""
    if not experiments:
        print("  Sin datos para mostrar.")
        return

    _header("RESULTADOS DE EFICIENCIA POR MALLA")

    mallas = sorted(set(e.malla for e in experiments))
    for malla in mallas:
        _subheader(malla.upper())
        print(_COL_HEADER)
        print("  " + "─" * (WIDTH - 2))

        malla_exps = [e for e in experiments if e.malla == malla]
        for i, exp in enumerate(malla_exps, 1):
            _experiment_row(i, exp)

    print()


# ── Visualización de configuración ────────────────────────────────────────────

def display_config() -> None:
    """Muestra los parámetros globales actuales."""
    _header("CONFIGURACIÓN GLOBAL")
    rows = [
        ("Masa de la olla",         f"{config.MASA_OLLA_G} g  →  {config.MASA_OLLA_G/1000:.6f} kg"),
        ("Cp  calor específico",    f"{config.CP} kJ/(kg·K)"),
        ("Hv  entalpía evap.",      f"{config.HV} kJ/kg"),
        ("PCI poder calorífico",    f"{config.PCI} kJ/kg"),
        ("Intervalo de tiempo",     f"{config.DELTA_T_INTERVAL} s"),
        ("Umbral de depuración",    f"{config.DIFF_THRESHOLD} °C"),
    ]
    for label, value in rows:
        print(f"  {label:<25}:  {value}")
    print()
