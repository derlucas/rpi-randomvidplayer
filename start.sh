#!/bin/bash

DIR="$(dirname "${0}")"
cd $DIR

python3 rpi_randomvidplayer/videoplayer.py --video-dir /home/lucas/Videos/ --gpio-pins 17 27 22 --debug --splash /home/lucas/Pictures/uzwei_konfetti_16zu9_1920x1080_03.jpg
