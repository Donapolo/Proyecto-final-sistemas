# PickaxeStation

**Consola retro sobre Raspberry Pi 3 Model B | Raspberry Pi OS Lite | Python, Pygame y Mednafen**

> Documentación contrastada con el archivo `menu.py` actual entregado para esta revisión. El código del menú no se modificó.

## 1. Descripción general

PickaxeStation es un sistema embebido dedicado a la ejecución de videojuegos retro. Funciona sobre una **Raspberry Pi 3 Model B (Rev. 1.2)** con **Raspberry Pi OS Lite de 64 bits** y una interfaz gráfica propia desarrollada en **Python y Pygame**, sin utilizar un entorno de escritorio ni distribuciones retro preconfiguradas como RetroPie, Batocera o Recalbox.

**PickaxeStation no es un emulador desarrollado desde cero.** Es una aplicación que administra la interfaz, la biblioteca de juegos, las entradas del control, las memorias USB y la ejecución de herramientas externas. Para reproducir videojuegos de **Super Nintendo (SNES)**, utiliza **Mednafen** como motor de emulación. **MPV** se encarga de reproducir el video de introducción.

La implementación documentada aquí corresponde a la versión funcional comprobada en Raspberry Pi 3B. La presencia de referencias a otras plataformas o emuladores en versiones anteriores del repositorio no significa que estén integrados en esta configuración.

### Funcionalidades verificadas

- Inicio automático de la consola al encender la Raspberry Pi.
- Reproducción de video introductorio y audio.
- Menú personalizado a pantalla completa mediante Pygame y DRM/KMS.
- Biblioteca de ROMs SNES y visualización de portadas.
- Navegación con control tipo PS4 y asignación de botones en Mednafen.
- Ejecución de juegos, salida mediante **Share + Options** y regreso al menú.
- Detección dinámica de particiones USB mediante `lsblk`, incorporación de ROMs `.sfc`/`.smc` y asociación de portadas `.png`; puede sincronizar contenido nuevo incluso mientras se ejecuta un juego.
- Apagado y reinicio desde el menú mediante permisos específicos.
- Transiciones de fundido a negro al lanzar juegos y al regresar al menú.
- Ejecución sin X11, Wayland ni un escritorio gráfico convencional.

## 2. Objetivo y relación con sistemas embebidos

El objetivo es implementar una consola de propósito específico que integre **hardware, sistema operativo y aplicación**. La Raspberry Pi ejecuta una función dedicada; Linux proporciona los controladores de pantalla, audio, almacenamiento y entrada, mientras que la aplicación organiza la interacción del usuario.

| Unidad | Aplicación en PickaxeStation |
|---|---|
| U1. Introducción | Problema definido: ofrecer una consola retro autónoma y operable con un gamepad. |
| U2. Arquitectura | Plataforma ARM; uso de USB, salida HDMI, red, microSD y dispositivos de entrada. |
| U3. Sistema operativo | Raspberry Pi OS Lite, controladores Linux, procesos externos y arranque con `systemd`. |
| U4. Programación | Python/Pygame, funciones de interfaz y control, `subprocess`, comprobación de errores y depuración. |
| U5. Integración | Funcionamiento conjunto de la Raspberry, Linux, el menú, Mednafen y los periféricos. |

**Elección del lenguaje.** Se utilizó Python por la experiencia adquirida durante las prácticas y proyectos del semestre anterior, por su facilidad para desarrollar y depurar el programa, y por la disponibilidad de bibliotecas como Pygame. El módulo `subprocess` permite coordinar aplicaciones externas y comandos de Linux. Esta elección facilitó concentrar el trabajo en la integración del sistema; no implica que Python sustituya a los controladores de hardware del kernel.

## 3. Hardware y conexiones

### Materiales utilizados

| Componente | Uso |
|---|---|
| Raspberry Pi 3 Model B (Rev. 1.2) | Unidad principal de procesamiento. |
| MicroSD (se recomienda 32 GB) | Sistema operativo, programa y biblioteca de juegos. |
| Fuente de alimentación compatible con Raspberry Pi 3B | Energía mediante micro-USB. |
| Control tipo PS4 / DualShock 4 | Navegación y control de videojuegos mediante USB. |
| Pantalla HDMI o capturadora HDMI | Salida de imagen y sonido. |
| PC con OBS (opcional) | Visualización y captura de la salida HDMI. |
| Memoria USB (opcional) | Incorporación de ROMs y sus portadas. |
| Ethernet o Wi-Fi | Administración y conexión SSH. |

