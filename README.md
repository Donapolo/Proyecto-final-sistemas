# PickaxeStation

## Descripción general del proyecto

PickaxeStation es una consola retro desarrollada sobre Raspberry Pi OS Lite, diseñada para ejecutar videojuegos clásicos de 8 y 16 bits mediante una interfaz propia desarrollada en Python, sin utilizar distribuciones retro preconfiguradas ni entornos gráficos de escritorio.

El objetivo principal del proyecto fue implementar un sistema de emulación funcional desde una instalación base de Raspberry Pi OS Lite, cumpliendo con las restricciones del proyecto académico, las cuales prohibían el uso de plataformas como RetroPie, Batocera, Recalbox o similares.

El sistema fue desarrollado para iniciar automáticamente al encender la Raspberry Pi, mostrando una interfaz fullscreen personalizada con navegación mediante control de videojuegos. La interfaz permite visualizar una galería de juegos, reproducir efectos de sonido, mostrar animaciones de introducción y ejecutar emuladores externos desde un menú centralizado.

Durante el desarrollo se configuraron distintos componentes del sistema operativo y del entorno de ejecución, incluyendo:

* instalación y configuración de Raspberry Pi OS Lite 64 bits,
* configuración del arranque automático del sistema,
* ocultamiento de mensajes de consola durante el boot,
* integración de controles USB tipo PS4,
* desarrollo de la interfaz gráfica usando Python y Pygame,
* implementación de reproducción de audio y video,
* organización automática de ROMs y recursos multimedia,
* integración de emuladores compatibles con NES, SNES y GBA,
* y configuración del sistema para ejecutarse sin entorno de escritorio.

La interfaz fue diseñada para ofrecer una experiencia similar a una consola comercial retro, manteniendo una navegación simple, visual y completamente operable mediante gamepad.

---

# Requisitos del sistema

## Hardware utilizado

* Raspberry Pi 4 Model B
* Tarjeta microSD de 16 GB o superior
* Fuente de alimentación oficial para Raspberry Pi
* Control USB tipo PS4
* Monitor o pantalla HDMI
* Bocinas o salida de audio auxiliar/HDMI
* Memoria USB para transferencia de ROMs (opcional)

## Software requerido

* Raspberry Pi OS Lite 64 bits
* Python 3
* Pygame
* RetroArch y emuladores compatibles
* Git
* Librerías de audio y video necesarias para el sistema

---

# Repositorio y código fuente

El proyecto cuenta con un repositorio público donde se encuentra disponible el código fuente completo, así como los archivos necesarios para su instalación, configuración y ejecución sobre Raspberry Pi OS Lite.

El repositorio incluye:

* código fuente del menú principal desarrollado en Python,
* recursos multimedia utilizados por la interfaz,
* configuraciones necesarias para el arranque automático,
* documentación técnica del proyecto,
* y el archivo `README.md` con instrucciones de instalación y uso.

## Descarga del proyecto

El repositorio puede descargarse utilizando Git mediante el siguiente comando:

```bash id="8n6cbi"
git clone https://github.com/Donapolo/Proyecto-final-sistemas
```

Posteriormente se debe ingresar a la carpeta del proyecto:

```bash id="1u9rr1"
cd Proyecto-final-sistemas
```

---

# Estructura del proyecto

```text id="7fw5rj"
Proyecto-final-sistemas/
|-- boot/
|   `-- intro.mp4
|-- menu/
|   |-- menu.py
|   |-- fondo.png
|   |-- logo.jpeg
|   `-- mover.wav
|-- roms/
|   |-- nes/
|   |-- snes/
|   `-- gba/
|-- media/
|   |-- Default.png
|   `-- snes/
|-- scripts/
|   `-- start_pickaxestation.sh

---

# Configuración del proyecto

La instalación y configuración del proyecto se realizó manualmente sobre Raspberry Pi OS Lite, instalando las dependencias necesarias para la ejecución de Python, Pygame y los emuladores utilizados.

Las configuraciones realizadas incluyen:

* instalación de librerías necesarias,
* configuración de audio y video,
* integración del control USB,
* configuración de arranque automático,
* organización de ROMs y recursos multimedia,
* y ajustes del sistema para ejecución fullscreen sin entorno de escritorio.

---

# Configuración y ejecución

También se incluye el archivo `start_pickaxestation.sh`, utilizado para automatizar el arranque de la aplicación principal en la Raspberry Pi al iniciar el sistema operativo. Este script permite ejecutar automáticamente el menú principal de PickaxeStation durante el proceso de inicio del sistema.

