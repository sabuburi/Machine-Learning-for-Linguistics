# Average surprisal as a predictor of word frequency and length in Arabic

## Summary
For about 30,000 Arabic words we have a phoneme-level predictability measure: **average surprisal**
(how unexpected each next sound is, averaged over the word). We ask whether this measure predicts
how **frequent** a word is and how **long** it is (number of phonemes). A quick pilot says surprisal is
a weak predictor of frequency and a moderate predictor of length (see "Pilot results").

## Research questions
1. **RQ1.** Does average surprisal predict word frequency? Prediction: more predictable words are more frequent (negative slope).
2. **RQ2.** Does average surprisal predict number of phonemes? Prediction: negative slope.
3. **RQ3.** Does surprisal add predictive value beyond the other variable (length for frequency, frequency for length)?

## Key terms
- **Phoneme bigram:** two sounds in a row, e.g. `l_i`.
- **Surprisal:** S = -log2 P(next phoneme | current phoneme). Rare transitions have high surprisal.
- **Entropy (of a phoneme):** uncertainty about which phoneme comes next after it.
- **Average_Surprisal:** mean surprisal over the bigrams of one word. Also `First_`, `Last_`, `Max_Surprisal`.
- **n_phon:** number of phonemes in the word. **zipf:** frequency on the Zipf scale, which appears to be log10(frequency per million) + 3.

## Data
Output of an R pipeline run on Arabic (the R script is not in this repo yet). The data files are **not committed**
(the main file is 24 MB). Put them in `data/` (ignored by git); ask [name A] for copies.

| File | What it is |
|---|---|
| `ar_comprehensive.csv` | 29,765 words x 73 columns: frequency, IPA, phoneme string, neighbourhood measures, per-position surprisal (S1-S18) and entropy (E1-E19), and summary metrics |
| `ar_bigram_lookup.csv` | 875 phoneme bigrams: frequency-weighted count, P(next given left), surprisal |
| `ar_phoneme_entropy.csv` | entropy of the next-phoneme distribution for each of the 42 phonemes |
| `word_counts.csv` | 29,765 word types, 104,015,732 tokens |
| `regression*.csv`, `regressions_S_E_vs_n_phon.csv` | the pipeline's regressions of surprisal and entropy metrics on `n_phon` |
| `surprisal_by_length_summary.csv`, `positional_surprisal_summary.csv` + `.jpg` plots | mean surprisal by length and by position |

Key columns of `ar_comprehensive.csv`: `word_original`, `raw_frequency` (minimum 411), `zipf`, `IPA`,
`phonemes_str` (space-separated phonemes, used for every computation), `n_phon`, `phon_density`, `PLD20`,
`First_/Last_/Average_/Max_Surprisal`, `First_/Last_/Average_/Max_Entropy`.

**How the numbers are computed** (checked: we reproduced every value exactly):
bigram count = sum over words of (word frequency x occurrences of the bigram in `phonemes_str`);
P(next | left) = bigram count / total count of bigrams with the same left phoneme;
surprisal = -log2 P; entropy of a phoneme = entropy of its next-phoneme distribution.

## Known issues (read before using the files)
1. **Four phonemes are missing from `phonemes_str`: ħ, ð, θ, χ** (the sounds of ح ذ ث خ). This affects
   **6,822 words (22.9%)**. Every surprisal, entropy and `n_phon` value for those words is computed on a
   sequence with sounds missing. Fix: re-tokenize `IPA` keeping these four (inventory becomes 46 phonemes;
   mean `n_phon` goes from 8.06 to 8.32). Our corrected tokenizer reproduces `phonemes_str` exactly for all
   unaffected words, and for affected words once the four are removed.
2. **The pipeline's length and position plots only cover 3 to 8 phonemes**: 17,136 of 29,765 words (58%).
   The regressions use all words. State or fix this in the report.
3. **Frequency leakage:** the bigram counts are weighted by word frequency, so a word's own frequency feeds its
   own surprisal. When predicting frequency, also use a type-based (unweighted) table and leave-one-out versions.
4. **The pronunciations look partly automatic.** Example: لقد is transcribed *liqadːa* and كنت *kannat*, which
   look like errors. Check a sample of about 50 words with an Arabic reader.
5. About 90 words share an IPA transcription with another word.
6. Frequency has a floor (no word below 411 occurrences), so we cannot say anything about rare words.

