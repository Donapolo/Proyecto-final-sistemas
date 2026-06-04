#!/bin/bash

LOG="/tmp/pickaxestation.log"

echo "===== INICIO PICKAXESTATION =====" > "$LOG"
date >> "$LOG"

clear
setterm -cursor off
setterm -blank 0
setterm -powerdown 0

INTRO="/home/apolo/pickaxestation/boot/intro.mp4"
MENU="/home/apolo/pickaxestation/menu/menu.py"

export SDL_VIDEODRIVER=kmsdrm
export SDL_RENDER_DRIVER=software
export SDL_KMSDRM_DEVICE=/dev/dri/card0

echo "INTRO=$INTRO" >> "$LOG"
echo "MENU=$MENU" >> "$LOG"
echo "USUARIO=$(whoami)" >> "$LOG"
echo "TTY=$(tty)" >> "$LOG"

if [ -f "$INTRO" ]; then
    echo "Reproduciendo intro..." >> "$LOG"
    mpv --fs --no-terminal --really-quiet --vo=drm --ao=alsa --audio-device=alsa/default "$INTRO" >> "$LOG" 2>&1
    echo "Intro terminada. Codigo=$?" >> "$LOG"
else
    echo "No existe intro.mp4" >> "$LOG"
fi

clear

echo "Iniciando menu..." >> "$LOG"
python3 "$MENU" >> "$LOG" 2>&1
echo "Menu termino. Codigo=$?" >> "$LOG"

clear
setterm -cursor on
echo "===== FIN PICKAXESTATION =====" >> "$LOG"