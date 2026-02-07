# Shrink (Termux Video Shrinker)

[![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Android%20%2B%20Termux-brightgreen)](https://termux.dev/)
[![FFmpeg](https://img.shields.io/badge/ffmpeg-required-brightgreen)](https://ffmpeg.org/)
[![License](https://img.shields.io/github/license/BGGremlin-Group/Shrink?color=brightgreen)](https://github.com/BGGremlin-Group/Shrink/blob/main/LICENSE)
[![Stars](https://img.shields.io/github/stars/BGGremlin-Group/Shrink?style=flat&color=brightgreen)](https://github.com/BGGremlin-Group/Shrink/stargazers)
[![Issues](https://img.shields.io/github/issues/BGGremlin-Group/Shrink?color=brightgreen)](https://github.com/BGGremlin-Group/Shrink/issues)

**Shrink** is a **no-root**, **no-arguments** video size reducer for **Termux on Android**.  
It uses **FFmpeg two-pass encoding** to compress videos toward a target size (e.g., `16MB → 9MB`) with a simple interactive menu.

> Developed by the **BGGG background gremlin group** 🟩


![Shrink demo screenshot](https://github.com/BGGremlin-Group/Shrink/main/assets/shrink-ui.png)

[![Watch demo]([a](/assets/shrink-ui.png)](assets/demo.mp4)
---

## Features

- ✅ Interactive **menu UI** (no CLI flags/arguments)
- ✅ Pick a video from storage (MP4/MOV/MKV/WEBM/AVI/3GP/M4V)
- ✅ Choose target size in **MB**
- ✅ Optional **audio bitrate** selection (48/64/96/128 kbps)
- ✅ Optional **downscale** (720p / 480p / 360p)
- ✅ Uses **two-pass H.264 (libx264)** for better size accuracy
- ✅ Writes output to a chosen folder with an auto filename

---

## Requirements

- Android device with **Termux** installed
- Termux packages:
  - `ffmpeg`
  - `python`
- Shared storage access (recommended)

---

## Install (Termux)

1) Allow shared storage access:
```sh
termux-setup-storage

2. Install dependencies:



pkg update
pkg install -y ffmpeg python

3. Download shrink.py (pick one method):



Option A: Git clone

pkg install -y git
git clone https://github.com/BGGremlin-Group/Shrink.git
cd Shrink

Option B: Manual

Create a file named shrink.py and paste the script contents.



---

Run

From the project directory (or wherever shrink.py lives):

python shrink.py

Picker tips (in-app)

S → jump to shared storage (~/storage/shared)

~ → jump to Termux home

D# → open folder

V# → select video

.. → go up

Q → quit



---

Output

The output filename is auto-generated like:

OriginalName_9mb.mp4

Output location is chosen in the menu:

Same folder as input (recommended)

Shared storage /Movies (if exists)

Termux home (~)



---

Notes on accuracy

Two-pass encoding aims to hit your target size, but exact MB can vary slightly due to:

MP4 container overhead

variable audio/video complexity

encoder rounding


If your output is slightly over target:

Try target 8.8MB instead of 9MB

Lower audio bitrate to 64 kbps

Enable downscale (720p or 480p)



---

Troubleshooting (Termux)

FFmpeg “CANNOT LINK EXECUTABLE … .so not found”

This usually means a partial upgrade left missing libraries.

Recommended fix:

pkg update
pkg upgrade -y
apt --fix-broken install -y
dpkg --configure -a

If you see a specific missing library like libvpx.so.12, installing the package that provides it can help:

pkg install -y libvpx


---

Security / Privacy

Runs entirely local on your device.

Does not require root.

Does not upload files anywhere.



---

Credits / Acknowledgements

FFmpeg — the underlying media engine used for encoding and probing.
FFmpeg is licensed under the LGPL/GPL depending on build configuration. See: https://ffmpeg.org/

Termux — Android terminal environment: https://termux.dev/

Python — scripting runtime: https://www.python.org/


Dev credits: BGGG background gremlin group


---

License

See LICENSE.
