# dataset-dl

GUI software to download video and audio.
To download a data set in CSV format.

<p align="center">
    <img src="https://user-images.githubusercontent.com/38586357/147847093-95ffbfed-6ea6-4f42-9e2d-192913b5acf7.png" alt="dataset-dl App" width="500px">
</p>
<br>


## Requirement

* [FFmpeg](https://ffmpeg.org/)  
<br>


## Installation

```
pip install --upgrade pip
pip install --upgrade setuptools
pip install --upgrade poetry
poetry install
```

<details>
<summary>When pasting from the clipboard on Linux</summary>

```
sudo apt install xclip
```
</details>
<br>


## Usage

Linux or MacOS    
```
poetry run python src/dataset-dl.py
```

Windows 10 or 11
```
poetry run python.exe src/dataset-dl.py
```

<details>
<summary>If the download fails</summary>

Try the following command.
```
poetry update
```
</details>
<br>


## Build

```
poetry run pyinstaller build.spec
```

Windows 10 or 11
```
poetry run python.exe -m nuitka --onefile --include-data-files=resources/fonts/*=resources/fonts/ src/dataset-dl.py --follow-imports --enable-plugin=tk-inter --windows-icon-from-ico=resources/dataset-dl.ico --windows-disable-console
```
<br>


## Note

- [ ] Download from CSV in various styles
- [ ] Download in wav format  
<br>


## License

Licensed under either of

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option.  
<br>


### Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the work by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without any additional terms or conditions.

### Redistribution

<details>
<summary>NotoSansJP</summary>

[SIL OPEN FONT LICENSE Version 1.1](resources/fonts/OFL.txt)
```
├── resources  
│   ├── fonts  
│   │   ├── NotoSansJP-Regular.otf  
│   │   └── OFL.txt
```
</details>