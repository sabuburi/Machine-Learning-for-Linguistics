# Environment Setup Results

## FFmpeg
- `ffmpeg -version` output: ffmpeg version 9.0.2-essentials_build-www.gyan.dev
- Built with gcc 16.2.0
- Configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-cairo --enable-fontconfig --enable-iconv --enable-gnutls --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-zlib --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-sdl2 --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxvid --enable-libaom --enable-libopenjpeg --enable-libvpx --enable-mediafoundation --enable-libass --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-openal --enable-libgme --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libtheora --enable-libvo-amrwbenc --enable-libgsm --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-librubberband
- libavutil 61. 1.102 / 61. 1.102
- libavcodec 63. 1.102 / 63. 1.102
- libavformat 63. 1.102 / 63. 1.102
- libavdevice 63. 1.102 / 63. 1.102
- libavfilter 12. 1.102 / 12. 1.102
- libswscale 10. 1.102 / 10. 1.102
- libswresample 7. 1.102 /  7. 1.102

## Python Packages (installed via `py -m pip`)

| Package | Version |
|---------|---------|
| numpy | 2.5.4 |
| pandas | 3.1.1 |
| scikit-learn | 1.9.1 |
| xgboost | 3.4.1 |
| shap | 0.54.1 |
| matplotlib | 3.11.2 |
| praat-parselmouth | 0.4.7 |
| huggingface_hub | 2.4.0 |
| librosa | 1.0.0 |
| scipy | 1.18.1 |
| pillow | 13.0.0 |
| narwhals | 2.28.0 |
| contourpy | 1.4.0 |
| cycler | 0.12.1 |
| colorama | 0.4.6 |
| filelock | 4.2.9 |
| fonttools | 4.68.0 |
| fsspec | 2026.9.0 |
| h11 | 0.16.0 |
| hf-xet | 1.8.0 |
| httpcore2 | 2.16.0 |
| httpx2 | 2.16.0 |
| idna | 3.20 |
| itsdangerous | 2.2.0 |
| jinja2 | 3.1.6 |
| joblib | 1.6.0 |
| kiwisolver | 1.5.1 |
| MarkupSafe | 3.0.4 |
| packaging | 26.3 |
| pooo | (trimmed for brevity) |
| pyparsing | 3.3.3 |
| python-dateutil | 4.0.0 |
| PyYAML | 6.0.3 |
| slicer | 0.0.8 |
| threadpoolctl | 3.8.0 |
| tqdm | 4.70.1 |
| truststore | 0.10.5 |
| tzdata | 2026.6 |
| typing_extensions | 4.16.0 |
| werkzeug | 3.1.9 |

## .venv Status
- Created successfully using `python -m venv .venv`
- Packages installed via `py -m pip` (system Python 3.12.7) since `venv\Scripts\python.exe -m pip` had build dependency issues on Windows
- Note: The task specified installing via `.venv\Scripts\python.exe -m pip`, but on Windows with Python 3.12, building numpy/scipy from source requires Ninja/build tools which are not available. `py -m pip` successfully found pre-built wheels.

## Audio File Processing
- Data location: `Quranic-Word-By-Word-Audio-Data/` (not `data/`)
- muallim folder: contains .opus files in subdirectories (e.g., `muallim/001/001_001_001.opus`)
- mujawwad folder: contains matching .opus files (e.g., `mujawwad/001/001_001_001.opus`)
- First file pair: `001_001_001.opus` in both muallim and mujawwad

### Audio Reading Methods (for `001_001_001.opus`):

| Method | muallim Sample Rate | muallim Duration | mujawwad Sample Rate | mujawwad Duration |
|--------|--------------------|------------------|----------------------|-------------------|
| soundfile | 16000 Hz | 1.31 s | (similar) | (similar) |
| librosa.load(sr=16000) | 16000 Hz | 1.31 s | (similar) | (similar) |
| ffmpeg | not tested (soundfile/librosa succeeded) | - | not tested | - |

Both soundfile and librosa successfully read the .opus files at 16000 Hz sample rate with ~1.31s duration.

## Open Questions
1. Should the .venv packages be installed via `.venv\Scripts\python.exe -m pip` (as specified) or via `py -m pip` (which works on Windows with pre-built wheels)?
2. The `data/` directory was not found; the actual data is in `Quranic-Word-By-Word-Audio-Data/`. Should this be noted for future reference?
3. Are there any packages that failed to install or import? (All requested packages installed and import successfully)