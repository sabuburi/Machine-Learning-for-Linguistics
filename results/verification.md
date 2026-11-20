# Verification

| check | passed | detail |
|---|---|---|
| n_phon equals number of tokens in phonemes_str | True |  |
| A: rebuilt bigram counts equal Sum_Total | True | (875 bigrams) |
| B: rebuilt P(next|left) and surprisal match the lookup | True |  |
| C: rebuilt phoneme entropy matches ar_phoneme_entropy.csv | True |  |
| D: all 8 per-word metrics equal the columns in ar_comprehensive.csv | True |  |
| E: regressions on n_phon reproduce slopes and R2 (tolerance 1e-4) | True | (max diff 1.53e-14) |
| V1: unaffected words: our tokens equal phonemes_str | True | (22943 words) |
| V2: affected words: our tokens minus the four equal phonemes_str | True | (6822 words) |