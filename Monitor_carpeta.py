# ============================================================
#  MONITOR DE CARPETA - Automatizacion con Python
#  TP Programacion 1 - Soporte de Infraestructura - ISTEA
#  Libreria usada: watchdog
# ============================================================


# --- 1. IMPORTACION DE LIBRERIAS ------------------------------

import os       # Para crear la carpeta y armar la ruta del log
import time     # Para hacer pausas mientras el programa sigue corriendo
from datetime import datetime  # Para mostrar la hora exacta de cada evento

# De la libreria watchdog importamos dos piezas:
from watchdog.observers import Observer            # El "observador": vigila la carpeta
from watchdog.events import FileSystemEventHandler # La clase base para reaccionar a los cambios


# --- 2. CONFIGURACION -----------------------------------------

# Nombre de la carpeta que queremos vigilar.
CARPETA_VIGILADA = "carpeta_vigilada"

# Archivo donde guardamos el registro de eventos. ~ = carpeta del usuario.
# IMPORTANTE: el log va FUERA de la carpeta vigilada, si no watchdog
# detectaria sus propias escrituras y se generaria un bucle infinito.
ARCHIVO_LOG = os.path.expanduser("~/Documents/eventos_carpeta.log")


# --- 3. NUESTRO "VIGILANTE" (que hacer ante cada cambio) ------

# Creamos nuestra propia clase que hereda de FileSystemEventHandler.
# Heredar significa que aprovechamos todo lo que ya sabe hacer watchdog
# y solo definimos como reaccionar a cada tipo de evento.
class Vigilante(FileSystemEventHandler):

    # Funcion central: arma un mensaje claro, lo muestra en pantalla Y lo guarda en el log.
    def registrar(self, accion, event, extra=""):
        # Fecha y hora actual como texto legible.
        momento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # event.is_directory es True si lo que cambio fue una CARPETA,
        # y False si fue un ARCHIVO. Asi distinguimos los dos casos.
        tipo = "la carpeta" if event.is_directory else "el archivo"

        # Armamos un mensaje en lenguaje natural, ej: "Se creo el archivo: ..."
        linea = f"[{momento}] Se {accion} {tipo}: {event.src_path}{extra}"

        # 1) Lo mostramos en la consola (para la demo en vivo).
        print(linea)
        # 2) Lo guardamos en el archivo de log (modo "a" = agregar al final).
        with open(ARCHIVO_LOG, "a", encoding="utf-8") as f:
            f.write(linea + "\n")

    # Se ejecuta cuando se CREA un archivo o carpeta.
    def on_created(self, event):
        self.registrar("creó", event)

    # Se ejecuta cuando se MODIFICA (se edita y guarda) un archivo o carpeta.
    def on_modified(self, event):
        self.registrar("modificó", event)

    # Se ejecuta cuando se BORRA un archivo o carpeta.
    def on_deleted(self, event):
        self.registrar("borró", event)

    # Se ejecuta cuando se MUEVE o RENOMBRA. Tiene origen (src) y destino (dest).
    def on_moved(self, event):
        self.registrar("movió/renombró", event, extra=f"  ->  {event.dest_path}")


# --- 4. PROGRAMA PRINCIPAL ------------------------------------

if __name__ == "__main__":

    # Creamos la carpeta a vigilar. Si ya existe, exist_ok=True evita el error.
    os.makedirs(CARPETA_VIGILADA, exist_ok=True)

    # Mensajes de bienvenida para la demo.
    print("=" * 60)
    print(f"  VIGILANDO LA CARPETA: {CARPETA_VIGILADA}")
    print(f"  Los eventos se guardan en: {ARCHIVO_LOG}")
    print("  Crea, edita, borra o mueve archivos/carpetas para ver los eventos.")
    print("  (Ctrl + C para salir)")
    print("=" * 60)

    # Creamos una instancia de nuestro vigilante (el "que hacer").
    vigilante = Vigilante()

    # Creamos el observador (el "quien mira").
    observador = Observer()

    # Le decimos al observador: vigila esta carpeta usando este vigilante.
    #   - recursive=True: ademas de la carpeta, mira TODAS sus subcarpetas.
    observador.schedule(vigilante, CARPETA_VIGILADA, recursive=True)

    # Arrancamos la vigilancia. A partir de aca queda escuchando cambios.
    observador.start()

    # Mantenemos el programa vivo con un bucle, hasta que el usuario lo corte.
    try:
        while True:
            time.sleep(1)  # Pausa de 1 segundo para no saturar el procesador.

    # Cuando apretas Ctrl + C, entra aca y frena la vigilancia ordenadamente.
    except KeyboardInterrupt:
        observador.stop()
        print("\nVigilancia detenida.")

    # Esperamos a que el observador termine de cerrarse bien antes de salir.
    observador.join()
