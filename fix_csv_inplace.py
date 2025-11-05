#!/usr/bin/env python3
# fix_csv_unify_lines_no_bak.py
# Une físicamente las líneas partidas dentro de campos entre comillas,
# dejando todo lo demás intacto. NO inserta '\n' donde no existía.
# No crea backups (sobrescribe los CSV directamente).

import os
import glob
import time
import re

# Ajusta aquí si tu carpeta está en otro lugar
CSV_FOLDER = r"ubicaciondel\csvs"
ENCODING = "utf-8"


def line_has_unbalanced_quotes(s: str) -> bool:
    """Devuelve True si la línea tiene un número impar de comillas dobles -> empieza/continúa campo abierto."""
    return s.count('"') % 2 == 1


# ================================================================
# ✅ NUEVO: limpieza inteligente de espacios en campos entre comillas
# ================================================================
def normalize_joined_spaces(s: str) -> str:
    """
    Limpia espacios duplicados SOLO dentro de comillas (campo CSV),
    sin tocar comandos \n, \t, \V[], \C[], etc.
    """
    if not s.startswith('"'):
        return s

    # Separar campos CSV correctamente
    parts = []
    current = []
    in_quotes = False
    i = 0

    while i < len(s):
        c = s[i]

        # Comillas escapadas ("")
        if c == '"' and i + 1 < len(s) and s[i + 1] == '"':
            current.append('""')
            i += 2
            continue

        if c == '"':
            in_quotes = not in_quotes
            current.append(c)
        elif c == ',' and not in_quotes:
            parts.append(''.join(current))
            current = []
        else:
            current.append(c)

        i += 1

    parts.append(''.join(current))

    cleaned_parts = []
    for p in parts:
        # Campo entre comillas
        if p.startswith('"') and p.endswith('"'):
            inner = p[1:-1]

            # ✅ Colapsar múltiples espacios normales (NO rompe secuencias \n, \t, \V[], etc.)
            inner = re.sub(r'(?<!\\) {2,}', ' ', inner)

            cleaned_parts.append(f'"{inner}"')
        else:
            cleaned_parts.append(p)

    return ",".join(cleaned_parts)


# ================================================================
# ✅ Función de unión con limpieza automática
# ================================================================
def safe_concat_part(prev: str, part: str) -> str:
    """
    Une prev + part introduciendo un único espacio si es necesario.
    Luego limpia espacios duplicados generados por unir líneas.
    """
    if prev == "":
        return part
    if part == "":
        return prev

    # Si prev termina con \n literal, no agregar espacio
    if prev.endswith("\\n") or prev.endswith("\\n\""):
        joined = prev + part
    else:
        # Evitar doble espacio automático
        if prev.endswith(" ") or part.startswith(" "):
            joined = prev + part
        else:
            joined = prev + " " + part

    # ✅ Limpieza final de espacios
    joined = normalize_joined_spaces(joined)

    return joined


# ================================================================
# PROCESO PRINCIPAL
# ================================================================
def process_file(path: str):
    name = os.path.basename(path)
    print(f"\nProcesando: {name}")
    t0 = time.time()

    # Leer líneas
    with open(path, "r", encoding=ENCODING, errors="replace") as f:
        raw_lines = f.read().splitlines()

    if not raw_lines:
        print("  -> archivo vacío, saltando.")
        return

    fixed_lines = []
    buffer = None
    merges = 0
    orig_count = len(raw_lines)

    for line in raw_lines:
        if buffer is None:
            if line_has_unbalanced_quotes(line):
                buffer = line
            else:
                fixed_lines.append(line)
        else:
            buffer = safe_concat_part(buffer, line)

            if not line_has_unbalanced_quotes(buffer):
                fixed_lines.append(buffer)
                buffer = None
                merges += 1
            else:
                continue

    if buffer is not None:
        fixed_lines.append(buffer)
        merges += 1

    # Guardar sin .bak
    try:
        with open(path, "w", encoding=ENCODING, newline="\n") as out:
            out.write("\n".join(fixed_lines))
    except Exception as e:
        print("  -> ERROR al escribir archivo:", e)
        return

    elapsed = time.time() - t0
    print(f"  → Líneas originales: {orig_count}")
    print(f"  → Líneas finales:    {len(fixed_lines)}")
    print(f"  → Líneas unidas:     {merges}")
    print(f"  → Tiempo: {elapsed:.2f}s")


def main():
    files = sorted(glob.glob(os.path.join(CSV_FOLDER, "*.csv")))
    if not files:
        print("No se encontraron CSVs en:", CSV_FOLDER)
        return
    print(f"CSV detectados: {len(files)}")

    for f in files:
        process_file(f)

    print("\n✅ Proceso terminado. (OJO: archivos sobrescritos sin .bak)")


if __name__ == "__main__":
    main()
