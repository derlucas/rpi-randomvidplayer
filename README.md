# rpi-randomvidplayer

A video player for the Raspberry Pi, controlled by GPIO pins. Designed to
run an unattended video display, where users can select the active video
by switch.

MIT licensed.

Based on [rpi-vidlooper by alubbock](https://github.com/alubbock/rpi-vidlooper)

## Features

* Play videos using [OMXplayer](https://elinux.org/Omxplayer), a hardware-
assisted video player for smooth playback.
* Switch between any number of videos using hardware switches wired to the
Raspberry Pi's GPIO pins.
* Callback-based, rather than polling-based. This means that button
presses should always be acted upon.
* Thread locking, to avoid issues when buttons are pressed rapidly
and the video hasn't finished loading yet.
* The Software plays a random video from a folder based on the GPIO triggered 

## Usage

You can use the two part tutorial on the [blog](https://alexlubbock.com) of Alex:

Start with the --video-dir Option to set the base path for Videos. Create a new folder
within the Videos folder for each GPIO pin, eg "17", "22" and so on. Put your
video files into that folder.

On the hardware side, you'll need a Raspberry PI with several switches,
one for each video. Each switch should be connected to a GPIO pin, and
to ground. 

Install dependencies:

```
sudo apt-get update
sudo apt-get install python3-pip omxplayer fbi
```

Install rpi-randomvidplayer:

```
git clone https://github.com/derlucas/rpi-randomvidplayer
```

For usage help, see:

```
cd rpi-randomvidplayer/
python3 vidlooper.py --help
```

## Troubleshooting

### RuntimeError: No access to /dev/mem. Try running as root!

The user you want to run the videoplayer as will need to be
in the `gpio` group. For example, for the `pi` user, you'd need to do this:

```
sudo usermod -a -G gpio pi
```

See [further information on this issue](https://raspberrypi.stackexchange.com/questions/40105/access-gpio-pins-without-root-no-access-to-dev-mem-try-running-as-root).

### No rights to /dev/vchiq

See the [OMXplayer troubleshooting](https://elinux.org/Omxplayer) to fix
this issue. It's also possible to avoid by running `sudo vidlooper`, but
as above, this is not recommended.

## Further reading

* [Raspberry Pi Video Player Hardware tutorial](https://alexlubbock.com/raspberry-pi-video-player-hardware)
* [Raspberry Pi Video Player Software tutorial](https://alexlubbock.com/raspberry-pi-video-player-software)
* [Python on the Raspberry Pi](https://www.raspberrypi.org/documentation/linux/software/python.md)
* [OMXPlayer, a hardware-accelerated video player for Raspberry Pi](https://www.raspberrypi.org/documentation/raspbian/applications/omxplayer.md)