Una vez instalado el entorno y las dependencias necesarias, el sistema puede ejecutarse mediante:

```bash id="2sw1s5"
python3 menu.py
```

El proyecto fue diseñado para iniciar automáticamente al arrancar la Raspberry Pi mediante scripts de inicio configurados en el sistema operativo.

---

# Documentación del código

Los archivos fuente fueron documentados mediante comentarios explicativos dentro del código, indicando el funcionamiento de funciones, módulos y secciones importantes del sistema.

Asimismo, se incluyen referencias al autor y licencias correspondientes de los recursos utilizados durante el desarrollo.

---

# Aporte realizado
<h1>
  Vazquez Apolonio Armando
</h1>

---

Como parte del desarrollo del proyecto, **participé principalmente en la preparación y configuración del entorno de trabajo** sobre Raspberry Pi OS Lite, así como en la integración y corrección de distintos componentes del sistema.

### Configuración del Entorno y Sistema Operativo

Realicé la instalación y configuración inicial del sistema operativo, **preparando una imagen funcional de Raspberry Pi OS Lite** para ejecutar el proyecto sin entorno gráfico de escritorio. Asimismo, configuré los servicios, dependencias y herramientas necesarias para la ejecución de scripts en Python y el correcto funcionamiento de los emuladores.

### Automatización y Optimización del Arranque

Durante el desarrollo, **trabajé en la automatización del arranque de la consola**, configurando scripts de inicio y corrigiendo problemas relacionados con la ejecución automática del menú principal al encender la Raspberry Pi. De igual forma, realicé modificaciones al sistema para ocultar los mensajes de la consola y mejorar la apariencia visual durante el proceso de *boot*.

### Resolución de Problemas Técnicos

Me encargué de la detección y solución de diversos errores técnicos presentados durante la implementación, entre los cuales destacan:

* **Audio:** Problemas de reproducción de sonido en los emuladores.
* **Pantalla:** Errores de ejecución en modo *fullscreen*.
* **Permisos:** Conflictos de permisos en la ejecución de scripts.
* **Periféricos:** Fallos de reconocimiento del control USB.
* **Rutas:** Errores relacionados con rutas de archivos y la carga de ROMs.
* **Flujo del Sistema:** Problemas de reinicio automático del menú tras cerrar las aplicaciones.

### Pruebas de Integración y Estructuración

Además, **realicé pruebas de integración** entre Python, Pygame, los emuladores y el sistema operativo, verificando el correcto funcionamiento de los videos de introducción, sonidos, la navegación mediante el *gamepad* y la ejecución de los juegos.

Finalmente, trabajé en la **organización de las carpetas del proyecto**, la estructura de los  multimedia y la configuración de scripts para facilitar la instalación y el mantenimiento futuro del sistema.
<h1>
Reyes Roque Andrik Uriel
</h1>
Reyes Roque Andrik Uriel
Interfaz gráfica propietaria

Programó la interfaz desde cero en Python 3 utilizando Pygame. Logró que opere directamente sobre el búfer de fotogramas físico mediante DRM/KMS, permitiendo un alto rendimiento y fluidez de 60 FPS sin necesidad de un entorno de escritorio como X11 o Wayland.

Diseño visual avanzado

Implementó una estética neón con paneles semitransparentes mediante técnicas de Alpha Blending. Además, desarrolló un sistema de renderizado de fuentes con sombreado dinámico para mejorar la legibilidad y un algoritmo de escalado automático de carátulas.

Sincronización USB (Centinela)

Diseñó un algoritmo que detecta memorias USB en tiempo real. Utilizó el comando lsblk y estructuras JSON para identificar dispositivos de almacenamiento dinámicamente, permitiendo reconocer memorias USB sin importar el puerto físico utilizado.

Control de hardware a bajo nivel

Implementó un monitor de eventos que lee directamente desde /dev/input/js0. También programó la combinación Share + Options para interceptar señales del control PS4/PS5, forzar el cierre del emulador Mednafen y regresar al menú principal de manera segura.

Gestión inteligente de biblioteca

Desarrolló la lógica de sincronización encargada de detectar y copiar únicamente ROMs nuevas (.sfc y .smc). El sistema vincula automáticamente las portadas .png por coincidencia de nombre y asigna una imagen predeterminada (Default.png) cuando el juego no cuenta con arte propio.
