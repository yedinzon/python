"""
main.py — Punto de entrada del Analizador de Eficiencia de Experimentos.

Uso:
    python main.py

Dependencias:
    pip install -r requirements.txt
"""
import sys

# Forzar UTF-8 en la consola de Windows para soportar caracteres especiales.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from menu import run

if __name__ == "__main__":
    run()
