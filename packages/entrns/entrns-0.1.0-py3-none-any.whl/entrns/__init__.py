# entrns/__init__.py

import time
import sys

class BotEntrenado:
    def __init__(self, nombre):
        self.nombre = nombre

    def responder(self, mensaje):
        corregido = self._corregir_texto(mensaje)
        respuesta = f"Hola, soy {self.nombre}. Dijiste: '{corregido}'"
        return respuesta

    def _corregir_texto(self, texto):
        # Corrección mínima
        correcciones = {"hoja": "hola", "grasias": "gracias", "asta": "hasta"}
        palabras = texto.lower().split()
        corregidas = [correcciones.get(p, p) for p in palabras]
        return " ".join(corregidas)

def crear_bot(nombre="BotEntrns", saltar_timer=False):
    if not saltar_timer:
        print("Entrenando al bot. Espera 5 minutos (simulados)...")
        for i in range(5, 0, -1):
            print(f"{i} minutos restantes...")
            time.sleep(1)  # Simulación rápida: 1 segundo = 1 minuto
    else:
        print("Entrenamiento saltado con --saltar-tim")

    print("Bot entrenado con éxito.")
    return BotEntrenado(nombre)

def main():
    args = sys.argv
    saltar = "--saltar-tim" in args
    bot = crear_bot(saltar_timer=saltar)
    while True:
        entrada = input("Tú: ")
        if entrada.lower() in ["salir", "exit"]:
            break
        print(bot.responder(entrada))

if __name__ == "__main__":
    main()
