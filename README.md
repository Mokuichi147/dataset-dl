# dataset-dl

GUI software to download video and audio.
To download a data set in CSV format.


## Requirement

* [FFmpeg](https://ffmpeg.org/)


## Installation

```
pip install --upgrade pip
pip install --upgrade setuptools
pip install --upgrade poetry
poetry install
```


## Usage

Linux or MacOS    
```
poetry run dataset_dl/main.py
```

Windows 10 or 11
```
poetry run python.exe dataset_dl/main.py
```


## Build

```
poetry run pyinstaller main.spec
```


## Note

- [x] Download from Video URL
- [x] Download from Playlist URL
- [ ] Download from CSV