"""
plotter.py — Gráficas temperatura vs tiempo por malla.

Cada figura tiene dos subplots apilados verticalmente:
  - Superior: todos los experimentos de calentamiento (tonos rojos)
  - Inferior: todos los experimentos de evaporación   (tonos azules)
"""
import math
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import config
from models import ExperimentData


# ── Paletas de color ──────────────────────────────────────────────────────────

def _palette(n: int, cmap_name: str) -> list:
    """Genera n colores distintos del colormap, evitando los extremos muy claros."""
    cmap = plt.get_cmap(cmap_name)
    return [cmap(0.35 + 0.55 * i / max(n - 1, 1)) for i in range(n)]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _tiempo(exp: ExperimentData) -> list[float]:
    """Eje de tiempo en segundos según el intervalo configurado."""
    return [i * config.DELTA_T_INTERVAL for i in range(len(exp.clean_values))]


def _legend_label(exp: ExperimentData) -> str:
    """Etiqueta de leyenda: nombre + eficiencia si está disponible."""
    if exp.eficiencia is None or math.isnan(exp.eficiencia):
        return exp.nombre
    return f"{exp.nombre}  (η = {exp.eficiencia:.2f} %)"


def _draw_series(ax: plt.Axes, experiments: list[ExperimentData],
                 cmap_name: str, linestyle: str, title: str) -> None:
    """
    Dibuja todas las series de una lista en el eje dado.
    Muestra un mensaje si no hay experimentos del tipo solicitado.
    """
    ax.set_title(title, fontsize=11, fontweight="bold", loc="left", pad=6)
    ax.set_xlabel("Tiempo (s)", fontsize=9)
    ax.set_ylabel("Temperatura (°C)", fontsize=9)
    ax.grid(True, alpha=0.3)

    if not experiments:
        ax.text(0.5, 0.5, "Sin datos", transform=ax.transAxes,
                ha="center", va="center", fontsize=10, color="gray")
        return

    colors = _palette(len(experiments), cmap_name)
    for exp, color in zip(experiments, colors):
        ax.plot(_tiempo(exp), exp.clean_values,
                color=color, linewidth=1.8, linestyle=linestyle,
                label=_legend_label(exp))

    ax.legend(fontsize=8, loc="best", framealpha=0.7)


# ── Figura por malla ──────────────────────────────────────────────────────────

def plot_malla(malla: str, experiments: list[ExperimentData]) -> None:
    """
    Genera una figura con dos subplots para una malla:
      - Arriba  → Calentamiento (línea continua, rojos)
      - Abajo   → Evaporación   (línea discontinua, azules)
    """
    cal = [e for e in experiments if e.tipo == config.FOLDER_CALENTAMIENTO]
    eva = [e for e in experiments if e.tipo == config.FOLDER_EVAPORACION]

    fig = plt.figure(figsize=(13, 9))
    fig.suptitle(f"Temperatura vs Tiempo  —  {malla.upper()}",
                 fontsize=13, fontweight="bold", y=0.98)

    gs = gridspec.GridSpec(2, 1, figure=fig, hspace=0.42)

    ax_cal = fig.add_subplot(gs[0])
    ax_eva = fig.add_subplot(gs[1])

    _draw_series(ax_cal, cal, cmap_name="Reds",  linestyle="-",
                 title="Calentamiento")
    _draw_series(ax_eva, eva, cmap_name="Blues", linestyle="--",
                 title="Evaporación")

    fig.tight_layout(rect=[0, 0, 1, 0.97])
    plt.show()


# ── Iterador sobre todas las mallas ──────────────────────────────────────────

def plot_all_mallas(experiments: list[ExperimentData]) -> None:
    """Genera una figura independiente por cada malla detectada."""
    mallas = sorted(set(e.malla for e in experiments))
    if not mallas:
        print("  [!] No hay datos cargados para graficar.")
        return
    for malla in mallas:
        plot_malla(malla, [e for e in experiments if e.malla == malla])
