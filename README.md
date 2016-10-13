# Sonopluie

## Dependancies

### pygame

```
sudo apt-get install mercurial python3-dev build-essential
sudo apt-get install libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl1.2-dev
sudo apt-get install libportmidi-dev ffmpeg libswscale-dev libavformat-dev libavcodec-dev libsmpeg-dev
hg clone https://bitbucket.org/pygame/pygame
cd pygame
python3 setup.py build
sudo python3 setup.py install
```

## Unit tests

```
python3 setup.py test
```

## Code coverage

```
make coverage
# or
./virtualenv/bin/coverage run -m unittest discover
```

## Launch tests in TDD mode

```
./virtualenv/bin/sniffer
# or
make tdd
```
