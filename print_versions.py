
import sys
# Map package names to import names
packages = {
    "numpy": "numpy",
    "pandas": "pandas",
    "scikit-learn": "sklearn",
    "xgboost": "xgboost",
    "shap": "shap",
    "matplotlib": "matplotlib",
    "praat-parselmouth": "parselmouth",  # praat-parselmouth installs as parselmouth
    "huggingface_hub": "huggingface_hub",
    "librosa": "librosa",
}

for pkg, mod_name in packages.items():
    try:
        mod = __import__(mod_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f"{pkg}: {version}")
    except ImportError as e:
        print(f"{pkg}: FAILED - {e}")