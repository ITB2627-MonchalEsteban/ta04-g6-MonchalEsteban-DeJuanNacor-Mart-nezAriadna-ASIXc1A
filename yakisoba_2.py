from time import sleep

# region Declaració de Funcions ----------
def recopilar_ingredients():
    print("Comprar al supermercat")
    sleep(1)
    print("Disposar-los sobre el marbre")
    sleep(1)

def cuinar_tallarines():
    print("Cuinar tallarines")
    #sleep(5)
    animacio_cuinar(15)
    print("FI Cuinar tallarines")

def cuinar_pastanagues():
    print("Cuinar pastanagues")
    #sleep(3)
    animacio_cuinar()
    print("FI Cuinar pastanagues")

def animacio_cuinar(temps=3):
    """
    Muestra una animación de Pac-Man comiendo puntos.
    Utiliza '\r' para volver al inicio de la línea y simular movimiento.
    """
    # Definimos los fotogramas de la animación (boca abierta y cerrada)
    pacman_frames = ["ᗤ", "ᗧ"]
    
    for i in range(temps):
        # Selecciona el fotograma (alterna entre 0 y 1)
        fotograma = pacman_frames[i % 2]
        
        # Calcula cuántos puntos quedan por comer después de este fotograma
        puntos_restantes = "." * (temps - 1 - i)
        
        # Construye la línea: Pac-Man actual + puntos restantes
        # Se usa '\r' para sobrescribir la línea anterior en la consola
        linea_animacion = f"\r{fotograma}{puntos_restantes}"
        
        # Imprime la línea sin salto de línea y fuerza la actualización de pantalla
        print(linea_animacion, end="", flush=True)
        
        # Pausa breve para que la animación sea visible
        sleep(0.3)
        
    # Salto de línea final para terminar la animación correctamente
    print()

# endregion

# region INICI: Preparar fideus Yakisoba
recopilar_ingredients()
cuinar_tallarines()
cuinar_pastanagues()
# endregion