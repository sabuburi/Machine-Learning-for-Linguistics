# Review 3 — README plan vs repository

## File listings (names only)

**Project root:** `.clinerules`, `.git/`, `.gitignore`, `.venv-new/`, `.venv/`, `AGENTS.md`, `data_raw/`, `data/`, `ffmpeg-9.0.2-essentials_build/`, `figures/`, `outputs.zip`, `outputs/`, `print_versions.py`, `Quranic-Word-By-Word-Audio-Data/`, `README.md`, `regressions_S&E_vs_n_phon.csv`, `requirements.txt`, `results_run.log`, `results/`, `scripts/`

**scripts/:** `01_verify_pipeline.py`, `surprisal_analysis.py`

**results/:** `ar_corrected.csv`, `bigram_lookup_corrected.csv`, `final_summary.md`, `leverage_check.csv`, `model_table.csv`, `nonlinearity.csv`, `phase_1.md`, `phoneme_entropy_corrected.csv`, `pip_install.log`, `poisson_table.csv`, `regression_old_vs_corrected.csv`, `review_1.md`, `review_2.md`, `setup.md`, `verification.md`

**figures/:** `fig1_zipf_vs_surprisal.png`, `fig2_surprisal_by_length.png`, `fig3_coefficients.png`, `fig4_surprisal_versions.png`, `fig5_correction_effect.png`

**docs/:** does not exist.

## Table A — Planned analysis

| Planned item | Covered? | Where |
|---|---|---|
| Main surprisal measure: type-based LOO, plus frequency-weighted | Yes | `results/final_summary.md` §4 (token_weighted, token_weighted_loo, type, type_loo) |
| Frequency models: `zipf ~ S`, `+ n_phon`, `+ phon_density` | Yes | `final_summary.md` §4 (M1, M2, M3) |
| Length models: `n_phon ~ S`, `+ zipf`, plus Poisson | Yes | `final_summary.md` §4 (N1, N2) and §5 (Poisson table) |
| Standardized coefficients, R2, robust SE, cross-validated R2 | Yes | `final_summary.md` §3 (HC3) and §4 (beta, ci_low/high, r2, cv_r2) |
| Checks: nonlinearity, high-leverage words, 3–8 phonemes | Partly | `final_summary.md` §5 has squared-term (nonlinearity), 3–8 phoneme table, and top-1% refit; `results/leverage_check.csv` exists but is not in `final_summary.md` |
| Figures: zipf-vs-surprisal, surprisal-by-length (all lengths), coefficient plot, version comparison | Partly | `figures/fig1`–`fig4` exist; `fig2` omits lengths 16–19 (only ≥30 words, `final_summary.md` §6), so not "all lengths" |

## Table B — Tasks

| Task checkbox | Done? | Evidence |
|---|---|---|
| Re-tokenize IPA (keep the four) and recompute S/E and summary metrics | Yes | `results/ar_corrected.csv`, `phoneme_entropy_corrected.csv`, `bigram_lookup_corrected.csv`; `final_summary.md` §2–4 |
| Compute surprisal versions (weighted, type, LOO) | Yes | `final_summary.md` §4 (all four versions) |
| Fit models, run diagnostics, make figures | Yes | `final_summary.md` §4–5; `figures/fig1`–`fig5` |
| Add analysis script to `scripts/` | Yes | `scripts/surprisal_analysis.py` |
| Write 1–2 pages of background | No | No background `.md`/`.docx`; `docs/` missing; only `README.md`, `AGENTS.md`, `results/*.md` (setup/verification/phase logs) |
| Check 50 random words' pronunciations, record error rate | No | `results/transcription_check.csv` not found (glob search: no files) |
| Find corpus and how pronunciations were generated | No | README "Open questions" still lists "What corpus is the word list from, and how were the pronunciations produced?" |
| Draft Introduction and Limitations | No | No Introduction draft; `final_summary.md` §7 has analysis limitations only |
| Both: write and proofread the report | Unknown | No report draft found |

## README promises that do not exist

- `docs/muallim-mujawwad-brief.md` — `docs/` does not exist.
- `00_setup_venv.py` and `02_process_audio.py` "still in the root" — neither is in the root (only `print_versions.py`).
- Planned layout includes `docs/` — missing.
- Fig. "mean surprisal by length (all lengths)" — `fig2` covers only lengths with ≥30 words (16–19 omitted).
- `results/transcription_check.csv` (expected by the task, not promised in README) — absent.
