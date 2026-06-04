# -*- coding: utf-8 -*-
import os

# Forzar audio del menu por la salida que si funciono con aplay:
# aplay -D plughw:0,0 ~/pickaxestation/menu/mover.wav
os.environ["SDL_AUDIODRIVER"] = "alsa"
os.environ["SDL_AUDIO_ALSA_DEFAULT_DEVICE"] = "plughw:0,0"

import pygame
import shutil
import subprocess
import struct
from datetime import datetime

# ============================================================
# PickaxeStation - Menu principal
# Raspberry Pi OS Lite + Pygame + Mednafen
# Sin escritorio, sin RetroPie, sin RetroArch, sin EmulationStation.
# ============================================================

pygame.init()
pygame.joystick.init()

try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
except pygame.error as e:
    print(f"No se pudo inicializar audio de Pygame: {e}")

info = pygame.display.Info()
W, H = info.current_w, info.current_h

pantalla = pygame.display.set_mode((W, H), pygame.NOFRAME)
reloj = pygame.time.Clock()

base_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(base_path)

ROMS_SNES = os.path.join(project_path, "roms", "snes")
MEDIA_SNES = os.path.join(project_path, "media", "snes")
MEDIA_GENERAL = os.path.join(project_path, "media")
RUTA_USB = "/mnt/usb"
DISPOSITIVO_USB = None  # Se detecta dinamicamente con lsblk: /dev/sda1, /dev/sdb1, etc.

BOTON_X_PS4 = 0
BOTON_CIRCULO_PS4 = 1
BOTON_TRIANGULO_PS4 = 2
BOTON_CUADRADO_PS4 = 3
BOTON_SHARE_PS4 = 8
BOTON_OPTIONS_PS4 = 9

C_NEON = (0, 245, 255)
C_BLANCO = (255, 255, 255)
C_GRIS = (180, 180, 180)
C_NEGRO = (0, 0, 0)
C_FONDO = (10, 12, 18)
C_VERDE = (0, 255, 100)
C_ROJO = (255, 60, 60)


def cargar_imagen(nombre, carpeta=None, tamano=None, es_logo=False):
    """
    Carga una imagen desde la carpeta indicada o desde la carpeta base del menu.

    Si la imagen existe, la convierte con canal alfa para respetar transparencia,
    puede escalarla al tamano solicitado y, cuando se trata del logo, elimina el
    fondo negro usando colorkey. Si ocurre algun error o el archivo no existe,
    regresa None para que el programa pueda usar una alternativa visual.
    """
    if carpeta:
        ruta = os.path.join(carpeta, nombre)
    else:
        ruta = os.path.join(base_path, nombre)

    if os.path.exists(ruta):
        try:
            img = pygame.image.load(ruta).convert_alpha()

            if es_logo:
                img.set_colorkey((0, 0, 0))

            if tamano:
                img = pygame.transform.smoothscale(img, tamano)

            return img

        except Exception as e:
            print(f"Error al cargar imagen {ruta}: {e}")
            return None

    print(f"No se encontro imagen: {ruta}")
    return None


def cargar_logo(tamano=(600, 300)):
    """
    Busca y carga el logo principal de PickaxeStation.

    Prueba varios formatos comunes de imagen: JPEG, JPG y PNG. Regresa la
    primera imagen encontrada correctamente o None si no hay logo disponible.
    """
    for nombre in ["logo.jpeg", "logo.jpg", "logo.png"]:
        img = cargar_imagen(nombre, tamano=tamano, es_logo=True)
        if img:
            return img
    return None


img_fondo = cargar_imagen("fondo.png", tamano=(W, H))
img_logo = cargar_logo(tamano=(600, 300))
img_default = cargar_imagen("Default.png", MEDIA_GENERAL, tamano=(340, 340))

try:
    if pygame.mixer.get_init():
        sonido_mover = pygame.mixer.Sound(os.path.join(base_path, "mover.wav"))
        sonido_mover.set_volume(1.0)
    else:
        sonido_mover = None
except Exception as e:
    print(f"No se pudo cargar mover.wav: {e}")
    sonido_mover = None


def dibujar_texto_con_sombra(sup, texto, fuente, color, pos, desfase=2):
    """
    Dibuja texto con una sombra negra para mejorar su lectura en pantalla.

    Primero imprime el texto desplazado como sombra y despues lo vuelve a
    imprimir en la posicion real con el color indicado.
    """
    sup.blit(fuente.render(texto, True, C_NEGRO), (pos[0] + desfase, pos[1] + desfase))
    sup.blit(fuente.render(texto, True, color), pos)


