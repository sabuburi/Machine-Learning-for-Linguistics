import os
import soundfile
import librosa
import subprocess
import tempfile

base = r"c:/Users/M. Sabri/Documents/Lectures UoA/Machine Learning/Machine-Learning-for-Linguistics-/Quranic-Word-By-Word-Audio-Data"

muallim_dir = os.path.join(base, "muallim")
mujawwad_dir = os.path.join(base, "mujawwad")

# Find first .opus file in muallim (files are in subdirectories)
def find_first_opus(directory):
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith(".opus"):
                return os.path.join(root, f)
    return None

first_muallim = find_first_opus(muallim_dir)
first_mujawwad = find_first_opus(mujawwad_dir)

print(f"First muallim file: {first_muallim}")
print(f"First mujawwad file: {first_mujawwad}")

if not first_muallim or not first_mujawwad:
    print("Could not find .opus files!")
    exit(1)

# Function to read audio and get duration
def read_audio(filepath, method_name):
    """Try to read audio file, return (sr, duration) or (None, None) on failure"""
    try:
        if method_name == "soundfile":
            data, sr = soundfile.read(filepath)
            duration = len(data) / sr
            return sr, duration
        elif method_name == "librosa":
            data, sr = librosa.load(filepath, sr=16000)
            duration = librosa.get_duration(y=data, sr=sr)
            return sr, duration
        elif method_name == "ffmpeg":
            # Use ffmpeg to convert to wav temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
            result = subprocess.run(
                ["ffmpeg", "-i", filepath, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", tmp_path],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                data, sr = soundfile.read(tmp_path)
                duration = len(data) / sr
                return sr, duration
            else:
                print(f"  ffmpeg error: {result.stderr}")
                return None, None
    except Exception as e:
        print(f"  {method_name} error: {type(e).__name__}: {e}")
        return None, None

# Process the muallim file
print(f"\n=== Processing muallim: {first_muallim} ===")
for method in ["soundfile", "librosa", "ffmpeg"]:
    sr, dur = read_audio(first_muallim, method)
    if sr is not None:
        print(f"  {method}: sample_rate={sr}, duration={dur:.2f}s - SUCCESS")
    else:
        print(f"  {method}: FAILED")

# Process the mujawwad file
print(f"\n=== Processing mujawwad: {first_mujawwad} ===")
for method in ["soundfile", "librosa", "ffmpeg"]:
    sr, dur = read_audio(first_mujawwad, method)
    if sr is not None:
        print(f"  {method}: sample_rate={sr}, duration={dur:.2f}s - SUCCESS")
    else:
        print(f"  {method}: FAILED")