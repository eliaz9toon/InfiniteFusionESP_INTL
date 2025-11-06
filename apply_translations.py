#!/usr/bin/env python3
# Reemplazar traducciones automáticas en intl.txt usando CSVs existentes
# Sobrescribe el intl.txt original

import os
import csv
import glob
import re

# ============================
# RUTAS CONFIGURADAS
# ============================
CSV_FOLDER = r"ubicacion\csvs"
INTL_PATH  = r"ubicacion\intl.txt"

# ============================
# Helpers
# ============================
def normalize_key(s: str) -> str:
    if s is None:
        return ""
    s = s.replace('\r', '').strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1]
    return s.rstrip()

# ============================
# Cargar todos los CSV
# ============================
def load_all_csvs(folder):
    mapping = {}
    patterns = ["map*.csv", "Map*.csv", "Common*.csv", "CommonEvents*.csv", "CommonEvents：：*.csv", "CommonEvents*.*"]
    files = []
    for p in patterns:
        files.extend(glob.glob(os.path.join(folder, p)))

    print(f"CSV detectados: {len(files)}")

    for file in sorted(files):
        try:
            with open(file, encoding="utf-8", errors="replace") as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if len(row) < 2:
                        continue
                    orig = normalize_key(row[0])
                    trans = row[1].replace('\r','').strip()
                    if len(trans) >= 2 and trans[0] == '"' and trans[-1] == '"':
                        trans = trans[1:-1].rstrip()
                    if orig and orig not in mapping:
                        mapping[orig] = trans
        except Exception as e:
            print(f"Error al leer {file}: {e}")

    print("Entradas totales cargadas en mapping:", len(mapping))
    return mapping

# ============================
# Reemplazar traducciones en intl.txt directamente
# ============================
def apply_replacements(intl_path, mapping):
    with open(intl_path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    out_lines = []
    i = 0
    replaced = 0
    scanned_pairs = 0
    not_found = 0

    while i < len(lines):
        line = lines[i]
        key = normalize_key(line.rstrip("\n"))

        if key.startswith("#") or re.match(r"^\[.*\]$", key):
            out_lines.append(line)
            i += 1
            continue

        if i + 1 < len(lines):
            scanned_pairs += 1
            if key in mapping and mapping[key]:
                out_lines.append(lines[i])
                out_lines.append(mapping[key] + "\n")
                replaced += 1
            else:
                out_lines.append(lines[i])
                out_lines.append(lines[i+1])
                not_found += 1
            i += 2
        else:
            out_lines.append(line)
            i += 1

    # Sobrescribir el archivo original
    with open(intl_path, "w", encoding="utf-8") as f:
        f.writelines(out_lines)

    print("\n✅ Proceso completado")
    print(f"Pares escaneados: {scanned_pairs}")
    print(f"Pares reemplazados (usando CSV): {replaced}")
    print(f"Pares no encontrados en CSV (se conservaron): {not_found}")
    print("Archivo original sobrescrito:", intl_path)

# ============================
# Main
# ============================
def main():
    print("Cargando CSV...")
    mapping = load_all_csvs(CSV_FOLDER)
    print("\nAplicando reemplazos en intl.txt ...")
    apply_replacements(INTL_PATH, mapping)

if __name__ == "__main__":
    main()
