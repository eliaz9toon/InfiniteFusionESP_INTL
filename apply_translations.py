#!/usr/bin/env python3

import os
import csv
import glob
import re

# ============================
# RUTAS CONFIGURADAS
# ============================

CSV_FOLDER = r"\ubicaciondel\csvs"
INTL_PATH = r"\ubicaciondel\intl.txt"

# ============================
# Cargar todos los CSV
# ============================

def load_all_csvs(folder):
    mapping = {}

    patterns = [
        "map*.csv", "Map*.csv",
        "Common*.csv",
        "CommonEvents*.csv",
        "CommonEvents：：*.csv",
        "CommonEvents*.*"
    ]

    files = []
    for p in patterns:
        files.extend(glob.glob(os.path.join(folder, p)))

    print(f"CSV detectados: {len(files)}")

    for file in files:
        try:
            with open(file, encoding="utf-8", errors="replace") as f:
                r = csv.reader(f)
                next(r, None)  # Saltar encabezado
                for row in r:
                    if len(row) < 2: 
                        continue
                    # Eliminar espacios extras y comillas dobles
                    original = row[0].strip().strip('"').rstrip()
                    translated = row[1].strip().strip('"')
                    if original not in mapping:
                        mapping[original] = translated
        except Exception as e:
            print(f"Error al leer {file}: {e}")

    print("Entradas totales:", len(mapping))
    return mapping



def apply_translations(intl, mapping):
    with open(intl, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    output = lines[:]

    total_pairs = 0
    applied = 0

    i = 0
    while i < len(lines) - 1:
        l1 = lines[i].rstrip("\n")
        l2 = lines[i+1].rstrip("\n")

        # Saltar comentarios y secciones
        if l1.strip().startswith("#") or re.match(r"^\[.*\]$", l1.strip()):
            i += 1
            continue

        # Solo traduce si es un par duplicado (ignorando espacios al final)
        if l1.strip() == l2.strip():
            total_pairs += 1
            key = l1.strip()
            if key in mapping and mapping[key]:
                output[i+1] = mapping[key] + "\n"
                applied += 1
            i += 2
        else:
            i += 1

    out_path = intl.replace(".txt", "_translated.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(output)

    print("\n✅ Proceso completado")
    print("Pares encontrados:", total_pairs)
    print("Pares traducidos:", applied)
    print("Archivo generado:", out_path)

# ============================

def main():
    print("Cargando CSV...")
    mapping = load_all_csvs(CSV_FOLDER)

    print("\nMappeando...")
    apply_translations(INTL_PATH, mapping)

if __name__ == "__main__":
    main()
