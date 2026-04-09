"""
menu.py — Menú interactivo por consola y lógica de cada opción.
El estado de la sesión (lista de experimentos cargados) vive aquí.
"""
import csv
import sys

import config
from cleaner import apply_cleaning
from display import display_config, display_results
from efficiency import apply_eficiencias
from models import ExperimentData
from reader import load_all_experiments

# ── Estado de sesión ──────────────────────────────────────────────────────────

_experiments: list[ExperimentData] = []


def _require_data() -> bool:
    """Verifica que haya datos cargados; muestra advertencia si no."""
    if not _experiments:
        print("  [!] No hay datos cargados. Use la opción '1. Leer archivos' primero.")
        return False
    return True


# ── Acciones del menú ─────────────────────────────────────────────────────────

def _action_load() -> None:
    """Solicita la ruta raíz, carga, depura y calcula eficiencias."""
    global _experiments

    ruta = input("  Ruta de la carpeta principal: ").strip()
    if not ruta:
        print("  [!] Ruta vacía. Operación cancelada.")
        return

    print(f"\n  Buscando experimentos en: {ruta}")
    experiments = load_all_experiments(ruta)

    if not experiments:
        print("  [!] No se encontraron experimentos válidos.")
        return

    print(f"\n  Depurando datos ({len(experiments)} archivos)...")
    for exp in experiments:
        apply_cleaning(exp)

    print("  Calculando eficiencias...")
    apply_eficiencias(experiments)

    _experiments = experiments
    print(f"\n  [✓] {len(_experiments)} experimento(s) cargado(s) correctamente.")


def _action_show_results() -> None:
    """Muestra la tabla de resultados en consola."""
    if _require_data():
        display_results(_experiments)


def _action_plot() -> None:
    """Genera las gráficas de temperatura vs tiempo por malla."""
    if not _require_data():
        return
    try:
        from plotter import plot_all_mallas
        plot_all_mallas(_experiments)
    except ImportError:
        print("  [!] matplotlib no está instalado.")
        print("      Instale con:  pip install matplotlib")


def _action_export_csv() -> None:
    """Exporta los resultados a un archivo CSV."""
    if not _require_data():
        return

    dest = input("  Ruta de destino (Enter = resultados.csv): ").strip() or "resultados.csv"
    try:
        with open(dest, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Malla", "Tipo", "Experimento",
                "Delta_T_C", "Puntos_raw", "Puntos_limpios",
                "mAguaInicial_kg", "mAguaFin_kg",
                "mButanoInicial_kg", "mButanoFin_kg",
                "Eficiencia_%",
            ])
            for e in _experiments:
                writer.writerow([
                    e.malla, e.tipo, e.nombre,
                    f"{e.delta_t:.4f}",
                    len(e.raw_values), len(e.clean_values),
                    f"{e.masses.m_agua_inicial_kg:.6f}",
                    f"{e.masses.m_agua_fin_kg:.6f}",
                    f"{e.masses.m_butano_inicial_kg:.6f}",
                    f"{e.masses.m_butano_fin_kg:.6f}",
                    f"{e.eficiencia:.4f}" if e.eficiencia is not None else "N/A",
                ])
        print(f"  [✓] Resultados exportados a: {dest}")
    except Exception as exc:
        print(f"  [!] Error al exportar: {exc}")


def _action_config() -> None:
    """Permite editar los parámetros globales uno a uno."""
    display_config()

    options: dict[str, tuple[str, str]] = {
        "1": ("Masa de la olla (g)",        "MASA_OLLA_G"),
        "2": ("Cp  [kJ/(kg·K)]",            "CP"),
        "3": ("Hv  [kJ/kg]",                "HV"),
        "4": ("PCI [kJ/kg]",               "PCI"),
        "5": ("Intervalo de tiempo (s)",    "DELTA_T_INTERVAL"),
        "6": ("Umbral de depuración (°C)",  "DIFF_THRESHOLD"),
    }

    for key, (label, _) in options.items():
        print(f"  {key}. {label}")
    print("  0. Volver")

    choice = input("\n  Parámetro a editar: ").strip()
    if choice == "0" or choice not in options:
        return

    label, attr = options[choice]
    current = getattr(config, attr)
    raw = input(f"  Nuevo valor para '{label}' [{current}]: ").strip()
    if not raw:
        return
    try:
        setattr(config, attr, float(raw))
        print(f"  [✓] '{label}' actualizado a {getattr(config, attr)}")
        if attr == "MASA_OLLA_G":
            print(f"      ({config.MASA_OLLA_G/1000:.6f} kg)")
        if _experiments:
            print("  [i] Recalculando eficiencias con los nuevos valores...")
            apply_eficiencias(_experiments)
            print("  [✓] Eficiencias actualizadas.")
    except ValueError:
        print("  [!] Valor inválido. No se realizaron cambios.")


# ── Definición del menú ───────────────────────────────────────────────────────

_MENU: list[tuple[str, str, object]] = [
    ("1", "Leer archivos",       _action_load),
    ("2", "Mostrar resultados",  _action_show_results),
    ("3", "Generar gráficas",    _action_plot),
    ("4", "Exportar CSV",        _action_export_csv),
    ("5", "Configuración",       _action_config),
    ("0", "Salir",               None),
]


def _print_menu() -> None:
    """Imprime el menú principal."""
    print()
    print("═" * 50)
    print("  ANALIZADOR DE EFICIENCIA DE EXPERIMENTOS")
    n = len(_experiments)
    estado = f"  {n} experimento(s) cargado(s)" if n else "  Sin datos cargados"
    print(f"  {estado}")
    print("═" * 50)
    for key, label, _ in _MENU:
        print(f"  {key}.  {label}")
    print("─" * 50)


def run() -> None:
    """Bucle principal del menú interactivo."""
    actions = {key: fn for key, _, fn in _MENU}

    while True:
        _print_menu()
        choice = input("  Opción: ").strip()
        print()

        if choice == "0":
            print("  Hasta luego.\n")
            sys.exit(0)

        action = actions.get(choice)
        if action is None:
            print("  [!] Opción inválida.")
        else:
            action()
