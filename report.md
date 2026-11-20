# Average Phoneme Surprisal as a Predictor of Word Frequency and Length in Arabic

## Methods

### Data and materials
The analysis used a list of 29,765 Arabic words, each annotated with its IPA transcription, a space-separated phoneme string, frequency on the Zipf scale, and a set of phoneme-level predictability measures. These materials were produced by an external R pipeline and distributed as `ar_comprehensive.csv`, which contains 73 columns, including per-position surprisal and entropy values as well as word-level summary metrics. The principal predictor was Average_Surprisal, defined as the mean surprisal of the phoneme bigrams in a word.

Inspection of the original phoneme strings revealed that four phonemes had been omitted during tokenisation, affecting 6,822 words (22.9% of the list). We therefore re-tokenised the IPA column while retaining these four segments, which increased the phoneme inventory from 42 to 46 and raised the mean number of phonemes per word from 8.06 to 8.32. All surprisal and entropy values reported below were recomputed from the corrected sequences.

### Surprisal measure
For each adjacent phoneme pair, surprisal was defined as S = −log2 P(next phoneme | current phoneme). Bigram counts were obtained by summing, over all words, either the word's frequency or a count of one, multiplied by the number of occurrences of the bigram in the word; the conditional probability was then the bigram count divided by the total count of bigrams sharing the same left phoneme. A word's Average_Surprisal was the mean over its bigrams. Four versions were computed: a frequency-weighted version matching the original pipeline, a frequency-weighted leave-one-out version, a type-based (unweighted) version, and a type-based leave-one-out version. The type-based leave-one-out measure was treated as the main predictor because it removes the contribution of a word's own frequency, which otherwise leaks into its own surprisal. The pipeline's frequency-weighted version is reported alongside it for comparability.

### Statistical models
All models were estimated by ordinary least squares on standardized variables, with heteroscedasticity-consistent (HC3) standard errors; predictive performance was assessed using five-fold cross-validated R² (seed 0). For frequency, we fitted `zipf ~ S` (M1), `zipf ~ S + n_phon` (M2), and `zipf ~ S + n_phon + phon_density` (M3). For length, we fitted `n_phon ~ S` (N1) and `n_phon ~ S + zipf` (N2), and, because `n_phon` is a count, we additionally fitted a Poisson regression of `n_phon` on surprisal.

### Verification and robustness
Before modelling, we reproduced the pipeline's own computations. All eight verification checks passed, including the reconstruction of bigram counts, conditional probabilities, phoneme entropy, the eight per-word metrics, and the regressions on `n_phon`; the largest discrepancy was 1.53e-14. Robustness was examined in three ways: by adding a squared surprisal term to test for nonlinearity, by refitting M2 without the 1% most frequent words to address high-leverage items, and by restricting the analysis to words of 3 to 8 phonemes.

## Results

### Pipeline verification and the effect of correction
The corrected tokeniser reproduced the original phoneme strings exactly for all unaffected words and, for affected words, once the four omitted phonemes were removed. All eight verification checks returned True. Correcting the sequences strengthened the relationship between surprisal and length: for Average_Surprisal, the slope changed from −0.1291 to −0.1397 and R² from 0.1255 to 0.1398, while for Max_Surprisal the slope fell from 0.0248 to 0.0008. The correction therefore removed a spurious positive association for the maximum measure and increased the explanatory power of the average measure.

### Surprisal and word frequency
Average surprisal was negatively associated with frequency, as predicted, but the association was weak. In the main type-based leave-one-out model (M1), the standardized coefficient was −0.080 with an R² of 0.006; the frequency-weighted version yielded −0.133 and R² = 0.018. Adding the number of phonemes (M2) increased the coefficient to −0.164 and the R² to 0.042, with `n_phon` itself at −0.207. Adding phoneme density (M3) left surprisal at −0.135 and raised R² to 0.062, with phon_density at +0.152. Thus, although the direction of the effect is consistent across specifications, frequency is only weakly explained by surprisal.

### Surprisal and word length
The relationship with length was considerably stronger. In the main type-based leave-one-out model (N1), the standardized coefficient for surprisal was −0.404 with R² = 0.163. Adding frequency (N2) left the coefficient essentially unchanged at −0.418 and increased R² to 0.193, with a zipf coefficient of −0.175. The Poisson regression agreed in direction, with log-rate changes per bit of −0.1620 in the type-based leave-one-out version and −0.1316 in the frequency-weighted version.

### Incremental predictive value
Surprisal retained predictive value after controlling for the competing variable. In the length models, the coefficient remained at −0.418 when frequency was included, and R² rose from 0.163 to 0.193. In the frequency models, surprisal remained negative at −0.164 after controlling for `n_phon`, with a 95% confidence interval of −0.176 to −0.151 that excluded zero. The incremental contribution was therefore reliable in sign, though modest in magnitude for frequency.

### Robustness checks
The squared surprisal term changed R² by at most 0.0030 across all rows, indicating that a linear specification is adequate. Removing the 1% most frequent words reduced the M2 surprisal coefficient only from −0.164 to −0.157 and R² from 0.042 to 0.036. Restricting the sample to words of 3 to 8 phonemes gave N1 R² values between 0.134 and 0.148 and M1 R² values between 0.019 and 0.037, preserving the overall pattern.

### Summary
Average phoneme surprisal is a weak predictor of word frequency (R² ≈ 0.006–0.018) but a moderate predictor of word length (R² ≈ 0.16–0.19), and it remains negatively associated with both outcomes after controlling for the other variable. These conclusions are subject to several limitations: the frequency distribution has a floor (no word below 411 occurrences), the pronunciations appear partly automatic and have not yet been validated on a sample of words, approximately 90 words share an IPA transcription with another word, and the bigram model ignores morphology and dependencies beyond adjacent phonemes.
