# Proyecto final  PickaxeStation
El proyecto pretende crear un simulador de consola  retro haciendo uso de de la Raspberry para poder tener un entorno de consola de videojuegos haciendo uso de emuladores y menús para una mejor experiencia 


Interfaz Gráfica: Desarrollada en Python 3 con Pygame. Opera sobre el búfer de fotogramas físico mediante DRM/KMS, permitiendo un alto rendimiento sin necesidad de un entorno de escritorio (X11/Wayland).
Diseño Visual: Estética neón con paneles semitransparentes (Alpha Blending), renderizado de fuentes con sombreado dinámico y escalado automático de carátulas para una navegación fluida.
Sincronización USB: Algoritmo que detecta memorias USB en tiempo real mediante el parseo de estructuras JSON y el comando lsblk, asegurando compatibilidad con cualquier puerto físico.
Controlador a Bajo Nivel: Monitor de eventos que lee directamente desde /dev/input/js0. Implementa la combinación de escape Share + Options para forzar el cierre del emulador y retornar al menú de forma segura.
Gestor de Biblioteca: Sincronización inteligente que copia únicamente ROMs nuevas (.sfc/.smc), vincula automáticamente portadas .png por nombre y asigna una imagen por defecto si falta el arte del juego.
