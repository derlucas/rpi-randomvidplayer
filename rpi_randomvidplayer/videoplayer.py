#!/usr/bin/python

# Raspberry Pi GPIO-controlled video looper
# Copyright (c) 2019 Alex Lubbock
# License MIT

import RPi.GPIO as GPIO
import os
import sys
from subprocess import Popen, PIPE, call
import time
from threading import Lock
import signal
import argparse
import random
import logging
import warnings


class VideoPlayer(object):
    _GPIO_BOUNCE_TIME = 200
    _VIDEO_EXTS = ('.mp4', '.m4v', '.mov', '.avi', '.mkv')
    _GPIO_PIN_DEFAULT = {17, 27, 22}

    # Use this lock to avoid multiple button presses updating the player
    # state simultaneously
    _mutex = Lock()

    # The currently playing video filename
    _active_vid = None

    # The process of the active video player
    _p = None

    def __init__(self, audio='hdmi', video_dir=os.getcwd(), gpio_pins=None,
                 splash=None, debug=False):
        self.gpio_pins = gpio_pins
        self.videos = {}
        self.debug = debug
        self.splash = splash
        self._splashproc = None

        logging.debug("GPIO Pins {}".format(self.gpio_pins))

        if self.splash is not None and not os.path.exists(self.splash):
            raise FileNotFoundError('Splash image "{}" not found'.format(self.splash))

        if not os.path.exists(video_dir):
            raise FileNotFoundError('Video directory "{}" not found'.format(video_dir))

        for pin in self.gpio_pins:
            pin_video_dir = os.path.join(video_dir, str(pin))
            if not os.path.exists(pin_video_dir):
                raise FileNotFoundError('Video Folder for Pin {} not found'.format(pin))

            videos_in_folder = [os.path.join(pin_video_dir, f)
                                for f in sorted(os.listdir(pin_video_dir))
                                if os.path.splitext(f)[1] in self._VIDEO_EXTS]
            logging.debug("videos in folder {} = {}".format(pin, videos_in_folder))

            if not videos_in_folder:
                raise Exception('No videos found in "{}"'.format(pin_video_dir))

            self.videos[pin] = videos_in_folder


        assert audio in ('hdmi', 'local', 'both'), "Invalid audio choice"
        self.audio = audio


    def _kill_process(self):
        """ Kill a video player process. SIGINT seems to work best. """
        if self._p is not None:
            os.killpg(os.getpgid(self._p.pid), signal.SIGINT)
            self._p = None

    def switch_vid(self, pin):
        """ Switch to the video corresponding to the shorted pin """

        # Use a mutex lock to avoid race condition when
        # multiple buttons are pressed quickly
        with self._mutex:
            videos = self.videos[pin]

            filename = videos[random.randint(0, len(videos)-1)]

            # Kill any previous video player process
            self._kill_process()
            # Start a new video player process, capture STDOUT to keep the
            # screen clear. Set a session ID (os.setsid) to allow us to kill
            # the whole video player process tree.
            cmd = ['omxplayer', '-b', '-o', self.audio, '--no-osd', '--no-keys']

            self._p = Popen(cmd + [filename],
                            stdout=None if self.debug else PIPE,
                            preexec_fn=os.setsid)
            self._active_vid = filename


    def start(self):
        if not self.debug:
            # Clear the screen
            os.system('clear')
            # Disable the (blinking) cursor
            os.system('tput civis')

        # Set up GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)


        if self.splash is not None:
            self._splashproc = Popen(['fbi', '--noverbose', '-a',
                                      self.splash])


        # Enable event detection on each input pin
        for pin in self.gpio_pins:
            GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.switch_vid,
                                  bouncetime=self._GPIO_BOUNCE_TIME)

        # Loop forever
        try:
            while True:
                time.sleep(0.5)
                pid = -1
                if self._p:
                    pid = self._p.pid
                    self._p.communicate()
                if self._p:
                    if self._p.pid == pid:

                        self._active_vid = None
                        self._p = None

        finally:
            self.__del__()

    def __del__(self):
        if not self.debug:
            # Reset the terminal cursor to normal
            os.system('tput cnorm')

        # Cleanup the GPIO pins (reset them)
        try:
            GPIO.cleanup()
        except RuntimeWarning:
            pass

        # Kill any active video process
        self._kill_process()

        # Kill any active splash screen
        if self._splashproc:
            os.killpg(os.getpgid(self._splashproc.pid), signal.SIGKILL)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Raspberry Pi video player controlled by GPIO pins

This program is designed to power a video display, where the active
video can be changed by pressing a button (i.e. by shorting a GPIO pin).

This video player uses omxplayer, a hardware-accelerated video player for the
Raspberry Pi, which must be installed separately.
"""
    )
    parser.add_argument('--audio', default='hdmi',
                        choices=('hdmi', 'local', 'both'),
                        help='Output audio over HDMI, local (headphone jack),'
                             'or both')
    parser.add_argument('--video-dir', default=os.getcwd(),
                        help='Directory containing video files.')
    parser.add_argument('--gpio-pins', required=True,
                        action="store", nargs='+', type=int,
                        help='List of GPIO pins, separated by space.')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Debug mode (don\'t clear screen or suppress '
                             'terminal output)')
    parser.add_argument('--splash', type=str, default=None,
                        help='Splash screen image to show when no video is '
                             'playing')

    # Invoke the videoplayer
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    VideoPlayer(**vars(args)).start()


if __name__ == '__main__':
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(str(e))
