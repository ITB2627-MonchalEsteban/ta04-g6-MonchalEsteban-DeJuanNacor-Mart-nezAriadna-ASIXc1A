import random
import time
from faker import Faker
from playwright.sync_api import sync_playwright

fake = Faker('es_ES')

# --- CONFIGURACIÓN ---
FORM_URLS = [
    "https://forms.gle/i77dc5vRpmUFNS476",
    # Añade aquí tus links
]

TOTAL_RESPUESTAS = 5  # Cantidad de envíos a realizar por cada enlace

OPINIONES_CREIBLES = [
    "Muy buena experiencia en general, me gustó mucho la atención.",
    "El servicio es correcto, aunque creo que se podría mejorar la puntualidad.",
    "Todo bien, sin inconvenientes relevantes.",
    "Excelente atención y gran profesionalidad por parte del personal.",
    "Cumplió con mis expectativas, lo recomendaría sin duda.",
    "El proceso fue sencillo y rápido de completar."
]

def pausa_humana(min_sec=1.5, max_sec=4.0):
    time.sleep(random.uniform(min_sec, max_sec))

def responder_formulario(page):
    # Texto corto
    for inp in page.query_selector_all('input[type="text"]:not([aria-label*="Otro"])'):
        if inp.is_visible():
            pausa_humana(0.5, 1.5)
            inp.fill(fake.name() if random.random() > 0.5 else fake.city())

    # Texto largo
    for area in page.query_selector_all('textarea'):
        if area.is_visible():
            pausa_humana(1.0, 3.0)
            area.fill(random.choice(OPINIONES_CREIBLES))

    # Opción única (Radio buttons)
    for group in page.query_selector_all('div[role="radiogroup"]'):
        opciones = group.query_selector_all('div[role="radio"]')
        if opciones:
            pausa_humana(0.8, 2.0)
            random.choice(opciones).click()

    # Casillas de verificación (Checkboxes)
    for group in page.query_selector_all('div[role="group"]'):
        checkboxes = group.query_selector_all('div[role="checkbox"]')
        if checkboxes:
            pausa_humana(0.8, 2.0)
            para_marcar = random.sample(checkboxes, k=random.randint(1, min(2, len(checkboxes))))
            for cb in para_marcar:
                cb.click()
                time.sleep(0.3)

def ejecutar():
    with sync_playwright() as p:
        # headless=True ejecuta el navegador en segundo plano sin abrir ventanas gráficas
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        for url in FORM_URLS:
            print(f"Procesando formulario: {url}")
            for i in range(TOTAL_RESPUESTAS):
                print(f"  -> Enviando respuesta {i + 1}/{TOTAL_RESPUESTAS}...")
                page = context.new_page()
                page.goto(url)
                
                pausa_humana(2.0, 4.0)
                responder_formulario(page)
                pausa_humana(1.5, 3.5)

                boton_enviar = page.query_selector('div[role="button"]:has-text("Enviar")') or \
                               page.query_selector('div[role="button"]:has-text("Submit")')
                if boton_enviar:
                    boton_enviar.click()
                    page.wait_for_timeout(2000)
                
                page.close()
                time.sleep(random.uniform(5.0, 12.0))

        browser.close()
        print("Proceso finalizado con éxito.")

if __name__ == "__main__":
    ejecutar()