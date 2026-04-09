"""
config.py — Parámetros globales y constantes físicas del analizador.
Todos los valores configurables por el usuario se centralizan aquí.
"""

# ── Constantes físicas ─────────────────────────────────────────────────────────
CP: float = 4.18        # Calor específico del agua       [kJ / (kg·K)]
HV: float = 2250.0      # Entalpía de evaporación del agua [kJ / kg]
PCI: float = 44700.0    # Poder calorífico inferior butano [kJ / kg]

# ── Parámetros editables por el usuario ──────────────────────────────────────
MASA_OLLA_G: float = 200.0    # Masa de la olla en gramos (convertida a kg en runtime)
DELTA_T_INTERVAL: float = 1.0   # Intervalo de tiempo entre registros [s]
DIFF_THRESHOLD: float = 5.0     # Umbral de diferencia para depuración de cola [°C]

# ── Índices de columnas en el archivo .xls (base 0) ───────────────────────────
COL_VALUE: int = 3              # Columna 4  → temperatura/valor de experimento
COL_M_AGUA_INICIAL: int = 6     # Columna 7  → masa agua inicial  [g]
COL_M_AGUA_FIN: int = 7         # Columna 8  → masa agua final     [g]
COL_M_BUTANO_INICIAL: int = 8   # Columna 9  → masa butano inicial [g]
COL_M_BUTANO_FIN: int = 9       # Columna 10 → masa butano final   [g]

# ── Nombres de carpetas de tipo de experimento ────────────────────────────────
FOLDER_CALENTAMIENTO: str = "calentamiento"
FOLDER_EVAPORACION: str = "evaporacion"
EXPERIMENT_TYPES: tuple[str, ...] = (FOLDER_CALENTAMIENTO, FOLDER_EVAPORACION)