## Pilot results (corrected phoneme sequences, all 29,765 words)
| Average surprisal version | r with zipf | R2 (zipf ~ S) | R2 (n_phon ~ S) |
|---|---|---|---|
| Frequency-weighted (current pipeline) | -0.133 | 0.018 | 0.140 |
| Frequency-weighted, leave-one-out | -0.115 | 0.013 | 0.141 |
| Type-based (each word counted once) | -0.082 | 0.007 | 0.164 |
| Type-based, leave-one-out | -0.080 | 0.006 | 0.163 |

- With `n_phon` added, R2 for frequency is about 0.04 to 0.06 and the 5-fold cross-validated R2 is about 0.04.
- Shorter words are more frequent (r = -0.14).
- First, last and average surprisal all fall as words get longer (slopes about -0.26, -0.26 and -0.14 bits per phoneme, corrected).
- Surprisal peaks at the second bigram and declines toward the end of the word (positional plot).
- These are exploratory numbers, not final results.

## Planned analysis
- Main surprisal measure: type-based, leave-one-out. Report the pipeline's frequency-weighted version next to it.
- Frequency: `zipf ~ S`, `zipf ~ S + n_phon`, `zipf ~ S + n_phon + phon_density`.
- Length: `n_phon ~ S`, `n_phon ~ S + zipf`, plus a Poisson regression (n_phon is a count).
- Report standardized coefficients, R2, robust standard errors and cross-validated R2. With about 30,000 words almost
  everything is significant, so focus on effect sizes.
- Checks: nonlinearity, high-leverage words (very frequent function words), and words with 3 to 8 phonemes only.
- Figures: zipf vs surprisal (hexbin with fit line), mean surprisal by length (all lengths), coefficient plot, comparison of the surprisal versions.

## Tasks
**[name A] (analysis)**
- [ ] Re-tokenize `IPA` (keep ħ ð θ χ) and recompute S/E and the summary metrics
- [ ] Compute the surprisal versions (frequency-weighted, type-based, leave-one-out)
- [ ] Fit the models, run diagnostics, make the figures
- [ ] Add the analysis script to `scripts/`

**[name B] (research and checking)**
- [ ] Read the starting points below and write 1 to 2 pages of background (see questions)
- [ ] Check 50 random words' pronunciations (Arabic reader) and record the error rate
- [ ] Find out what corpus the word list comes from and how the pronunciations were generated
- [ ] Draft the Introduction and Limitations sections

**Both:** write and proofread the report.

## Research questions for [name B]
- What is known about the relationship between word length, frequency and phonotactic probability?
- Is a phoneme bigram surprisal model a standard way to measure phonotactic predictability? What are the alternatives?
- How might Arabic root-and-pattern morphology and affixes shape predictability at the start and end of words?
- How are the Zipf scale and word frequency usually modelled in regression (why log frequency)?

**Starting points (look these up and verify the details before citing):**
- Shannon (1948), *A mathematical theory of communication*.
- Zipf (1935), *The Psycho-Biology of Language* (the law of abbreviation: frequent words are short).
- Piantadosi, Tily & Gibson (2011), "Word lengths are optimized for efficient communication", PNAS.
- Mahowald, Dautriche, Gibson & Piantadosi (2018), "Word forms are structured for efficient use", Cognitive Science.
- Vitevitch & Luce (1999), "Probabilistic phonotactics and neighborhood activation in spoken word recognition", Journal of Memory and Language.
- McCarthy (1981), "A prosodic theory of nonconcatenative morphology", Linguistic Inquiry (Arabic root-and-pattern morphology).

## Open questions for the professor
1. Is predicting frequency and `n_phon` from average surprisal the intended analysis?
2. Should the frequency-weighted surprisal from the pipeline be the main measure, or the leakage-free type-based one?
3. Report or poster, and any length or format requirements?
4. Are we expected to compare Arabic with other languages (the pipeline's summary files are set up for several languages)?
5. What corpus is the word list from, and how were the pronunciations produced?

## Repository notes
- This README describes the current project (Arabic surprisal). An earlier project (Muallim vs Mujawwad recitation,
  word-level audio) is **paused**; its brief is in `docs/muallim-mujawwad-brief.md`, and its setup scripts
  (`00_setup_venv.py`, `02_process_audio.py`) are still in the root.
- Planned layout: `data/` (not committed), `scripts/`, `results/`, `figures/`, `docs/`.
