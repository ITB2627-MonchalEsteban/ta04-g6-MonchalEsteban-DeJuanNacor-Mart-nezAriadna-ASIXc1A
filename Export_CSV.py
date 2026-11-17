import csv
import xml.etree.ElementTree as ET


def csv_a_xml(archivo_csv, archivo_xml):
    # Crear el elemento raíz del XML
    raiz = ET.Element("datos")

    # Leer el archivo CSV
    with open(archivo_csv, mode="r", encoding="utf-8") as file:
        lector_csv = csv.DictReader(file)

        # Iterar por cada fila del CSV
        for fila in lector_csv:
            # Crear un elemento contenedor para cada registro
            item = ET.SubElement(raiz, "registro")

            # Añadir las columnas como etiquetas hijas
            for clave, valor in fila.items():
                # Reemplazar espacios en nombres de columna si los hubiera
                clave_limpia = clave.strip().replace(" ", "_")
                hijo = ET.SubElement(item, clave_limpia)
                hijo.text = valor.strip() if valor else ""

    # Generar el árbol XML y formatear con sangría
    arbol = ET.ElementTree(raiz)
    ET.indent(arbol, space="  ", level=0)

    # Guardar en archivo
    arbol.write(archivo_xml, encoding="utf-8", xml_declaration=True)
    print(f"Archivo guardado exitosamente como '{archivo_xml}'")


# Ejemplo de uso:
# Reemplaza 'datos.csv' y 'resultado.xml' con las rutas de tus archivos
csv_a_xml("incidencies.csv", "incidencies.xml")