### Esquema de conexiones

```text
                         Red local / SSH
                               |
                               v
 Control PS4 -- USB --> +-----------------------+ -- HDMI / audio --> Pantalla
                        | Raspberry Pi 3B       |                       |
 Memoria USB -- USB --> | Raspberry Pi OS Lite  |                       +--> Capturadora HDMI
                        | Python / Pygame       |                                |
  Fuente 5.1 V -------> | MPV / Mednafen        |                                +--> PC / OBS (USB)
     micro-USB          +-----------------------+
                               |
                         MicroSD del sistema
```

La capturadora HDMI y OBS se utilizan para visualizar o registrar la demostración; no son necesarios si la Raspberry está conectada directamente a un monitor o televisión HDMI.

## 4. Software y arquitectura

| Componente | Función |
|---|---|
| Raspberry Pi OS Lite 64 bits | Sistema operativo Linux sin escritorio. |
| Python 3 y Pygame 2 | Lógica del menú, imágenes, audio de navegación y eventos de control. |
| SDL con `kmsdrm` | Salida de la aplicación gráfica mediante DRM/KMS. |
| MPV | Reproducción de `boot/intro.mp4` mediante salida DRM. |
| Mednafen | Emulación de videojuegos SNES. |
| ALSA | Administración de dispositivos de sonido. |
| `lsblk`, `findmnt`, `mount`, `umount` | Detección, verificación y montaje del almacenamiento USB. |
| `systemd` | Ejecución automática del script de inicio. |
| `sudoers` y `pickaxe-usb` | Autorización limitada para tareas privilegiadas. |

### Organización del software

1. **`start_pickaxestation.sh`** prepara la terminal, configura SDL, reproduce la introducción y abre el menú.
2. **`menu/menu.py`** administra imágenes, portadas, biblioteca de ROMs SNES, audio del menú, eventos de control y menú de apagado/reinicio.
3. **Mednafen** se lanza mediante `subprocess.Popen(["mednafen", rom])`. Mientras se ejecuta, el menú supervisa el control desde `/dev/input/js*` y comprueba si existen juegos nuevos en USB. Si detecta **Share + Options** o nuevos archivos, termina el proceso y recupera la pantalla.
4. El menú detecta dispositivos con `lsblk -J -p -o NAME,TYPE,TRAN,RM,MOUNTPOINTS` y verifica montajes con `findmnt`. Utiliza el auxiliar restringido `/usr/local/sbin/pickaxe-usb` para montar o desmontar en `/mnt/usb`.
5. Las ROMs se sincronizan desde la raíz de la memoria USB a `roms/snes/` y las portadas con el mismo nombre base a `media/snes/`, sin duplicar archivos existentes; una portada ausente se sustituye visualmente por `media/Default.png` cuando está disponible.
6. **`systemd`** inicia el sistema automáticamente tras el arranque de Linux.

## 5. Código fuente y estructura

Repositorio original del proyecto:

```bash
git clone https://github.com/Donapolo/Proyecto-final-sistemas.git
```

Estructura observada en los archivos del proyecto:

```text
Proyecto-final-sistemas/
├── boot/
│   └── intro.mp4
├── menu/
│   ├── menu.py
│   ├── fondo.png
│   ├── logo.jpeg / logo.jpg / logo.png
│   └── mover.wav
├── media/
│   ├── Default.png
│   └── snes/
│       └── [portadas .png]
├── roms/
│   └── snes/
│       └── [ROMs .sfc/.smc]
├── scripts/
│   └── start_pickaxestation.sh
├── LICENSE
└── README.md
```

En la instalación funcional, los archivos ejecutados se encuentran en **`/home/apolo/pickaxestation/`** y el script de inicio se ubicó directamente en su raíz. Además existen configuraciones **fuera del repositorio**, en `/etc/systemd/system/`, `/etc/sudoers.d/`, `/usr/local/sbin/` y `~/.mednafen/`. Para reproducir fielmente la instalación deben incluirse sus copias revisadas en el paquete de entrega; **no basta con clonar el repositorio original**.

