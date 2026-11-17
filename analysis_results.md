# Analysis Results — Arabic Surprisal

## Pipeline Execution

The surprisal analysis pipeline was run successfully on Arabic (`ar`).

- **Processing**: Arabic processed and saved to `outputs/ar_comprehensive.csv`
- **Languages processed**: 1 (Arabic)
- **Output directory**: `outputs/`

## Corpus Statistics

| Metric | Arabic |
|--------|--------|
| Word types | 29,765 |
| Word tokens | 104,015,732 |

Saved to `outputs/word_counts.csv`.

---

## Regression Results: S&E Metrics vs. n_phon

Slopes and R² values for each metric regressed against number of phonemes (`n_phon`), per language (Arabic only):

| Metric | Slope | R² | p-value | Direction |
|--------|-------|-----|---------|-----------|
| First_Surprisal | -0.2657 | 0.1256 | ~0 | Negative |
| Last_Surprisal | -0.2533 | 0.1048 | ~0 | Negative |
| Average_Surprisal | -0.1291 | 0.1255 | ~0 | Negative |
| Last_Entropy | -0.0276 | 0.0096 | 1.11e-64 | Negative |
| Max_Surprisal | 0.0248 | 0.0011 | 1.37e-8 | Positive |
| Max_Entropy | 0.0188 | 0.0793 | ~0 | Positive |
| First_Entropy | 0.0066 | 0.0003 | 0.0017 | Positive |
| Average_Entropy | -0.0013 | 0.0002 | 0.0137 | Negative |

**Key findings:**

- Surprisal metrics (First, Last, Average) show **negative slopes**: surprisal decreases as word length (in phonemes) increases.
- Entropy metrics show mixed slopes: Max_Entropy positive (+0.0188), First_Entropy slightly positive (+0.0066), Last_Entropy negative (-0.0276), Average_Entropy near zero (-0.0013).
- All 8 regressions are statistically significant (significant = 1).
- All slopes ranked #1 across languages (`n_languages = 1`).

Saved to:
- `outputs/regression_forest_data.csv`
- `outputs/regression_summary_across_languages.csv`

---

## Surprisal by Word Length (n_phon)

Mean surprisal decreases as word length increases:

| n_phon | N words | Mean Surprisal | 95% CI |
|--------|---------|----------------|--------|
| 3 | 334 | 4.6591 | [4.4778, 4.8404] |
| 4 | 1,055 | 4.4656 | [4.3870, 4.5442] |
| 5 | 1,990 | 4.2411 | [4.1936, 4.2885] |
| 6 | 3,496 | 3.8308 | [3.8019, 3.8597] |
| 7 | 4,766 | 3.6486 | [3.6288, 3.6684] |
| 8 | 5,495 | 3.5000 | [3.4850, 3.5150] |

Trend: mean surprisal drops ~1.16 bits from 3-phoneme to 8-phoneme words.

Saved to `outputs/surprisal_by_length_summary.csv`.

---

## Positional Surprisal Profiles

Positional surprisal (mean surprisal at each phoneme position within words of length `n_phon`) shows a characteristic pattern:

- **First positions**: lower surprisal (e.g., n_phon=8, pos=1: mean=2.22)
- **Middle positions**: higher surprisal (e.g., n_phon=8, pos=2: mean=4.72)
- **Last positions**: lower surprisal (e.g., n_phon=8, pos=7: mean=2.24)

This U-shaped pattern indicates that phonemes at word boundaries are more predictable, while medial phonemes carry more information.

Saved to `outputs/positional_surprisal_summary.csv`.

---

## Output Files Generated

| File | Description |
|------|-------------|
| `outputs/ar_comprehensive.csv` | Processed Arabic data with surprisal metrics |
| `outputs/word_counts.csv` | Type/token counts per language |
| `outputs/regression_forest_data.csv` | Per-metric regression coefficients (slope, R², p-value) |
| `outputs/regression_summary_across_languages.csv` | Aggregated regression summary |
| `outputs/surprisal_by_length_summary.csv` | Mean surprisal by word length |
| `outputs/positional_surprisal_summary.csv` | Positional surprisal by phoneme position |
| `outputs/surprisal_by_length_ar.jpg` | Surprisal-by-length plot (Arabic) |
| `outputs/surprisal_by_length_faceted.jpg` | Faceted surprisal-by-length plot |
| `outputs/positional_surprisal_faceted.jpg` | Faceted positional surprisal plot |
| `outputs/regressions_S&E_vs_n_phon.csv` | Full regression table |
| `outputs/terminal-output.txt` | Full terminal execution log |

---

## Warnings

1. NaNs produced in confidence interval calculation for `Average_Entropy` group (single observation → `qt()` with df=0).
2. 16 total warnings in `summarise()`; see terminal log for details.
3. `size` aesthetic deprecated in ggplot2 3.4.0; use `linewidth` instead.
4. Parsing issues reported by `vroom()`; call `problems()` on data frames for details.

---

## Interpretation

Arabic surprisal decreases with word length, consistent with the finding that longer words distribute information across more phonemes. The positional profile shows higher surprisal in medial positions, reflecting greater uncertainty in word-internal phoneme transitions compared to word-initial and word-final positions. All regression slopes are statistically significant, supporting a systematic relationship between surprisal/entropy metrics and phoneme count in Arabic.