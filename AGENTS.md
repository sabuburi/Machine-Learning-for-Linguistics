# Project: Arabic surprisal (ML for Linguistics report, due 24 Nov 2026)
Goal: run scripts/surprisal_analysis.py on data/ and report its results. Do not redesign the analysis.

## Files
- data/ : raw CSVs (ar_comprehensive.csv ~24 MB, ar_bigram_lookup.csv, ar_phoneme_entropy.csv, regressions_S_E_vs_n_phon.csv). Read-only.
- scripts/surprisal_analysis.py : the verified analysis script. Do not rewrite it.
- results/ and figures/ : outputs written by the script.
- README.md : project description. Do not edit.

## Rules
- Your context is small (16k tokens). Keep every output short.
- NEVER open or print a whole CSV. Check the file size first. For a CSV show only the header and 5 rows.
- Never read a file over 100 KB in full. Use head or tail (PowerShell: Get-Content file -TotalCount 40 or -Tail 40).
- Redirect long command output to a file and show only the last 40 lines.
- Windows PowerShell. Use `py`, not python3.
- Every number you report must be copied from a file or command output. Never estimate or round into a result.
- If a check prints FAIL, stop and report it. Do not edit code to make it pass.
- Before changing any file, show the exact change and ask me. Never delete files. No git commands that change the repository.
- Install only `statsmodels`, and only if it is missing.
- One task at a time. When finished, summarize in at most 10 lines and stop.