> **Importante:** los pasos siguientes documentan cómo se preparó el sistema. En la Raspberry ya configurada no es necesario volver a instalarlos; antes de realizar cambios conviene hacer un respaldo de la microSD.

## 6. Instalación y preparación del entorno

### 6.1. Instalar y configurar Raspberry Pi OS Lite

1. Grabar **Raspberry Pi OS Lite de 64 bits** en la microSD mediante Raspberry Pi Imager.
2. Configurar el usuario del equipo (en la instalación documentada: `apolo`), la red y el acceso SSH.
3. Iniciar la Raspberry y conectarse por terminal o SSH.

En una instalación que conserve el nombre `Apolo`, se puede intentar:

```powershell
ssh apolo@Apolo.local
```

El nombre `.local` puede requerir resolución mDNS en la computadora cliente. Si no funciona, utilizar la IP asignada por el router; esta dirección **no es fija**.

Comprobar la arquitectura y el sistema:

```bash
uname -m
cat /etc/os-release
```

La instalación probada utilizó Raspberry Pi OS Lite de 64 bits, basado en Debian 13 (Trixie), sobre arquitectura `aarch64`.

### 6.2. Instalar dependencias

Con la Raspberry conectada a Internet:

```bash
sudo apt update
sudo apt install -y git python3 python3-pygame mpv mednafen \
    alsa-utils util-linux sudo
```

Comprobar que las herramientas principales están disponibles:

```bash
python3 --version
python3 -c 'import pygame; print(pygame.version.ver)'
command -v mpv
command -v mednafen
ls -l /dev/dri/card0
```

En la instalación probada, Mednafen se encontraba en `/usr/games/mednafen`. Si `command -v mednafen` no lo encuentra en una terminal interactiva, verificar:

```bash
ls -l /usr/games/mednafen
```

### 6.3. Preparar los directorios de ejecución

Los siguientes comandos corresponden a una **instalación nueva** con el usuario `apolo`:

```bash
cd /home/apolo
git clone https://github.com/Donapolo/Proyecto-final-sistemas.git
mkdir -p /home/apolo/pickaxestation
cp -a Proyecto-final-sistemas/boot Proyecto-final-sistemas/menu \
      Proyecto-final-sistemas/media Proyecto-final-sistemas/roms \
      /home/apolo/pickaxestation/
cp Proyecto-final-sistemas/scripts/start_pickaxestation.sh \
   /home/apolo/pickaxestation/start_pickaxestation.sh
sed -i 's/\r$//' /home/apolo/pickaxestation/start_pickaxestation.sh
chmod +x /home/apolo/pickaxestation/start_pickaxestation.sh
sudo mkdir -p /mnt/usb
```

La corrección `sed` evita errores si el script fue editado previamente con finales de línea de Windows (CRLF). La creación del punto de montaje `/mnt/usb` requiere permisos administrativos.

Comprobar la sintaxis:

```bash
bash -n /home/apolo/pickaxestation/start_pickaxestation.sh
python3 -m py_compile /home/apolo/pickaxestation/menu/menu.py
```

### 6.4. Video sin escritorio y audio

El script de inicio incluye las variables empleadas para la salida gráfica:

```bash
export SDL_VIDEODRIVER=kmsdrm
export SDL_RENDER_DRIVER=software
export SDL_KMSDRM_DEVICE=/dev/dri/card0
```

MPV reproduce el archivo de introducción por DRM y ALSA:

```bash
mpv --fs --no-terminal --really-quiet \
    --vo=drm --ao=alsa --audio-device=alsa/default \
    /home/apolo/pickaxestation/boot/intro.mp4
```

La disponibilidad del dispositivo de audio depende de la configuración HDMI y de ALSA. Para diagnosticar:

```bash
aplay -l
```

Durante las pruebas se utilizó también `--audio-device=alsa/plughw:1,0` para seleccionar explícitamente el dispositivo HDMI. El menú Pygame tiene su propia configuración de salida de audio en `menu.py`; no debe confundirse con la de MPV.

