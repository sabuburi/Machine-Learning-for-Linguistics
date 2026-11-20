# Review 2 — claims vs results/final_summary.md

File size: 7,780 bytes (~7.6 KB). Tolerance 0.002.

| # | Claim | Value in the file | Match |
|---|---|---|---|
| 1 | Section 1 verification checks all True | All 8 checks: True | YES |
| 2 | type_loo M1 beta_S -0.080, R2 0.006; token_weighted M1 beta_S -0.133, R2 0.018 | type_loo: -0.080 / 0.006; token_weighted: -0.133 / 0.018 | YES |
| 3 | type_loo N1 beta_S -0.404, R2 0.163; token_weighted N1 beta_S -0.374, R2 0.140 | type_loo: -0.404 / 0.163; token_weighted: -0.374 / 0.140 | YES |
| 4 | type_loo M2 beta_S -0.164, n_phon beta -0.207, R2 0.042 | S -0.164, n_phon -0.207, R2 0.042 | YES |
| 5 | type_loo M3 phon_density beta +0.152, R2 0.062 | phon_density 0.152, R2 0.062 | YES |
| 6 | type_loo N2 R2 0.193, zipf beta -0.175 | R2 0.193, zipf -0.175 | YES |
| 7 | Poisson type_loo coef -0.1620; token_weighted coef -0.1316 | type_loo -0.1620; token_weighted -0.1316 | YES |
| 8 | Squared-term change in R2 at most 0.003 in every row | Max delta_r2 = 0.0030 (M1 token_weighted); all others 0.0005–0.0028 | YES |
| 9 | Without top 1%: type_loo M2 beta_S -0.164 to -0.157 | beta_all -0.164, beta_without_top1pct -0.157 | YES |
| 10 | 3–8 phonemes: N1 R2 0.13–0.15; M1 R2 0.019–0.037 | N1: 0.134, 0.133, 0.148, 0.145; M1: 0.037, 0.030, 0.020, 0.019 | YES |
| 11 | Correction: Average_Surprisal slope -0.1291 -> -0.1397, R2 0.1255 -> 0.1398; Max_Surprisal slope 0.0248 -> 0.0008 | Average: -0.1291/0.1255 -> -0.1397/0.1398; Max: 0.0248 -> 0.0008 | YES |
| 12 | 6822 words affected; inventory 42 -> 46; mean phonemes 8.06 -> 8.32; 67 words missing in LOO versions | 6822 (22.9%); 42 vs 46; 8.06 vs 8.32; token_weighted_loo 67, type_loo 67 | YES |

All 12 claims match the file (within 0.002).
