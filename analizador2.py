import os
import re
import sys
import xml.etree.ElementTree as ET

try:
    import pandas as pd
    from tabulate import tabulate
except ImportError:
    print("❌ Error: Faltan librerías. Ejecuta: pip install pandas tabulate")
    sys.exit(1)

# Expresiones regulares
RE_INVALIDOS = re.compile(r'[^\w\s\d,.:;\-\_\(\)\?\!áéíóúÁÉÍÓÚñÑüÜàèìòùÀÈÌÒÙâêîôûÂÊÎÔÛ]')
RE_ANIOS = re.compile(r'\b(19\d\d|20\d\d)\b')

# Palabras clave de error
PALABRAS_ERROR = {"error", "fallo", "critico", "crítico", "bug", "failed"}

# Etiquetas específicas a evaluar
TAGS_EQUIPO = {"etiqueta", "equipo", "etiqueta_equipo", "tag", "etiquetaequipo"}
TAGS_FECHA = {"fecha", "date", "fecha_incidencia", "created_at"}


def es_caracter_valido(char):
    codepoint = ord(char)
    if 32 <= codepoint <= 126:
        return True
    if char in "áéíóúÁÉÍÓÚñÑüÜàèìòùÀÈÌÒÙâêîôûÂÊÎÔÛ":
        return True
    return False


def analizar_y_filtrar_texto(texto):
    if not texto:
        return True, ""

    texto_str = str(texto).strip()
    es_valido = True
    caracteres_limpios = []

    for char in texto_str:
        if es_caracter_valido(char):
            caracteres_limpios.append(char)
        else:
            es_valido = False

    return es_valido, "".join(caracteres_limpios)


def validar_etiqueta_equipo(valor):
    val = valor.strip()
    if val == "":
        return True
    return len(val) == 9 and val.isdigit()


def parsear_y_filtrar_xml(ruta_xml):
    if not os.path.exists(ruta_xml):
        print(f"❌ No se encontró el archivo: '{ruta_xml}'.")
        return None

    try:
        tree = ET.parse(ruta_xml)
        root = tree.getroot()
    except Exception as e:
        print(f"❌ Error al leer la estructura del XML: {e}")
        return None

    registros = []

    for i, child in enumerate(root):
        registro = {"ID": i + 1}
        motivos_mala = []

        for elem in child:
            tag_name = elem.tag.lower()
            val_original = elem.text if elem.text else ""

            # 1. Caracteres latinos / ASCII
            valido_char, val_limpio = analizar_y_filtrar_texto(val_original)
            if not valido_char:
                motivos_mala.append(f"ASCII en '{elem.tag}'")

            # 2. Etiqueta de Equipo (9 dígitos o vacía)
            if any(k in tag_name for k in TAGS_EQUIPO):
                if not validar_etiqueta_equipo(val_limpio):
                    motivos_mala.append(f"Etiqueta inválida ('{val_limpio}')")

            # 3. Fechas (2024 - 2026)
            if any(f in tag_name for f in TAGS_FECHA):
                anios = RE_ANIOS.findall(val_limpio)
                for anio_str in anios:
                    if not (2024 <= int(anio_str) <= 2026):
                        motivos_mala.append(f"Año fuera de 2024-2026 ({anio_str})")
                        break

            # 4. Palabras clave de error
            if any(p in val_limpio.lower() for p in PALABRAS_ERROR):
                motivos_mala.append(f"Error en '{elem.tag}'")

            registro[elem.tag] = val_limpio

        if motivos_mala:
            registro["Evaluación"] = f"Mala ({', '.join(set(motivos_mala))})"
            registro["Estado"] = "Mala"
        else:
            registro["Evaluación"] = "Buena (Correcta)"
            registro["Estado"] = "Buena"

        registros.append(registro)

    return pd.DataFrame(registros)


def imprimir_tabla_compacta(df):
    """Imprime el DataFrame limitando el ancho máximo de las celdas para no romper la pantalla."""
    if df.empty:
        print("⚠️ Sin registros para mostrar.")
        return

    # tabulate con límites de ancho por columna para que entre limpio en consola
    tabla_fmt = tabulate(
        df,
        headers="keys",
        tablefmt="fancy_grid",
        showindex=False,
        maxcolwidths=[6, 25, 12, 12, 30]  # Limita el ancho de los textos largos
    )
    print(tabla_fmt)


def dibujar_grafico_terminal(conteo_buenas, conteo_malas, total):
    print("\n" + "=" * 55)
    print("      📊 DIAGRAMA DE BARRAS (EN CONSOLA) 📊")
    print("=" * 55)

    ancho_max = 35
    pct_buenas = (conteo_buenas / total * 100) if total > 0 else 0
    pct_malas = (conteo_malas / total * 100) if total > 0 else 0

    len_buenas = int((conteo_buenas / total) * ancho_max) if total > 0 else 0
    len_malas = int((conteo_malas / total) * ancho_max) if total > 0 else 0

    barra_buenas = "█" * len_buenas
    barra_malas = "█" * len_malas

    print(f"\nBuenas : |{barra_buenas:<{ancho_max}}| {conteo_buenas} ({pct_buenas:.1f}%)")
    print(f"Malas  : |{barra_malas:<{ancho_max}}| {conteo_malas} ({pct_malas:.1f}%)")
    print("\n" + "-" * 55)


def main():
    print("=" * 55)
    print("  ANALIZADOR Y FILTRADOR AUTOMÁTICO DE INCIDENCIAS XML")
    print("=" * 55)

    ruta = input("\n📄 Introduce la ruta de tu archivo XML (ej: datos.xml): ").strip()
    df = parsear_y_filtrar_xml(ruta)

    if df is None or df.empty:
        print("⚠️ No se pudieron procesar datos del XML.")
        return

    df_buenas = df[df["Estado"] == "Buena"].drop(columns=["Estado"])
    df_malas = df[df["Estado"] == "Mala"].drop(columns=["Estado"])

    buenas = len(df_buenas)
    malas = len(df_malas)
    total = len(df)

    print("\n--- ESTADÍSTICAS GLOBALES ---")
    print(f"• Total procesadas  : {total}")
    print(f"• Incidencias Buenas: {buenas}")
    print(f"• Incidencias Malas : {malas}")

    dibujar_grafico_terminal(buenas, malas, total)

    print("\n" + "=" * 55)
    print("         ✅ TABLA DE INCIDENCIAS BUENAS ✅")
    print("=" * 55)
    imprimir_tabla_compacta(df_buenas)

    while True:
        print("\n🔍 OPCIONES ADICIONALES:")
        print("1. Mostrar tabla de incidencias BUENAS")
        print("2. Mostrar tabla de incidencias MALAS")
        print("3. Mostrar tabla de TODAS las incidencias")
        print("4. Salir")

        op = input("\nSelecciona una opción (1-4): ").strip()

        if op == "1":
            print("\n================ Incidencias BUENAS ================")
            imprimir_tabla_compacta(df_buenas)
        elif op == "2":
            print("\n================ Incidencias MALAS ================")
            imprimir_tabla_compacta(df_malas)
        elif op == "3":
            print("\n================ TODAS LAS INCIDENCIAS ================")
            imprimir_tabla_compacta(df.drop(columns=["Estado"]))
        elif op == "4":
            print("👋 Saliendo del programa...")
            break
        else:
            print("⚠️ Opción no válida.")


if __name__ == "__main__":
    main()