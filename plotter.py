"""
plotter.py — Generación de gráficas temperatura vs tiempo por malla.

Convención de colores:
  Calentamiento → tonos rojos/naranjas (colormap Reds)
  Evaporación   → tonos azules/cianes  (colormap Blues)
"""
import math
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

import config
from models import ExperimentData


# ── Paletas ───────────────────────────────────────────────────────────────────

def _palette(n: int, cmap_name: str) -> list:
    """Genera n colores distintos del colormap dado, evitando los extremos."""
    cmap = plt.get_cmap(cmap_name)
    return [cmap(0.35 + 0.60 * i / max(n - 1, 1)) for i in range(n)]


# ── Gráfica de una sola malla ─────────────────────────────────────────────────

def _efic_label(exp: ExperimentData) -> str:
    """Texto breve para la leyenda: nombre + eficiencia."""
    if exp.eficiencia is None or math.isnan(exp.eficiencia):
        return exp.nombre
    return f"{exp.nombre}  η={exp.eficiencia:.1f}%"


def plot_malla(malla: str, experiments: list[ExperimentData]) -> None:
    """
    Genera una figura con todas las series de temperatura de una malla.
    Calentamiento: línea continua roja. Evaporación: línea discontinua azul.
    """
    cal = [e for e in experiments if e.tipo == config.FOLDER_CALENTAMIENTO]
    eva = [e for e in experiments if e.tipo == config.FOLDER_EVAPORACION]

    if not cal and not eva:
        print(f"  [!] Sin experimentos para graficar en {malla}.")
        return

    cal_colors = _palette(len(cal), "Reds")
    eva_colors = _palette(len(eva), "Blues")

    fig, ax = plt.subplots(figsize=(13, 6))
    fig.suptitle(f"Temperatura vs Tiempo — {malla.upper()}", fontsize=14, fontweight="bold")

    # ── Series de calentamiento ───────────────────────────────────────────────
    for exp, color in zip(cal, cal_colors):
        t = [i * config.DELTA_T_INTERVAL for i in range(len(exp.clean_values))]
        ax.plot(t, exp.clean_values,
                color=color, linewidth=1.8, linestyle="-",
                label=_efic_label(exp))

    # ── Series de evaporación ─────────────────────────────────────────────────
    for exp, color in zip(eva, eva_colors):
        t = [i * config.DELTA_T_INTERVAL for i in range(len(exp.clean_values))]
        ax.plot(t, exp.clean_values,
                color=color, linewidth=1.8, linestyle="--",
                label=_efic_label(exp))

    # ── Leyenda con indicadores de tipo ──────────────────────────────────────
    cal_proxy = mlines.Line2D([], [], color="tomato",    linewidth=2, linestyle="-",  label="Calentamiento")
    eva_proxy = mlines.Line2D([], [], color="steelblue", linewidth=2, linestyle="--", label="Evaporación")
    type_legend = ax.legend(handles=[cal_proxy, eva_proxy],
                            loc="upper left", fontsize=9, title="Tipo")
    ax.add_artist(type_legend)
    ax.legend(loc="upper right", fontsize=8, title="Experimentos")

    ax.set_xlabel("Tiempo (s)", fontsize=11)
    ax.set_ylabel("Temperatura (°C)", fontsize=11)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    plt.show()


# ── Iterador sobre todas las mallas ──────────────────────────────────────────

def plot_all_mallas(experiments: list[ExperimentData]) -> None:
    """Genera una gráfica independiente por cada malla detectada."""
    mallas = sorted(set(e.malla for e in experiments))
    if not mallas:
        print("  [!] No hay datos cargados para graficar.")
        return
    for malla in mallas:
        plot_malla(malla, [e for e in experiments if e.malla == malla])
