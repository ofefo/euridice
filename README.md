# Euridice.py

*Euridice.py* [eu.riˈdi.tʃe/] is python reimplementation of marcwallach's [bash
script](https://github.com/marcwallach/euridice) that takes a video URL from a
medium supported by `yt-dlp` and outputs a PDF document consisting of the
unique frames of that video.

Its name is taken from that of [Orpheus'
wife](https://www.youtube.com/watch?v=_7Wo-3DtI34) in Greek mythology. Her name
is derived from the words *ευρύς*, "wide" and *δικη*, "justice”, and serves as
a metaphor for the educational and ethical gap this script was designed to
bridge.

## Installation

After cloning the repo, `cd` to it and create a virtual environment:

```bash
python -m venv venv
```

Activate it before installing dependencies:

```bash
. venv/bin/activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

And you're good to go!

## Requirements

* img2pdf 
* opencv-python 
* yt-dlp
* not believing in intellectual property

## Usage

Simply pass as an argument a video URL, like this:

```bash
python euridice.py https://www.youtube.com/watch?v=ft_G8bKieNc
```

## LICENSE
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