def dibujar_panel(sup, x, y, ancho, alto, grosor=3):
    """
    Dibuja un panel semitransparente con borde neon.

    Se usa para separar visualmente secciones del menu, como informacion del
    proyecto, portada del juego y datos del sistema.
    """
    s = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    sup.blit(s, (x, y))
    pygame.draw.rect(sup, C_NEON, (x, y, ancho, alto), grosor, border_radius=10)


def oscurecer_fondo(nivel=160):
    """
    Coloca una capa negra semitransparente sobre toda la pantalla.

    Sirve para oscurecer el fondo y hacer que los textos, paneles y menus
    aparezcan con mayor contraste.
    """
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, nivel))
    pantalla.blit(overlay, (0, 0))


def mostrar_mensaje_centro(titulo, subtitulo="", color=C_NEON, segundos=1.5):
    """
    Muestra una pantalla simple con un titulo y un subtitulo centrados.

    Se utiliza para avisos temporales como carga de juego, sincronizacion,
    regreso al menu, apagado, reinicio o errores.
    """
    pantalla.fill(C_NEGRO)

    f_t = pygame.font.SysFont("Consolas", 36, bold=True)
    f_s = pygame.font.SysFont("Consolas", 22, bold=True)

    t = f_t.render(titulo, True, color)
    pantalla.blit(t, (W // 2 - t.get_width() // 2, H // 2 - 45))

    if subtitulo:
        s = f_s.render(subtitulo, True, C_BLANCO)
        pantalla.blit(s, (W // 2 - s.get_width() // 2, H // 2 + 15))

    pygame.display.flip()
    pygame.time.delay(int(segundos * 1000))


def mostrar_pantalla_carga(nombre_juego):
    """
    Muestra el mensaje de carga antes de iniciar un juego.

    Recibe el nombre del juego seleccionado y lo presenta como subtitulo.
    """
    mostrar_mensaje_centro("CARGANDO JUEGO...", nombre_juego, C_NEON, 0.7)


def asegurar_carpetas():
    """
    Verifica que existan las carpetas necesarias del proyecto.

    Crea, si hacen falta, las carpetas de ROMs de SNES, portadas de SNES y
    recursos generales para evitar errores al leer o copiar archivos.
    """
    os.makedirs(ROMS_SNES, exist_ok=True)
    os.makedirs(MEDIA_SNES, exist_ok=True)
    os.makedirs(MEDIA_GENERAL, exist_ok=True)


def obtener_juegos():
    """
    Lee la carpeta de ROMs de SNES y construye la lista de juegos disponibles.

    Solo toma archivos con extension .sfc o .smc. Para cada juego guarda su
    titulo, la ruta completa de la ROM y la ruta esperada de su portada PNG.
    """
    asegurar_carpetas()
    lista = []

    for archivo in sorted(os.listdir(ROMS_SNES)):
        if archivo.lower().endswith((".sfc", ".smc")):
            nombre = os.path.splitext(archivo)[0]
            img_p = os.path.join(MEDIA_SNES, nombre + ".png")

            lista.append({
                "titulo": nombre.upper(),
                "rom": os.path.join(ROMS_SNES, archivo),
                "img_path": img_p
            })

    return lista


def detectar_particion_usb():
    """
    Detecta dinamicamente la particion de una memoria USB.

    No se usa /dev/sda1 fijo porque Linux puede asignar la memoria como:
    /dev/sda1, /dev/sdb1, /dev/sdc1, etc.

    Regresa algo como "/dev/sdb1" o None si no hay USB.
    """
    try:
        resultado = subprocess.run(
            ["lsblk", "-J", "-p", "-o", "NAME,TYPE,TRAN,RM,MOUNTPOINTS"],
            capture_output=True,
            text=True,
            timeout=3
        )
    except Exception as e:
        print(f"Error ejecutando lsblk: {e}")
        return None

    if resultado.returncode != 0:
        return None

    try:
        import json
        datos = json.loads(resultado.stdout)
    except Exception as e:
        print(f"Error leyendo salida de lsblk: {e}")
        return None

    # Prioridad 1: si algo ya esta montado en /mnt/usb, usar ese dispositivo.
    for disco in datos.get("blockdevices", []):
        for hijo in disco.get("children", []) or []:
            puntos = hijo.get("mountpoints") or []
            if RUTA_USB in puntos:
                return hijo.get("name")

    # Prioridad 2: buscar discos USB/removibles y regresar su primera particion.
    for disco in datos.get("blockdevices", []):
        es_usb = disco.get("tran") == "usb"
        es_removible = str(disco.get("rm")) == "1"

        if not (es_usb or es_removible):
            continue

        # Si el disco tiene particiones, usar la primera particion.
        for hijo in disco.get("children", []) or []:
            if hijo.get("type") == "part":
                return hijo.get("name")

        # Si no tiene particiones, usar el disco directo. No es lo ideal,
        # pero permite algunas memorias formateadas sin tabla de particiones.
        if disco.get("type") == "disk":
            return disco.get("name")

    return None


def obtener_dispositivo_montado_en_usb():
    """
    Regresa el dispositivo montado actualmente en /mnt/usb.
    Por ejemplo: /dev/sda1 o /dev/sdb1.
    """
    try:
        resultado = subprocess.run(
            ["findmnt", "-n", "-o", "SOURCE", RUTA_USB],
            capture_output=True,
            text=True,
            timeout=3
        )
    except Exception:
        return None

    if resultado.returncode != 0:
        return None

    fuente = resultado.stdout.strip()
    return fuente if fuente else None


def intentar_desmontar_usb():
    """
    Intenta desmontar /mnt/usb para limpiar montajes viejos.
    Requiere sudoers para umount.
    """
    if not os.path.ismount(RUTA_USB):
        return True

    try:
        subprocess.run(
            ["sudo", "-n", "umount", RUTA_USB],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3
        )
    except Exception:
        return False

    return not os.path.ismount(RUTA_USB)


def intentar_montar_usb():
    """
    Detecta y monta dinamicamente la memoria USB en /mnt/usb.

    Requiere sudoers, recomendado:
    apolo ALL=(root) NOPASSWD: /usr/bin/mount /dev/sd?1 /mnt/usb
    apolo ALL=(root) NOPASSWD: /usr/bin/umount /mnt/usb
    """
    asegurar_carpetas()

    dispositivo = detectar_particion_usb()

    if dispositivo is None:
        return False

    montado_actual = obtener_dispositivo_montado_en_usb()

    # Si ya esta montado el mismo dispositivo y se puede leer, no hacemos nada.
    if os.path.ismount(RUTA_USB) and montado_actual == dispositivo:
        try:
            os.listdir(RUTA_USB)
            return True
        except Exception:
            # Montaje viejo o en mal estado: intentar desmontar y montar de nuevo.
            intentar_desmontar_usb()

    # Si /mnt/usb tiene montado otro dispositivo, desmontarlo antes de montar el nuevo.
    if os.path.ismount(RUTA_USB) and montado_actual != dispositivo:
        intentar_desmontar_usb()

    try:
        subprocess.run(
            ["sudo", "-n", "mount", dispositivo, RUTA_USB],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3
        )
    except Exception:
        return False

    return os.path.ismount(RUTA_USB)


def usb_lista():
    """
    Comprueba si hay una memoria USB montada y si contiene ROMs compatibles.

    Intenta montar la USB, revisa su contenido y regresa True si encuentra al
    menos un archivo .sfc o .smc. Si no hay USB o no hay juegos, regresa False.
    """
    if not intentar_montar_usb():
        return False

    try:
        archivos = os.listdir(RUTA_USB)
    except Exception:
        return False

    for archivo in archivos:
        if archivo.lower().endswith((".sfc", ".smc")):
            return True

    return False



def hay_contenido_nuevo_en_usb():
    """
    Revisa si la USB contiene ROMs o portadas que aun no estan
    copiadas en la microSD.

    Esto permite que PickaxeStation vuelva a sincronizar una USB
    aunque ya haya sido procesada antes, sin reiniciar la Raspberry.
    """
    if not usb_lista():
        return False

    try:
        archivos = os.listdir(RUTA_USB)
    except Exception:
        return False

    for archivo in archivos:
        if not archivo.lower().endswith((".sfc", ".smc")):
            continue

        origen_rom = os.path.join(RUTA_USB, archivo)
        destino_rom = os.path.join(ROMS_SNES, archivo)

        nombre_base = os.path.splitext(archivo)[0]
        origen_png = os.path.join(RUTA_USB, nombre_base + ".png")
        destino_png = os.path.join(MEDIA_SNES, nombre_base + ".png")

        # ROM nueva
        if os.path.exists(origen_rom) and not os.path.exists(destino_rom):
            return True

        # Portada nueva para un ROM ya existente
        if os.path.exists(origen_png) and not os.path.exists(destino_png):
            return True

    return False


def sincronizar_usb():
    """
    Copia desde la USB las ROMs y portadas nuevas hacia la microSD.

    Evita duplicar ROMs que ya existen, copia portadas PNG cuando estan
    disponibles y regresa tres contadores: ROMs copiadas, ROMs omitidas y
    portadas copiadas.
    """
    asegurar_carpetas()

    if not usb_lista():
        return (0, 0, 0)

    copiados = 0
    omitidos = 0
    portadas = 0

    for archivo in sorted(os.listdir(RUTA_USB)):
        if not archivo.lower().endswith((".sfc", ".smc")):
            continue

        origen_rom = os.path.join(RUTA_USB, archivo)
        destino_rom = os.path.join(ROMS_SNES, archivo)

        nombre_base = os.path.splitext(archivo)[0]
        origen_png = os.path.join(RUTA_USB, nombre_base + ".png")
        destino_png = os.path.join(MEDIA_SNES, nombre_base + ".png")

        try:
            if os.path.exists(destino_rom):
                omitidos += 1
            else:
                shutil.copy2(origen_rom, destino_rom)
                copiados += 1

            if os.path.exists(origen_png) and not os.path.exists(destino_png):
                shutil.copy2(origen_png, destino_png)
                portadas += 1

        except Exception as e:
            print(f"Error copiando {archivo}: {e}")

    return (copiados, omitidos, portadas)


def reproducir_sonido_mover():
    """
    Reproduce el efecto de sonido al mover la seleccion del menu.

    Si el audio no esta disponible o ocurre un error, el programa continua sin
    detenerse.
    """
    if sonido_mover:
        try:
            sonido_mover.play()
        except Exception as e:
            print(f"No se pudo reproducir sonido: {e}")


def mover_derecha():
    """
    Avanza la seleccion al siguiente juego disponible.

    La seleccion es circular: despues del ultimo juego vuelve al primero.
    Tambien reproduce el sonido de movimiento.
    """
    global indice
    if juegos:
        indice = (indice + 1) % len(juegos)
        reproducir_sonido_mover()


def mover_izquierda():
    """
    Regresa la seleccion al juego anterior disponible.

    La seleccion es circular: antes del primer juego pasa al ultimo. Tambien
    reproduce el sonido de movimiento.
    """
    global indice
    if juegos:
        indice = (indice - 1) % len(juegos)
        reproducir_sonido_mover()


def sincronizar_y_actualizar(mensaje_inicial="USB DETECTADA"):
    """
    Sincroniza la USB y actualiza la biblioteca mostrada en el menu.

    Muestra mensajes de estado, copia ROMs y portadas nuevas, recarga la lista
    de juegos y ajusta el indice de seleccion para que siga siendo valido.
    """
    global juegos, indice, usb_procesada

    mostrar_mensaje_centro(mensaje_inicial, "SINCRONIZANDO BIBLIOTECA...", C_NEON, 0.8)

    copiados, omitidos, portadas = sincronizar_usb()
    juegos = obtener_juegos()

    if indice >= len(juegos):
        indice = max(0, len(juegos) - 1)

    resumen = f"NUEVOS: {copiados} | OMITIDOS: {omitidos} | PORTADAS: {portadas}"
    mostrar_mensaje_centro("SINCRONIZACION COMPLETA", resumen, C_VERDE, 1.7)

    usb_procesada = True



def abrir_joystick_linux():
    """
    Abre el dispositivo joystick de Linux para leer botones mientras Mednafen corre.

    Pygame controla el gamepad dentro del menu, pero durante el juego Mednafen
    toma la pantalla y el menu queda monitoreando por fuera. Por eso aqui se lee
    directamente /dev/input/js0, /dev/input/js1, etc.
    """
    for i in range(4):
        ruta = f"/dev/input/js{i}"
        if os.path.exists(ruta):
            try:
                return os.open(ruta, os.O_RDONLY | os.O_NONBLOCK)
            except OSError as e:
                print(f"No se pudo abrir {ruta}: {e}")

    return None


def leer_botones_joystick_linux(fd, estado_botones):
    """
    Lee eventos del joystick Linux.

    Formato js_event:
    unsigned int time, short value, unsigned char type, unsigned char number

    type == 1 corresponde a botones.
    value == 1 presionado, value == 0 liberado.
    """
    if fd is None:
        return estado_botones

    while True:
        try:
            data = os.read(fd, 8)
            if len(data) < 8:
                break

            _tiempo, valor, tipo, numero = struct.unpack("IhBB", data)

            # Quitar bandera JS_EVENT_INIT si viene marcada.
            tipo = tipo & ~0x80

            # JS_EVENT_BUTTON = 0x01
            if tipo == 0x01:
                estado_botones[numero] = valor

        except BlockingIOError:
            break
        except OSError:
            raise

    return estado_botones


def combinacion_regresar_menu(estado_botones):
    """
    Combinacion elegida:
    Share + Options = regresar al menu principal.
    """
    return (
        estado_botones.get(BOTON_SHARE_PS4, 0) == 1 and
        estado_botones.get(BOTON_OPTIONS_PS4, 0) == 1
    )



def ejecutar_comando_sistema(comando, titulo):
    """
    Ejecuta una accion del sistema desde PickaxeStation.
    Requiere sudoers para poweroff/reboot sin contrasena.
    """
    mostrar_mensaje_centro(titulo, "ESPERE UN MOMENTO...", C_NEON, 1.0)

    try:
        subprocess.Popen(
            ["sudo", "-n", comando],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"No se pudo ejecutar {comando}: {e}")
        mostrar_mensaje_centro("ERROR", "NO SE PUDO EJECUTAR LA ACCION", C_ROJO, 1.4)


def dibujar_borde_igual(x, y, ancho, alto):
    """
    Dibuja borde tipo consola con '=' solo arriba y abajo.
    """
    f_borde = pygame.font.SysFont("Consolas", 24, bold=True)
    linea = "=" * max(12, ancho // 14)

    texto_sup = f_borde.render(linea, True, C_NEON)
    texto_inf = f_borde.render(linea, True, C_NEON)

    pantalla.blit(texto_sup, (W // 2 - texto_sup.get_width() // 2, y))
    pantalla.blit(texto_inf, (W // 2 - texto_inf.get_width() // 2, y + alto - 32))


def mostrar_menu_sistema():
    """
    Menu de sistema abierto con Options desde el menu principal.

    Se puede usar de dos formas:
    - Botones directos:
      X = apagar, Triangulo = reiniciar, Circulo = cancelar.
    - Selector:
      Arriba/abajo para moverse, X para confirmar, Circulo para cancelar.
    """
    global pantalla

    f_t = pygame.font.SysFont("Consolas", 36, bold=True)
    f_m = pygame.font.SysFont("Consolas", 24, bold=True)
    f_s = pygame.font.SysFont("Consolas", 18, bold=True)

    opciones = [
        ("APAGAR CONSOLA", "apagar"),
        ("REINICIAR CONSOLA", "reiniciar"),
        ("CANCELAR Y VOLVER", "cancelar"),
    ]
    seleccion = 0

    while True:
        if img_fondo:
            pantalla.blit(img_fondo, (0, 0))
        else:
            pantalla.fill(C_FONDO)

        oscurecer_fondo(180)

        ancho = min(860, W - 80)
        alto = 380
        x = W // 2 - ancho // 2
        y = H // 2 - alto // 2

        panel = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 220))
        pantalla.blit(panel, (x, y))

        dibujar_borde_igual(x + 20, y + 20, ancho - 40, alto - 40)

        titulo = "PickaxeStation"
        dibujar_texto_con_sombra(
            pantalla,
            titulo,
            f_t,
            C_NEON,
            (W // 2 - f_t.size(titulo)[0] // 2, y + 68)
        )

        yy = y + 145
        etiquetas = [
            "X          APAGAR CONSOLA",
            "TRIANGULO  REINICIAR CONSOLA",
            "CIRCULO    CANCELAR Y VOLVER",
        ]

        for i, etiqueta in enumerate(etiquetas):
            color = C_NEON if i == seleccion else C_BLANCO
            prefijo = "> " if i == seleccion else "  "
            linea = prefijo + etiqueta

            dibujar_texto_con_sombra(
                pantalla,
                linea,
                f_m,
                color,
                (W // 2 - f_m.size(linea)[0] // 2, yy)
            )
            yy += 54

        ayuda = "D-Pad mueve | X confirma | Circulo cancela"
        dibujar_texto_con_sombra(
            pantalla,
            ayuda,
            f_s,
            C_GRIS,
            (W // 2 - f_s.size(ayuda)[0] // 2, y + alto - 75)
        )

        pygame.display.flip()
        reloj.tick(30)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return "cancelar"

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return "cancelar"
                elif ev.key == pygame.K_UP:
                    seleccion = (seleccion - 1) % len(opciones)
                elif ev.key == pygame.K_DOWN:
                    seleccion = (seleccion + 1) % len(opciones)
                elif ev.key == pygame.K_RETURN:
                    return opciones[seleccion][1]
                elif ev.key == pygame.K_x:
                    return "apagar"
                elif ev.key == pygame.K_r:
                    return "reiniciar"

            if ev.type == pygame.JOYDEVICEADDED:
                refrescar_controles("control conectado en menu sistema")

            if ev.type == pygame.JOYDEVICEREMOVED:
                refrescar_controles("control desconectado en menu sistema")

            if ev.type == pygame.JOYHATMOTION:
                _x, yhat = ev.value
                if yhat == 1:
                    seleccion = (seleccion - 1) % len(opciones)
                elif yhat == -1:
                    seleccion = (seleccion + 1) % len(opciones)

            if ev.type == pygame.JOYBUTTONDOWN:
                print(f"Menu sistema boton: {ev.button}")

                # Botones directos
                if ev.button == BOTON_TRIANGULO_PS4:
                    return "reiniciar"
                elif ev.button == BOTON_CIRCULO_PS4:
                    return "cancelar"

                # X confirma la opcion seleccionada. Si el selector esta en
                # APAGAR, apaga; si esta en REINICIAR, reinicia; si esta en
                # CANCELAR, regresa.
                elif ev.button == BOTON_X_PS4:
                    return opciones[seleccion][1]

                # Fallback por si el control reporta D-Pad como botones.
                elif ev.button == 13:
                    seleccion = (seleccion - 1) % len(opciones)
                elif ev.button == 14:
                    seleccion = (seleccion + 1) % len(opciones)

def lanzar_juego():
    """
    Lanza Mednafen y monitorea eventos externos mientras el juego corre.

    Durante el juego permite:
    - detectar USB con contenido nuevo
    - cerrar Mednafen y sincronizar biblioteca
    - regresar al menu con Share + Options del control PS4
    """
    global pantalla, juegos, indice, usb_procesada, bloquear_options_hasta_suelta

    if not juegos:
        return

    rom = juegos[indice]["rom"]
    titulo = juegos[indice]["titulo"]

    print(f"Lanzando {rom}")

    mostrar_pantalla_carga(titulo)
    os.system("clear")

    pygame.display.quit()

    if pygame.mixer.get_init():
        pygame.mixer.pause()

    usb_detectada_durante_juego = False
    salida_por_control = False
    estado_botones = {}
    js_fd = abrir_joystick_linux()
    ultimo_intento_js = pygame.time.get_ticks()

    try:
        with open(os.devnull, "w") as devnull:
            proceso = subprocess.Popen(
                ["mednafen", rom],
                stdout=devnull,
                stderr=devnull
            )

            while proceso.poll() is None:
                # 1) USB nueva durante el juego
                if hay_contenido_nuevo_en_usb():
                    usb_detectada_durante_juego = True
                    print("USB detectada durante el juego. Cerrando Mednafen...")

                    proceso.terminate()
                    try:
                        proceso.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        proceso.kill()

                    break

                # 2) Share + Options para regresar al menu
                try:
                    estado_botones = leer_botones_joystick_linux(js_fd, estado_botones)

                    if combinacion_regresar_menu(estado_botones):
                        salida_por_control = True
                        print("Share + Options detectado. Regresando al menu...")

                        proceso.terminate()
                        try:
                            proceso.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            proceso.kill()

                        break

                except OSError:
                    # Si el control se desconecto durante el juego, intentamos reabrirlo
                    # por si vuelve a conectarse.
                    try:
                        if js_fd is not None:
                            os.close(js_fd)
                    except Exception:
                        pass
                    js_fd = None
                    estado_botones = {}

                # Reintentar abrir joystick si no estaba disponible.
                ahora = pygame.time.get_ticks()
                if js_fd is None and ahora - ultimo_intento_js > 1000:
                    js_fd = abrir_joystick_linux()
                    ultimo_intento_js = ahora

                pygame.time.delay(80)

    except FileNotFoundError:
        print("Error: Mednafen no esta instalado o no esta en PATH.")
        print("Instala con: sudo apt install -y mednafen")

    except Exception as e:
        print(f"Error al lanzar el juego: {e}")

    finally:
        try:
            if js_fd is not None:
                os.close(js_fd)
        except Exception:
            pass

    os.system("clear")

    pygame.display.init()
    pantalla = pygame.display.set_mode((W, H), pygame.NOFRAME)

    if pygame.mixer.get_init():
        pygame.mixer.unpause()

    refrescar_controles("regreso desde juego")

    if usb_detectada_durante_juego:
        sincronizar_y_actualizar("USB DETECTADA DURANTE JUEGO")
    elif salida_por_control:
        bloquear_options_hasta_suelta = True
        pygame.event.clear()
        mostrar_mensaje_centro("REGRESANDO AL MENU", "SHARE + OPTIONS", C_NEON, 0.8)



def refrescar_controles(motivo=""):
    """
    Actualiza la lista de controles sin reiniciar todo el subsistema.

    Importante: no usamos pygame.joystick.quit() aqui, porque al hacerlo
    dentro de JOYDEVICEADDED se puede generar un ciclo de eventos y dejar
    la pantalla atorada en "CONTROL CONECTADO".
    """
    global controles

    try:
        if not pygame.joystick.get_init():
            pygame.joystick.init()

        nuevos = []
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            if not joy.get_init():
                joy.init()
            nuevos.append(joy)

        controles = nuevos

        if motivo:
            print(f"Controles actualizados por: {motivo} | total={len(controles)}")

        for joy in controles:
            try:
                print(f"Control activo: {joy.get_name()}")
            except Exception:
                pass

    except Exception as e:
        print(f"Error refrescando controles: {e}")


def control_conectado():
    """
    Regresa True si Pygame tiene al menos un joystick activo.
    Si ocurre algun problema, intenta refrescar la lista.
    """
    try:
        return pygame.joystick.get_count() > 0
    except Exception:
        refrescar_controles("verificacion")
        return pygame.joystick.get_count() > 0


f_info = pygame.font.SysFont("Consolas", 16, bold=True)
f_main = pygame.font.SysFont("Consolas", 26, bold=True)
f_titulo = pygame.font.SysFont("Consolas", 38, bold=True)

controles = []
refrescar_controles("inicio del menu")

juegos = obtener_juegos()
indice = 0
ejecutando = True
usb_procesada = False
ultimo_refresco_control = 0
bloquear_options_hasta_suelta = False

print(f"Juegos encontrados: {len(juegos)}")
print("USB esperada en /mnt/usb")
print("PS4: D-Pad mueve, X lanza, Options abre menu de sistema")
print("Dentro del juego: Share + Options regresa al menu")


while ejecutando:
    # Refresco ligero cada 2 segundos por si el control fue reconectado
    # y el evento hotplug no llego completo en KMS/DRM.
    ahora_ticks = pygame.time.get_ticks()
    if ahora_ticks - ultimo_refresco_control > 2000:
        refrescar_controles("revision periodica")
        ultimo_refresco_control = ahora_ticks

    if hay_contenido_nuevo_en_usb():
        sincronizar_y_actualizar("USB DETECTADA")

    elif detectar_particion_usb() is None:
        usb_procesada = False

    if img_fondo:
        pantalla.blit(img_fondo, (0, 0))
    else:
        pantalla.fill(C_FONDO)

    oscurecer_fondo(80)

    dibujar_panel(pantalla, 30, 30, 560, 180)
    dibujar_texto_con_sombra(pantalla, "PROYECTO: CONSOLA RETRO - PICKAXESTATION", f_info, C_NEON, (50, 50))
    dibujar_texto_con_sombra(pantalla, "MATERIA: FUNDAMENTOS DE SISTEMAS EMBEBIDOS", f_info, C_NEON, (50, 75))
    dibujar_texto_con_sombra(pantalla, "EQUIPO: BRIGADA 04", f_info, C_NEON, (50, 100))
    dibujar_texto_con_sombra(pantalla, "REYES ROQUE / VAZQUEZ A. / ALMODOVAR", f_info, C_BLANCO, (50, 150))

    dibujar_panel(pantalla, W - 510, 30, 480, 130)
    hora = datetime.now().strftime("%I:%M:%S %p")
    dibujar_texto_con_sombra(pantalla, f"SYSTEM TIME: {hora}", f_main, C_NEON, (W - 480, 60))

    controles_ready = control_conectado()
    estado = "GAMEPAD: READY" if controles_ready else "GAMEPAD: NOT FOUND"
    color_estado = C_VERDE if controles_ready else C_ROJO
    dibujar_texto_con_sombra(pantalla, estado, f_info, color_estado, (W - 480, 105))

    if img_logo:
        pantalla.blit(img_logo, (W // 2 - 300, -20))
    else:
        texto_logo = "PICKAXESTATION"
        dibujar_texto_con_sombra(
            pantalla,
            texto_logo,
            f_titulo,
            C_NEON,
            (W // 2 - f_titulo.size(texto_logo)[0] // 2, 70)
        )

    if juegos:
        j = juegos[indice]
        rect_c = pygame.Rect(W // 2 - 175, H // 2 - 40, 350, 350)
        dibujar_panel(pantalla, rect_c.x, rect_c.y, rect_c.width, rect_c.height, 4)

        img_j = None
        if os.path.exists(j["img_path"]):
            try:
                img_j = pygame.image.load(j["img_path"]).convert_alpha()
                img_j = pygame.transform.smoothscale(img_j, (340, 340))
            except Exception as e:
                print(f"Error cargando portada {j['img_path']}: {e}")
                img_j = None

        if img_j:
            pantalla.blit(img_j, (rect_c.x + 5, rect_c.y + 5))
        elif img_default:
            pantalla.blit(img_default, (rect_c.x + 5, rect_c.y + 5))
        else:
            pygame.draw.rect(pantalla, (35, 35, 35), (rect_c.x + 5, rect_c.y + 5, 340, 340))
            dibujar_texto_con_sombra(
                pantalla,
                "SIN PORTADA",
                f_main,
                C_NEON,
                (W // 2 - f_main.size("SIN PORTADA")[0] // 2, rect_c.y + 155)
            )

        tit = j["titulo"]
        dibujar_texto_con_sombra(
            pantalla,
            tit,
            f_titulo,
            C_BLANCO,
            (W // 2 - f_titulo.size(tit)[0] // 2, rect_c.bottom + 20)
        )

        info_g = f"GAME {indice + 1} OF {len(juegos)}"
        dibujar_texto_con_sombra(
            pantalla,
            info_g,
            f_main,
            C_NEON,
            (W // 2 - f_main.size(info_g)[0] // 2, rect_c.bottom + 70)
        )

    else:
        msg = "NO HAY JUEGOS SNES"
        dibujar_texto_con_sombra(
            pantalla,
            msg,
            f_titulo,
            C_BLANCO,
            (W // 2 - f_titulo.size(msg)[0] // 2, H // 2)
        )

    # Barra inferior de controles para el usuario.
    barra_h = 64
    barra = pygame.Surface((W, barra_h), pygame.SRCALPHA)
    barra.fill((0, 0, 0, 220))
    pantalla.blit(barra, (0, H - barra_h))

    ayuda_menu = "< / > MOVER      X JUGAR      OPTIONS SALIR"
    fuente_ayuda = pygame.font.SysFont("Consolas", 24, bold=True)
    dibujar_texto_con_sombra(
        pantalla,
        ayuda_menu,
        fuente_ayuda,
        C_NEON,
        (W // 2 - fuente_ayuda.size(ayuda_menu)[0] // 2, H - 43)
    )

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            ejecutando = False

        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                ejecutando = False
            elif ev.key == pygame.K_RIGHT:
                mover_derecha()
            elif ev.key == pygame.K_LEFT:
                mover_izquierda()
            elif ev.key == pygame.K_RETURN:
                lanzar_juego()

        if ev.type == pygame.JOYDEVICEADDED:
            refrescar_controles("control conectado")

        if ev.type == pygame.JOYDEVICEREMOVED:
            refrescar_controles("control desconectado")

        if ev.type == pygame.JOYBUTTONUP:
            if ev.button == BOTON_OPTIONS_PS4:
                bloquear_options_hasta_suelta = False

        if ev.type == pygame.JOYBUTTONDOWN:
            print(f"Boton presionado: {ev.button}")

            if ev.button == BOTON_X_PS4:
                lanzar_juego()
            elif ev.button == BOTON_OPTIONS_PS4:
                if bloquear_options_hasta_suelta:
                    print("Options ignorado despues de regresar del juego")
                else:
                    accion = mostrar_menu_sistema()

                    if accion == "apagar":
                        ejecutar_comando_sistema("/usr/sbin/poweroff", "APAGANDO CONSOLA")
                    elif accion == "reiniciar":
                        ejecutar_comando_sistema("/usr/sbin/reboot", "REINICIANDO CONSOLA")
                    # cancelar: no hacer nada y volver al menu principal
            elif ev.button == 14:
                mover_derecha()
            elif ev.button == 13:
                mover_izquierda()

        if ev.type == pygame.JOYHATMOTION:
            print(f"HAT movimiento: {ev.value}")
            x, y = ev.value

            if x == 1:
                mover_derecha()
            elif x == -1:
                mover_izquierda()

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
