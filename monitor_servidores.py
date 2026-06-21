# ============================================================
#  MONITOR DE SERVIDORES - Automatizacion con Python
#  TP Programacion 1 - Soporte de Infraestructura - ISTEA
#  Librerias usadas: subprocess + schedule
# ============================================================


# --- 1. IMPORTACION DE LIBRERIAS ------------------------------

import subprocess   # Permite ejecutar comandos del sistema operativo (como "ping") desde Python
import schedule     # Permite programar tareas para que se repitan cada cierto tiempo
import time         # Libreria estandar de Python para manejar pausas (sleep)
import platform     # Nos dice en que sistema operativo estamos (Windows, Linux o Mac)
from datetime import datetime  # Para obtener la fecha y hora exacta de cada chequeo


# --- 2. CONFIGURACION -----------------------------------------

# Lista de servidores (hosts) que queremos vigilar.
# Pueden ser direcciones IP o nombres de dominio.
HOSTS = [
    "127.0.0.1",                   # localhost: SIEMPRE responde (no necesita internet)
    "8.8.8.8",                     # DNS de Google: responde si hay internet
    "servidor-que-no-existe.local" # Host inventado: lo usamos para ver un caso DOWN
]

# Cada cuantos segundos queremos repetir el chequeo de todos los hosts.
INTERVALO_SEGUNDOS = 10

# Nombre del archivo donde vamos a ir guardando el registro (log) de resultados.
ARCHIVO_LOG = "monitor.log"


# --- 3. FUNCION QUE HACE EL PING ------------------------------

def hacer_ping(host):
    """Hace ping a un host. Devuelve True si responde, False si no."""

    # El parametro de "cantidad de paquetes" cambia segun el sistema operativo:
    # Windows usa "-n" y Linux/Mac usan "-c". Lo elegimos automaticamente.
    parametro = "-n" if platform.system().lower() == "windows" else "-c"

    # Armamos el comando como una lista, por ejemplo: ["ping", "-c", "1", "8.8.8.8"]
    # El "1" significa enviar un solo paquete (suficiente para saber si esta vivo).
    comando = ["ping", parametro, "1", host]

    # Ejecutamos el comando con subprocess:
    #   - capture_output=True  -> guarda la salida en vez de imprimirla en pantalla
    #   - text=True            -> devuelve la salida como texto y no como bytes
    resultado = subprocess.run(comando, capture_output=True, text=True)

    # subprocess devuelve un "returncode":
    #   0  -> el comando salio bien (el host respondio)
    #   otro numero -> fallo (el host no respondio)
    return resultado.returncode == 0


# --- 4. FUNCION QUE CHEQUEA TODOS LOS HOSTS -------------------

def chequear_servidores():
    """Recorre la lista de hosts, hace ping a cada uno y registra el resultado."""

    # Tomamos la fecha y hora actual y la formateamos como texto legible.
    momento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Recorremos uno por uno todos los hosts de la lista.
    for host in HOSTS:

        # Llamamos a la funcion del paso 3 para saber si el host esta vivo.
        esta_vivo = hacer_ping(host)

        # Segun el resultado, definimos el texto del estado.
        estado = "[  UP  ]" if esta_vivo else "[ DOWN ]"

        # Armamos la linea de log con hora, host (alineado a 30 caracteres) y estado.
        linea = f"{momento}  {host:<30} {estado}"

        # La mostramos en pantalla: esto es lo que se ve en vivo durante la demo.
        print(linea)

        # Y ademas la guardamos en el archivo de log.
        # El modo "a" (append) agrega al final sin borrar lo que ya estaba.
        with open(ARCHIVO_LOG, "a", encoding="utf-8") as archivo:
            archivo.write(linea + "\n")

    # Linea separadora para distinguir cada ronda de chequeos.
    print("-" * 55)


# --- 5. PROGRAMACION DE LA TAREA (aca entra "schedule") -------

# Le decimos a schedule: "ejecuta la funcion chequear_servidores cada X segundos".
# Notar que pasamos la funcion SIN parentesis: schedule la llamara por nosotros.
schedule.every(INTERVALO_SEGUNDOS).seconds.do(chequear_servidores)


# --- 6. PROGRAMA PRINCIPAL ------------------------------------

# Esta condicion asegura que el codigo de abajo solo corra si ejecutamos
# este archivo directamente (y no si alguien lo importa desde otro script).
if __name__ == "__main__":

    # Mensaje de bienvenida al arrancar el monitor.
    print("=" * 55)
    print("   MONITOR DE SERVIDORES INICIADO")
    print(f"   Chequeo cada {INTERVALO_SEGUNDOS} segundos.  (Ctrl + C para salir)")
    print("=" * 55)

    # Hacemos un primer chequeo inmediato, sin esperar el intervalo.
    chequear_servidores()

    # Bucle infinito: mantiene el programa corriendo de forma continua.
    while True:

        # schedule revisa si llego el momento de ejecutar alguna tarea pendiente.
        schedule.run_pending()

        # Pausa de 1 segundo para no saturar el procesador.
        time.sleep(1)
