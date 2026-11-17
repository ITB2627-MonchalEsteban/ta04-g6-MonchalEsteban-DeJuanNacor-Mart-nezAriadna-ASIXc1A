import xml.etree.ElementTree as ET
import re
import sys
import unicodedata
from lingua import Language, LanguageDetectorBuilder

# --- CONFIGURACIÓN ---
ARCHIVO_XML = "incidencies.xml"
ETIQUETA_REGISTRO = "incidencia"
ETIQUETA_EQUIPO = "etiqueta_del_equipo_texto_corto_ejemplo_202500127"

IDIOMAS_PERMITIDOS = {Language.SPANISH, Language.CATALAN, Language.ENGLISH}

# Respuestas evasivas o sin contenido real (en castellano, catalán e inglés)
RESPUESTAS_EVASIVAS = {
    # Castellano
    "no lo se", "no se", "nose", "ni idea", "no tengo ni idea", "no tengo idea",
    "ni puta idea", "ns", "nc", "ns nc", "ns/nc", "no aplica", "na", "n/a",
    "ninguno", "ninguna", "nada", "todo bien", "sin comentarios", "lo desconozco",
    "desconocido", "no me acuerdo", "no recuerdo", "no lo recuerdo", "paso",
    "no quiero decirlo", "anonimo", "asdf", "qwerty", "test", "prueba", "hola",
    
    # Catalán
    "no ho se", "no se pas", "no en tinc ni idea", "ni idea", "res", "cap",
    "no aplica", "no me n'enrecordo", "no ho recordo", "desconegut", "prova",
    
    # Inglés
    "i dont know", "dont know", "idk", "no idea", "nothing", "none", "unknown",
    "not sure", "i am not sure", "im not sure", "whatever", "dunno"
}

def normalizar_texto(texto):
    """Quita tildes, pasa a minúsculas y elimina espacios extra."""
    texto = texto.lower().strip()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return re.sub(r'\s+', ' ', texto)

def limpiar_puntuacion(texto_norm):
    """Deja solo letras, números y espacios para comparar respuestas evasivas."""
    limpio = re.sub(r'[^a-z0-9\s]', ' ', texto_norm)
    return re.sub(r'\s+', ' ', limpio).strip()

EVASIVAS_NORMALIZADAS = {limpiar_puntuacion(normalizar_texto(r)) for r in RESPUESTAS_EVASIVAS}

detector = LanguageDetectorBuilder.from_languages(
    Language.SPANISH,
    Language.CATALAN,
    Language.ENGLISH,
    Language.FRENCH,
    Language.GERMAN,
    Language.ITALIAN,
    Language.PORTUGUESE,
    Language.RUSSIAN,
    Language.ARABIC,
    Language.CHINESE,
    Language.JAPANESE,
    Language.ROMANIAN,
    Language.POLISH
).with_low_accuracy_mode().build()