### 6.5. Ajustar Mednafen para SNES

Después de la primera ejecución de Mednafen, editar `~/.mednafen/mednafen.cfg` y verificar estas opciones:

```ini
snes.stretch aspect
video.fs 1
```

Permiten conservar la proporción de pantalla y abrir el emulador en pantalla completa. En la versión probada también fue necesario configurar los botones del control PS4 dentro de Mednafen. El menú y el emulador gestionan las entradas de forma independiente.

### 6.6. Permisos y detección USB: dificultad y solución

Una de las principales dificultades fue que **Linux podía asignar diferentes nombres a la partición USB** (`/dev/sda1`, `/dev/sdb1`, etc.). También se presentaron **errores de permisos al montar y desmontar** unidades desde una aplicación que se ejecutaba como usuario normal.

La solución integrada en la consola consistió en:

1. Detectar los discos y particiones mediante `lsblk` (salida JSON) y consultar montajes con `findmnt`.
2. Utilizar un auxiliar privilegiado en **`/usr/local/sbin/pickaxe-usb`** que valida la operación y el origen USB antes de montar o desmontar en `/mnt/usb`.
3. Autorizar **solo dicho auxiliar** con una regla específica de `sudoers`, evitando conceder permisos administrativos generales al menú.
4. Montar la memoria de forma restrictiva y en modo de solo lectura antes de copiar las ROMs y portadas hacia la biblioteca local.

En la instalación funcional se utilizó esta regla en `/etc/sudoers.d/pickaxestation-usb`:

```sudoers
apolo ALL=(root) NOPASSWD: /usr/local/sbin/pickaxe-usb
```

En **`menu.py`**, las llamadas de montaje y desmontaje de la versión funcional utilizaron el auxiliar, de la siguiente forma:

```python
["sudo", "-n", "/usr/local/sbin/pickaxe-usb", "mount", dispositivo, RUTA_USB]
["sudo", "-n", "/usr/local/sbin/pickaxe-usb", "umount", RUTA_USB]
```

**Verificación en el `menu.py` actual:** las funciones `intentar_montar_usb()` e `intentar_desmontar_usb()` **ya llaman** a `/usr/local/sbin/pickaxe-usb`; no es necesario aplicar otra vez esos cambios al menú. El programa requiere que el ejecutable real y la regla de `sudoers` estén instalados en la Raspberry. Para una instalación nueva, debe acompañarse una copia revisada del auxiliar; **su contenido no está incluido en el archivo `menu.py`**. No se recomienda sustituirlo por permisos generales de `mount`/`umount`.

Es recomendable incorporar al paquete de entrega las copias revisadas de:

```text
config/pickaxe-usb
config/pickaxestation-usb.sudoers
config/pickaxestation-power.sudoers
config/pickaxestation.service
config/mednafen.cfg       (solo opciones pertinentes, sin datos privados)
```

Las reglas de `sudoers` se editan o validan con `visudo`. Las modificaciones requieren permisos administrativos y deben revisarse antes de aplicarse en otra Raspberry.

En la instalación funcional se habilitaron, por separado, las operaciones de apagar y reiniciar mediante:

```sudoers
apolo ALL=(root) NOPASSWD: /usr/sbin/poweroff, /usr/sbin/reboot
```

Después de conectar una memoria USB con una ROM `.sfc` o `.smc` y, opcionalmente, una portada `.png` con el mismo nombre base, el menú verifica su contenido y copia los archivos nuevos. Si una memoria se conecta mientras Mednafen está ejecutándose y contiene material pendiente de sincronización, el menú termina el juego y actualiza la biblioteca. La memoria se puede conectar en distintos puertos USB; no se fija el nombre de partición.

**Ejemplo de nombres:** `Juego.sfc` y `Juego.png`. La implementación probada busca los archivos compatibles en la raíz de la memoria USB.

### 6.7. Inicio automático mediante systemd

Se configuró el servicio **`/etc/systemd/system/pickaxestation.service`** para ejecutar el script al iniciar la Raspberry, desde la primera terminal virtual, sin escritorio:

