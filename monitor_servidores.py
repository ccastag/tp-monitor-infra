# ============================================================
#  MONITOR DE INFRAESTRUCTURA - Automatizacion con Python
#  TP Programacion - Soporte de Infraestructura - ISTEA
#  Librerias: subprocess + schedule
# ============================================================


# --- 1. IMPORTACION DE LIBRERIAS ------------------------------

import subprocess   # Ejecuta comandos del sistema (ping, osascript) desde Python
import schedule     # Programa tareas para que se repitan cada cierto tiempo
import time         # Pausas (sleep) para el bucle principal
import platform     # Detecta el sistema operativo (Windows, Linux o Mac)
import os           # Para armar la ruta del archivo de alertas
from datetime import datetime  # Fecha y hora exacta de cada evento


# --- 2. UTILIDADES DE PANTALLA --------------------------------

# Codigos ANSI: le dan color al texto que imprimimos en la consola.
VERDE    = "\033[92m"   # Texto verde
ROJO     = "\033[91m"   # Texto rojo
AMARILLO = "\033[93m"   # Texto amarillo
RESET    = "\033[0m"    # Vuelve al color normal (importante cerrar siempre)

def ahora():
    """Devuelve la fecha y hora actual como texto legible."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# --- 3. CONFIGURACION POR DEFECTO -----------------------------

# Lista de ejemplo: un host que SIEMPRE responde, uno de internet y uno caido.
HOSTS_EJEMPLO = ["127.0.0.1", "8.8.8.8", "10.255.255.1"]

# Cada cuantos segundos repetir el chequeo si el usuario no elige otro valor.
INTERVALO_POR_DEFECTO = 10

# Archivo donde se guardan las alertas. ~  = carpeta del usuario actual.
ARCHIVO_ALERTAS = os.path.expanduser("~/Documents/alertas.log")

# Estas dos variables se completan segun lo que elija el usuario en el menu.
HOSTS = []
INTERVALO_SEGUNDOS = INTERVALO_POR_DEFECTO


# --- 4. CONFIGURACION INTERACTIVA (el usuario decide) ---------

def configurar():
    """Pregunta al usuario que hosts monitorear y cada cuantos segundos."""

    # 'global' nos permite modificar las variables de afuera de la funcion.
    global HOSTS, INTERVALO_SEGUNDOS

    print("=" * 55)
    print("   CONFIGURACION DEL MONITOR")
    print("=" * 55)
    print("  1) Usar lista de ejemplo (localhost, Google DNS, IP caida)")
    print("  2) Ingresar mis propias IPs / dominios")

    # input() lee lo que el usuario escribe por teclado. .strip() saca espacios.
    opcion = input("  Elegi una opcion (1 o 2): ").strip()

    if opcion == "2":
        # Pedimos las IPs todas juntas, separadas por comas.
        texto = input("  Escribi las IPs separadas por coma: ")
        # split(",") corta el texto en cada coma y arma una lista.
        # Con el for limpiamos espacios y descartamos lo que quede vacio.
        HOSTS = [ip.strip() for ip in texto.split(",") if ip.strip()]
    else:
        # Cualquier otra cosa que no sea "2" usa la lista de ejemplo.
        HOSTS = HOSTS_EJEMPLO

    # Preguntamos el intervalo. Si aprieta Enter sin escribir, usa el default.
    intervalo_texto = input(f"  Cada cuantos segundos chequeo? (Enter = {INTERVALO_POR_DEFECTO}): ").strip()
    # .isdigit() es True solo si el texto son numeros (ej: "15").
    if intervalo_texto.isdigit():
        INTERVALO_SEGUNDOS = int(intervalo_texto)
    else:
        INTERVALO_SEGUNDOS = INTERVALO_POR_DEFECTO


# --- 5. FUNCION QUE HACE EL PING (subprocess) -----------------

def hacer_ping(host):
    """Hace ping a un host. Devuelve True si responde, False si no."""

    # Windows usa "-n" y Linux/Mac usan "-c" para indicar 1 solo paquete.
    parametro = "-n" if platform.system().lower() == "windows" else "-c"

    # Comando final como lista, ej: ["ping", "-c", "1", "8.8.8.8"]
    comando = ["ping", parametro, "1", host]

    try:
        # timeout=3 -> si el ping tarda mas de 3 segundos, lo cortamos.
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=3)
        # returncode 0 = respondio. Cualquier otro numero = no respondio.
        return resultado.returncode == 0
    except subprocess.TimeoutExpired:
        # Si se paso de los 3 segundos, lo damos por caido.
        return False


# --- 6. ACCIONES DE REACCION (el efecto WOW) ------------------

def registrar_alerta(host):
    """Escribe una linea de alerta en el archivo cuando un host se cae."""
    linea = f"[{ahora()}] ALERTA: el host {host} esta CAIDO\n"
    # Modo "a" (append): agrega al final sin borrar lo anterior.
    with open(ARCHIVO_ALERTAS, "a", encoding="utf-8") as f:
        f.write(linea)


def notificar_escritorio(titulo, mensaje):
    """Muestra una notificacion real del sistema usando subprocess."""
    sistema = platform.system().lower()
    try:
        if sistema == "darwin":      # darwin = macOS
            # Llamamos a osascript (lenguaje de automatizacion de Mac).
            subprocess.run(["osascript", "-e",
                            f'display notification "{mensaje}" with title "{titulo}"'])
        elif sistema == "linux":
            # En Linux usamos notify-send (si esta disponible).
            subprocess.run(["notify-send", titulo, mensaje])
        # En Windows lo omitimos para no complicar; el resto de alertas igual anda.
    except Exception:
        # Si el sistema no permite notificar, NO rompemos el programa.
        pass


# --- 7. CHEQUEO DE TODOS LOS HOSTS ----------------------------

def chequear_servidores():
    """Recorre todos los hosts, los pinguea y reacciona si alguno esta caido."""

    print(f"\n--- Chequeo {ahora()} ---")

    # Recorremos uno por uno los hosts configurados.
    for host in HOSTS:

        esta_vivo = hacer_ping(host)

        if esta_vivo:
            # Host OK: lo mostramos en verde.
            print(f"{VERDE}[  UP  ]{RESET} {host}")
        else:
            # Host caido: lo mostramos en rojo y disparamos las alertas.
            print(f"{ROJO}[ DOWN ]{RESET} {host}  -> disparando alertas!")
            registrar_alerta(host)                    # 1) Escribe el archivo de alertas
            notificar_escritorio("Monitor de Infraestructura",  # 2) Notificacion de escritorio
                                 f"El host {host} esta CAIDO")


# --- 8. PROGRAMA PRINCIPAL ------------------------------------

if __name__ == "__main__":

    # Primero corremos el menu interactivo para que el usuario configure todo.
    configurar()

    # Le decimos a schedule que repita el chequeo cada X segundos.
    schedule.every(INTERVALO_SEGUNDOS).seconds.do(chequear_servidores)

    print("=" * 55)
    print(f"  MONITOR INICIADO - {len(HOSTS)} hosts cada {INTERVALO_SEGUNDOS}s")
    print(f"  Las alertas se guardan en: {ARCHIVO_ALERTAS}")
    print("  (Ctrl + C para salir)")
    print("=" * 55)

    # Primer chequeo inmediato, sin esperar el intervalo.
    chequear_servidores()

    # Bucle infinito que mantiene vivo el programa.
    while True:
        schedule.run_pending()   # schedule revisa si toca ejecutar la tarea
        time.sleep(1)            # Pausa de 1 segundo para no saturar el CPU
