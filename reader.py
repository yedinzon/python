"""
reader.py — Lectura de archivos .xls (formato TSV) y recorrido de carpetas.

Los archivos tienen extensión .xls pero son texto tabulado (TSV):
    Columna 1  No
    Columna 2  Time
    Columna 3  T1/T2
    Columna 4  Value        ← temperatura registrada
    Columna 5  Unit
    Columna 6  Judge
    Columna 7  mAguaInicial ← solo en la primera fila de datos
    Columna 8  mAguaFin
    Columna 9  mButanoInicial
    Columna 10 mButanoFin

Estructura de carpetas esperada:
    <raíz>/
        malla1/
            calentamiento/  exp1.xls  exp2.xls ...
            evaporacion/    exp1.xls  exp2.xls ...
        malla2/
            ...
"""
import csv
import os

import config
from models import ExperimentData, MassData


# ── Conversión de unidades ─────────────────────────────────────────────────────

def grams_to_kg(value: float) -> float:
    """Convierte gramos a kilogramos."""
    return value / 1000.0


# ── Parsing de una fila TSV ───────────────────────────────────────────────────

def _safe_float(row: list[str], col: int) -> float:
    """Extrae un float de la columna `col`; retorna 0.0 si está vacía o no es número."""
    try:
        val = row[col].strip()
        return float(val) if val else 0.0
    except (ValueError, IndexError):
        return 0.0


def _read_tsv(filepath: str) -> list[list[str]]:
    """Lee un archivo TSV (con extensión .xls) y retorna todas las filas como listas de strings."""
    encodings = ("utf-8", "utf-8-sig", "latin-1")
    for enc in encodings:
        try:
            with open(filepath, encoding=enc, newline="") as f:
                return list(csv.reader(f, delimiter="\t"))
        except UnicodeDecodeError:
            continue
    raise ValueError(f"No se pudo decodificar el archivo: {filepath}")


# ── Extracción de masas y valores ─────────────────────────────────────────────

def _find_mass_row(rows: list[list[str]]) -> int:
    """
    Busca la primera fila de datos (post-header) que tenga valor en mAguaInicial.
    Retorna el índice; si no encuentra, retorna 1.
    """
    for i in range(1, len(rows)):
        if len(rows[i]) > config.COL_M_AGUA_INICIAL and rows[i][config.COL_M_AGUA_INICIAL].strip():
            return i
    return 1


def _read_masses(rows: list[list[str]]) -> MassData:
    """Lee las masas de la primera fila que las contiene y las convierte a kg."""
    i = _find_mass_row(rows)
    return MassData(
        m_agua_inicial_kg=grams_to_kg(_safe_float(rows[i], config.COL_M_AGUA_INICIAL)),
        m_agua_fin_kg=grams_to_kg(_safe_float(rows[i], config.COL_M_AGUA_FIN)),
        m_butano_inicial_kg=grams_to_kg(_safe_float(rows[i], config.COL_M_BUTANO_INICIAL)),
        m_butano_fin_kg=grams_to_kg(_safe_float(rows[i], config.COL_M_BUTANO_FIN)),
    )


def _read_value_column(rows: list[list[str]]) -> list[float]:
    """Lee todos los valores numéricos válidos de la columna Value (col índice 3)."""
    values: list[float] = []
    for row in rows[1:]:                       # saltar header
        if len(row) <= config.COL_VALUE:
            continue
        raw = row[config.COL_VALUE].strip()
        if not raw:
            continue
        try:
            values.append(float(raw))
        except ValueError:
            continue
    return values


# ── Lectura de un archivo de experimento ─────────────────────────────────────

def read_experiment_file(
    filepath: str, malla: str, tipo: str
) -> ExperimentData | None:
    """
    Parsea un archivo TSV/.xls y construye un ExperimentData.
    Retorna None si el archivo no puede leerse o está vacío.
    """
    try:
        rows = _read_tsv(filepath)

        if len(rows) < 2:
            print(f"    [!] Archivo vacío o sin datos: {os.path.basename(filepath)}")
            return None

        raw_values = _read_value_column(rows)
        if not raw_values:
            print(f"    [!] Sin valores en columna Value: {os.path.basename(filepath)}")
            return None

        masses = _read_masses(rows)
        nombre = os.path.splitext(os.path.basename(filepath))[0]

        return ExperimentData(
            malla=malla,
            tipo=tipo,
            nombre=nombre,
            raw_values=raw_values,
            clean_values=[],   # se rellena en cleaner.py
            masses=masses,
        )

    except Exception as exc:
        print(f"    [!] Error leyendo '{os.path.basename(filepath)}': {exc}")
        return None


# ── Recorrido de la estructura de carpetas ────────────────────────────────────

def _sorted_xls_files(directory: str) -> list[str]:
    """Devuelve los archivos .xls de un directorio ordenados alfabéticamente."""
    return sorted(
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith(".xls")
        and os.path.isfile(os.path.join(directory, f))
    )


def load_all_experiments(root_path: str) -> list[ExperimentData]:
    """
    Recorre raíz/mallaN/tipo/expN.xls y retorna todos los ExperimentData encontrados.
    """
    experiments: list[ExperimentData] = []

    if not os.path.isdir(root_path):
        print(f"  [!] La ruta no existe: {root_path}")
        return experiments

    malla_dirs = sorted(
        entry for entry in os.listdir(root_path)
        if entry.lower().startswith("malla")
        and os.path.isdir(os.path.join(root_path, entry))
    )

    if not malla_dirs:
        print("  [!] No se encontraron carpetas con nombre 'mallaN'.")
        return experiments

    for malla in malla_dirs:
        malla_path = os.path.join(root_path, malla)
        print(f"  → {malla}")

        for tipo in config.EXPERIMENT_TYPES:
            tipo_path = os.path.join(malla_path, tipo)
            if not os.path.isdir(tipo_path):
                continue

            files = _sorted_xls_files(tipo_path)
            print(f"      [{tipo}]  {len(files)} archivo(s)")

            for filepath in files:
                exp = read_experiment_file(filepath, malla, tipo)
                if exp is not None:
                    experiments.append(exp)

    return experiments
