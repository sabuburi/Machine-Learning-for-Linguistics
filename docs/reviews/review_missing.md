# Missing / wrong — consolidated from reviews 1–3

## Evidence status
- Pronunciation check (~50 words) and error rate: **missing** (`results/transcription_check.csv` absent).
- Background notes / draft Introduction: **missing** (no background `.md`/`.docx`; `docs/` absent).
- Draft Methods/Results, figure captions, limitations: **missing** (only `results/final_summary.md`; §7 limitations only).
- Professor's answers (main measure; report vs poster): **unknown** (not covered by the reviews).
- Positional surprisal recomputed with corrected phonemes: **unknown** (not covered by the reviews).
- Repo hygiene: mixed — `.gitignore` OK, no broken dataset pointer, `requirements.txt` OK; large tracked files and README placeholders are problems.

## MUST FIX BEFORE SUBMITTING
- Large tracked files `af_subs.csv` (3,463,516), `ar_subs.csv` (8,938,246), `outputs.zip` (9,914,666) — bloats the repo and risks submission limits — `git ls-files`; untrack them (`git rm --cached`) and add to `.gitignore`.
- README placeholders `[name A]` (lines 23, 82) and `[name B]` (lines 88, 96) — looks unfinished — `README.md`; replace with the real names.
- No Introduction/background draft — the report has no opening/literature — `README.md` tasks; write 1–2 pages of background.
- No report draft (Methods/Results) — there is no report to hand in — repo; draft Methods and Results from `results/final_summary.md`.
- No figure captions — figures cannot be used in the report as-is — `figures/`; add a caption for each figure.
- Pronunciation check of ~50 words and its error rate not done — data validity is unverified — `results/transcription_check.csv` (missing); run the check and record the error rate.

## SHOULD DO
- README does not explain how to run `scripts/surprisal_analysis.py` — reproducibility — `README.md`; add the exact command.
- `fig2` omits lengths 16–19, so it is not "all lengths" as planned — planned analysis unmet — `figures/fig2_surprisal_by_length.png`; regenerate with all lengths or document the cutoff.
- `results/leverage_check.csv` exists but is not reported in `final_summary.md` — a planned check is missing from the write-up — `results/final_summary.md`; add a leverage subsection.
- Corpus origin and how pronunciations were generated not established — Methods is incomplete — `README.md` open questions; investigate and record.
- Limitations section not drafted (only analysis limitations in `final_summary.md` §7) — report limitation section missing — write it.
- `docs/` and `docs/muallim-mujawwad-brief.md` do not exist though README references them — broken README promise — `README.md`; restore `docs/` or remove the reference.

## NICE TO HAVE
- Root scripts `00_setup_venv.py` and `02_process_audio.py` are promised but absent (paused project) — stale README — `README.md`; restore them or update the note.
- Stray/generated artifacts in root (`outputs.zip`, `outputs/`, `data_raw/`, `ffmpeg-9.0.2-essentials_build/`) — clutter — root; move out of the repo or ignore them.
