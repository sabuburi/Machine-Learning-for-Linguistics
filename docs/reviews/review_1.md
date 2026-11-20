# Review 1 checklist

Branch: `results`. `git status --short` was empty.

| Check | Status | Evidence |
|---|---|---|
| .gitignore contains `data/`, `outputs/`, `Quranic-Word-By-Word-Audio-Data/`, `.venv/`, `__pycache__/` | OK | All five entries present in `.gitignore`. |
| `outputs/` and dataset folder are NOT tracked by git | OK | `git ls-files outputs` and `git ls-files -s Quranic-Word-By-Word-Audio-Data` both returned no output (no 160000 pointers). |
| No tracked file is larger than 1 MB | PROBLEM | Tracked files over 1 MB: `af_subs.csv` (3,463,516), `ar_subs.csv` (8,938,246), `outputs.zip` (9,914,666). |
| `requirements.txt` is plain text and lists packages | OK | First 4 bytes are `b'pand'` (not UTF-16); lists pandas, numpy, scipy, matplotlib, statsmodels. |
| `analysis_results.md` does not exist | OK | `Test-Path analysis_results.md` returned `False`. |
| No `.py` file sits in `results/` | OK | `Get-ChildItem results -Filter *.py` returned no output. |
| README placeholders `[name A]` and `[name B]` are filled in | PROBLEM | `README.md` still contains `[name A]` at lines 23, 82 and `[name B]` at lines 88, 96. |
| README explains how to run `scripts/surprisal_analysis.py` | PROBLEM | `Select-String -Path README.md -Pattern "surprisal_analysis.py"` returned no matches. |

Summary: 5 OK, 3 PROBLEM (large tracked files, README name placeholders, missing run instructions for the analysis script).