# Expresiones regulares compiladas
RE_CAJAS = re.compile(r'[\u2500-\u259F]')
RE_SIMBOLOS_REP = re.compile(r'([_/\\|*#=~-]{4,})')
RE_NO_LETRAS = re.compile(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜçÇ·\s.,;:¿?¡!()"-]')
RE_SOLO_PALABRAS = re.compile(r'[^a-zA-ZáéíóúÁÉÍÓÚàèòÀÈÒïüÏÜñÑçÇ·\s]')
RE_ETIQUETA_VALIDA = re.compile(r'^202\d{6}$')

def es_etiqueta_valida(texto):
    if not texto or not texto.strip():
        return True
    return bool(RE_ETIQUETA_VALIDA.match(texto.strip()))

def es_respuesta_evasiva(texto_campo):
    """Detecta si un campo entero es una evasiva ('no lo se', 'ni idea', '...', etc.)."""
    norm = normalizar_texto(texto_campo)
    limpio = limpiar_puntuacion(norm)
    
    if not limpio:
        return True
    if limpio in EVASIVAS_NORMALIZADAS:
        return True
    if limpio.startswith(("no lo se ", "no ho se ", "ni idea ", "i dont know ")):
        return True
        
    return False

def es_arte_ascii(texto):
    if not texto or not texto.strip():
        return False
    if texto.count('\n') >= 3:
        return True
    if RE_CAJAS.search(texto):
        return True
    if RE_SIMBOLOS_REP.search(texto):
        return True
        
    texto_limpio = texto.strip()
    if len(texto_limpio) > 15:
        simbolos = len(RE_NO_LETRAS.findall(texto_limpio))
        if (simbolos / len(texto_limpio)) > 0.35:
            return True
    return False

def es_idioma_invalido(texto_combinado):
    if not texto_combinado.strip():
        return False

    if re.search(r'[\u0400-\u04FF\u0600-\u06FF\u4E00-\u9FFF\u3040-\u30FF]', texto_combinado):
        return True

    solo_palabras = RE_SOLO_PALABRAS.sub('', texto_combinado).strip()
    if len(solo_palabras) < 20 or len(solo_palabras.split()) < 4:
        return False

    idioma = detector.detect_language_of(solo_palabras)
    if idioma is not None and idioma not in IDIOMAS_PERMITIDOS:
        return True

    return False

def mostrar_barra(correctos, mal_etiqueta, mal_evasiva, mal_ascii, mal_idioma):
    total_malos = mal_etiqueta + mal_evasiva + mal_ascii + mal_idioma
    total = correctos + total_malos
    
    if total == 0:
        print("No se encontraron registros para analizar.")
        return

    pct_ok = (correctos / total) * 100
    pct_mal = (total_malos / total) * 100

    ancho_barra = 40
    bloques_ok = int(round((correctos / total) * ancho_barra))
    bloques_mal = ancho_barra - bloques_ok

    VERDE = "\033[92m"
    ROJO = "\033[91m"
    AMARILLO = "\033[93m"
    NEGRITA = "\033[1m"
    RESET = "\033[0m"

    barra = f"{VERDE}{'█' * bloques_ok}{ROJO}{'█' * bloques_mal}{RESET}"

    print("\n" + "=" * 64)
    print(f"{NEGRITA}📊 ANÁLISIS DE INCIDENCIAS (Total registros: {total}){RESET}")
    print("=" * 64)
    print(f"[{barra}]")
    print(f"{VERDE}✔ Correctos  : {correctos:<5} ({pct_ok:.1f}%){RESET}")
    print(f"{ROJO}✘ Malos      : {total_malos:<5} ({pct_mal:.1f}%){RESET}")
    print(f"{AMARILLO}   ├─ Por etiqueta inválida : {mal_etiqueta}{RESET}")
    print(f"{AMARILLO}   ├─ Por 'No lo sé'/evasiva: {mal_evasiva}{RESET}")
    print(f"{AMARILLO}   ├─ Por arte ASCII        : {mal_ascii}{RESET}")
    print(f"{AMARILLO}   └─ Por otro idioma       : {mal_idioma}{RESET}")
    print("=" * 64 + "\n")

def analizar_xml():
    print("Cargando archivo XML...")
    try:
        tree = ET.parse(ARCHIVO_XML)
        root = tree.getroot()
    except FileNotFoundError:
        print(f"❌ Error: No se encuentra '{ARCHIVO_XML}'.")
        sys.exit(1)
    except ET.ParseError as e:
        print(f"❌ Error de sintaxis en el XML: {e}")
        sys.exit(1)

    registros = root.findall(f".//{ETIQUETA_REGISTRO}")
    if not registros:
        registros = list(root)

    total_registros = len(registros)
    correctos = 0
    mal_etiqueta = 0
    mal_evasiva = 0
    mal_ascii = 0
    mal_idioma = 0

    for i, registro in enumerate(registros, start=1):
        if i % 100 == 0 or i == total_registros:
            print(f"\rProcesando: {i}/{total_registros} registros...", end="", flush=True)

        # 1. Comprobación de la etiqueta del equipo
        campo_etiqueta = registro.find(f".//{ETIQUETA_EQUIPO}")
        texto_etiqueta = campo_etiqueta.text if campo_etiqueta is not None else ""
        
        if not es_etiqueta_valida(texto_etiqueta):
            mal_etiqueta += 1
            continue

        # 2. Comprobación campo por campo (evasivas y arte ASCII)
        tiene_ascii = False
        tiene_evasiva = False
        textos_formulario = []

        for campo in registro.iter():
            if campo.tag == ETIQUETA_EQUIPO:
                continue
                
            if campo.text and campo.text.strip():
                if es_arte_ascii(campo.text):
                    tiene_ascii = True
                    break
                if es_respuesta_evasiva(campo.text):
                    tiene_evasiva = True
                    break
                textos_formulario.append(campo.text.strip())
        
        if tiene_ascii:
            mal_ascii += 1
            continue
        if tiene_evasiva:
            mal_evasiva += 1
            continue

        # 3. Comprobación de idioma
        texto_completo = " ".join(textos_formulario)
        if es_idioma_invalido(texto_completo):
            mal_idioma += 1
        else:
            correctos += 1

    print()
    mostrar_barra(correctos, mal_etiqueta, mal_evasiva, mal_ascii, mal_idioma)

if __name__ == "__main__":
    analizar_xml()