```ini
[Unit]
Description=PickaxeStation - Consola Retro
After=systemd-user-sessions.service
Conflicts=getty@tty1.service
After=getty@tty1.service

[Service]
Type=simple
User=apolo
Group=apolo
WorkingDirectory=/home/apolo/pickaxestation
Environment=HOME=/home/apolo
Environment=TERM=linux
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games
PAMName=login
TTYPath=/dev/tty1
StandardInput=tty
StandardOutput=journal
StandardError=journal
TTYReset=yes
TTYVHangup=yes
ExecStart=/bin/bash /home/apolo/pickaxestation/start_pickaxestation.sh
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

La inclusión de **`/usr/games` en `PATH`** es relevante: Mednafen podía ejecutarse manualmente, pero inicialmente no era encontrado cuando el menú se iniciaba como servicio.

Después de instalar el archivo de servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl enable pickaxestation.service
sudo systemctl start pickaxestation.service
sudo systemctl status pickaxestation.service
```

**Nota:** el servicio ocupa la terminal `tty1`; no debe iniciarse simultáneamente con otra sesión gráfica que intente utilizar el mismo dispositivo DRM/KMS.

## 7. Uso del sistema

1. Encender la Raspberry Pi con el control y la pantalla conectados.
2. Esperar a que termine el video de introducción y aparezca el menú de PickaxeStation.
3. En el menú principal, usar **izquierda/derecha en la cruceta** para recorrer juegos y **X** para ejecutar el seleccionado.
4. Jugar a través de Mednafen. Los botones deben haberse configurado también dentro del emulador.
5. Durante un juego, presionar **Share + Options** para cerrar Mednafen y regresar al menú.
6. Conectar una memoria USB con archivos SNES compatibles `.sfc` o `.smc` en su raíz y portadas `.png` opcionales con el mismo nombre base. Si hay contenido nuevo, la biblioteca se sincroniza, incluso durante el juego.
7. En el menú principal, presionar **Options** para abrir el menú del sistema; **X** confirma la opción seleccionada, **Triángulo** reinicia y **Círculo** cancela. Seleccionar **Apagar consola** para apagar.
8. También se permite navegar el menú básico con las flechas izquierda/derecha y Enter de un teclado conectado.

Utilizar únicamente ROMs y recursos sobre los que se cuente con derechos de uso o autorización. Los derechos de videojuegos y portadas pertenecen a sus respectivos titulares.

### Observaciones del código actual

- El archivo `menu.py` configura el sonido del menú con `SDL_AUDIODRIVER=alsa` y `SDL_AUDIO_ALSA_DEFAULT_DEVICE=plughw:0,0`. La salida apropiada depende del hardware de audio detectado en cada instalación.
- La consulta de ROMs y portadas se limita a la **raíz del montaje USB**; no realiza una exploración recursiva de subcarpetas.
- La detección permite elegir dispositivos con distintos nombres de partición (`/dev/sda1`, `/dev/sdb1`, etc.) en vez de fijar una letra o número de puerto.
- En los comentarios de `intentar_montar_usb()` todavía hay un ejemplo antiguo de permisos directos para `mount` y `umount`. **La implementación ejecutable usa el auxiliar `pickaxe-usb`**, como se explica anteriormente; debe considerarse esta última la configuración real.

## 8. Comprobación y solución de problemas

| Síntoma | Posible causa y comprobación |
|---|---|
| El servicio inicia, pero no abre juegos | Comprobar `PATH` y `/usr/games/mednafen`; revisar el registro del menú. |
| La pantalla gráfica no inicia | Verificar `/dev/dri/card0`, permisos del usuario y variables SDL; evitar sesiones que ocupen DRM/KMS. |
| Video con imagen, pero sin audio | Comprobar los dispositivos ALSA con `aplay -l` y la salida de MPV. |
| El juego aparece reducido o en una esquina | Revisar `snes.stretch aspect` y `video.fs 1` en Mednafen. |
| El control funciona en el menú, pero no en el juego | Configurar las asignaciones de botones por separado dentro de Mednafen. |
| No se detecta la USB | Consultar `lsblk`, confirmar el formato compatible y verificar la detección dinámica de particiones. |
| La USB se detecta, pero no se monta | Revisar `/usr/local/sbin/pickaxe-usb`, el archivo `/etc/sudoers.d/pickaxestation-usb`, el montaje `/mnt/usb` y los registros; no conceder permisos generales de montaje. |
| El menú no se inicia tras reiniciar | Revisar el estado y los logs del servicio `systemd`. |
| El script presenta errores de sintaxis | Comprobar `bash -n` y, si provino de Windows, corregir los finales de línea CRLF. |

