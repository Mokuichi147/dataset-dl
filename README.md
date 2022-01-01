# dataset-dl

GUI software to download video and audio.
To download a data set in CSV format.

<p align="center">
    <img src="https://user-images.githubusercontent.com/38586357/147847093-95ffbfed-6ea6-4f42-9e2d-192913b5acf7.png" alt="dataset-dl App" width="500px">
</p>


## Requirement

* [FFmpeg](https://ffmpeg.org/)


## Installation

```sh
pip install --upgrade pip
pip install --upgrade setuptools
pip install --upgrade poetry
poetry install
```


## Usage

Linux or MacOS    
```sh
poetry run python src/main.py
```

Windows 10 or 11
```
poetry run python.exe src/main.py
```


## Build

```
poetry run pyinstaller main.spec
```


## Note

- [x] Download from Video URL
- [x] Download from Playlist URL
- [ ] Download from CSV


## License

### dataset-dl

Licensed under either of [Apache License, Version 2.0](LICENSE-APACHE) or [MIT license](LICENSE-MIT) at your option.  

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in this project by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without any additional terms or conditions.


### NotoSansJP

[SIL OPEN FONT LICENSE Version 1.1](resources/fonts/OFL.txt)

```
├── resources  
│   ├── fonts  
│   │   ├── NotoSansJP-Regular.otf  
│   │   └── OFL.txt
```