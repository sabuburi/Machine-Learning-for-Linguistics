#!/usr/bin/env python
import os, subprocess, sys

# Find the .venv Python
venv_python = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")
if not os.path.exists(venv_python):
    # Try to find it
    for candidate in [
        r"C:\Users\M. Sabri\Documents\Lectures UoA\Machine Learning\Machine-Learning-for-Linguistics-\.venv\Scripts\python.exe",
    ]:
        if os.path.exists(candidate):
            venv_python = candidate
            break

print("Using Python:", venv_python)

packages = ["librosa", "numpy", "pandas", "scikit-learn", "xgboost", "shap", 
            "matplotlib", "praat-parselmouth", "huggingface_hub"]

cmd = [venv_python, "-m", "pip", "install"] + packages
result = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)

# Write requirements.txt
req_path = os.path.join(os.getcwd(), "requirements.txt")
with open(req_path, "w") as f:
    # Get installed packages
    req_result = subprocess.run([venv_python, "-m", "pip", "freeze"], capture_output=True, text=True)
    f.write(req_result.stdout)
print("Wrote requirements.txt")