Comandos útiles para depuración:

```bash
sudo systemctl status pickaxestation.service
sudo journalctl -u pickaxestation.service -b --no-pager
tail -n 100 /tmp/pickaxestation.log
lsblk -o NAME,TYPE,TRAN,MOUNTPOINTS
findmnt /mnt/usb
ls /dev/input/js*
```

Para conocer la IP actual de la Raspberry:

```bash
hostname -I
```

## 9. Pruebas de integración realizadas

En la Raspberry Pi 3B se verificó el arranque automático, el video introductorio, los sonidos del menú, la visualización de las portadas, la navegación con control PS4, la ejecución de juegos SNES, la salida al menú mediante Share + Options, la incorporación dinámica de nuevas ROMs desde USB, las transiciones, el escalado de pantalla, la reproducción de audio y las opciones de apagado/reinicio.

Durante las pruebas se resolvieron conflictos concretos de permisos de montaje, nombres dinámicos de unidades USB, rutas de ejecutables del servicio, configuración de audio y comportamiento de Mednafen en pantalla completa. Estas correcciones forman parte de la integración del sistema y de la evidencia de depuración.

## 10. Procedencia del proyecto y aportaciones individuales

Este proyecto se desarrolló originalmente durante el semestre anterior como un trabajo académico con participación de **Armando Vázquez Apolonio**, **Andrik Uriel Reyes Roque** y **Sergio I. Almodóvar Tufiño**. La presente documentación describe la implementación funcional examinada en Raspberry Pi 3B y distingue las aportaciones reconocidas en el desarrollo original.

### Armando Vázquez Apolonio — Configuración e integración del sistema

Sus actividades se concentraron principalmente en:

- Instalación y configuración de Raspberry Pi OS Lite y de las dependencias de la aplicación.
- Preparación del entorno de ejecución sin escritorio gráfico.
- Configuración y verificación del inicio automático mediante scripts y servicios de Linux.
- Integración y pruebas de video, audio, control USB y ejecución de videojuegos.
- Diagnóstico y resolución de conflictos de permisos, rutas y acceso a memorias USB.
- Ajustes y pruebas de funcionamiento en pantalla completa y retorno del emulador al menú.
- Organización de archivos, pruebas del conjunto y documentación de la configuración del sistema.

Estas aportaciones corresponden principalmente a la **administración del sistema operativo, la integración, la configuración y la depuración**. No se atribuye a Armando la autoría exclusiva de la interfaz gráfica ni de los algoritmos originales de sincronización USB.

### Andrik Uriel Reyes Roque — Interfaz gráfica y controles

El README del trabajo original le atribuye el desarrollo de la interfaz en Python/Pygame, su diseño visual, el manejo de eventos del control y funciones de navegación y gestión de la biblioteca. También reconoce su participación en los mecanismos de detección USB.

### Sergio I. Almodóvar Tufiño — Sincronización y gestión de medios USB

El README del trabajo original describe su participación en el diseño y desarrollo del mecanismo de detección de medios extraíbles, el análisis de unidades mediante `lsblk`, el filtrado de ROMs, la evitación de duplicados y la asociación automática de portadas.

> **Alcance de los créditos:** el documento original atribuye actividades relacionadas con la detección USB tanto a Andrik como a Sergio. Se conservan ambas menciones sin inventar una división más precisa del trabajo. El código, la historia de cambios y las explicaciones personales de los autores son las referencias apropiadas para detallar líneas o funciones concretas.


## 11. Licencia y terceros

El repositorio original contiene un archivo `LICENSE` de tipo **MIT** (copyright 2026, Donapolo). Los derechos y licencias de **Pygame**, **MPV**, **Mednafen**, ROMs, portadas, audio y video son independientes de la licencia del código del repositorio y deben respetarse.
