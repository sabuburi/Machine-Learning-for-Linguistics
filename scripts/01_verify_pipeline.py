#!/usr/bin/env python

import os
import math
import numpy as np
import pandas as pd
from scipy import stats

PROJECT_ROOT = os.getcwd()
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")

CSV = os.path.join(DATA_DIR, "ar_comprehensive.csv")
BIGRAM_LOOKUP = os.path.join(DATA_DIR, "ar_bigram_lookup.csv")
PHONEME_ENTROPY = os.path.join(DATA_DIR, "ar_phoneme_entropy.csv")
REGRESSIONS = os.path.join(DATA_DIR, "regressions_S_E_vs_n_phon.csv")

FAIL = False

print("Loading CSV ...")
df = pd.read_csv(CSV)
print(f"  rows={df.shape[0]}, cols={df.shape[1]}")

PHONEMES_COL = "phonemes_str"
N_PHON_COL = "n_phon"

# CHECK A: Bigram counts
print("\nCHECK A: bigram counts vs ar_bigram_lookup.csv")

bigram_counts = {}

for _, row in df.iterrows():
    freq = float(row["raw_frequency"])
    phonemes = str(row[PHONEMES_COL]).split()

    for i in range(len(phonemes) - 1):
        bigram = (phonemes[i], phonemes[i + 1])
        bigram_counts[bigram] = bigram_counts.get(bigram, 0) + freq

lookup_df = pd.read_csv(BIGRAM_LOOKUP)
print(f"  lookup bigrams={len(lookup_df)}")

mismatches = 0

for _, row in lookup_df.iterrows():
    bigram_str = str(row["bigram"])
    parts = bigram_str.split("_", 1)

    if len(parts) != 2:
        print(f"    INVALID BIGRAM FORMAT: {bigram_str}")
        mismatches += 1
        continue

    bigram = tuple(parts)
    expected = row["Sum_Total"]
    got = bigram_counts.get(bigram, 0)

    if not np.isclose(got, expected, atol=1e-6):
        mismatches += 1

        if mismatches <= 5:
            print(
                f"    MISMATCH: {bigram_str} "
                f"expected={expected} got={got}"
            )

print(f"  total mismatches={mismatches}")

if mismatches > 0:
    FAIL = True


# CHECK B: P(next|left) and surprisal
print("\nCHECK B: P(next|left) and surprisal vs lookup")

left_totals = {}

for (left, right), count in bigram_counts.items():
    left_totals[left] = left_totals.get(left, 0) + count

if "Divided_Sum" in lookup_df.columns and "Surprisal" in lookup_df.columns:

    b_mismatches = 0

    for _, row in lookup_df.iterrows():
        bigram_str = str(row["bigram"])
        parts = bigram_str.split("_", 1)

        if len(parts) != 2:
            continue

        left, right = parts
        count = bigram_counts.get((left, right), 0)

        total_left = left_totals.get(left, 0)

        p = count / total_left if total_left > 0 else 0

        calculated_surprisal = (
            -math.log2(p) if p > 0 else float("inf")
        )

        divided_sum = row["Divided_Sum"]
        reference_surprisal = row["Surprisal"]

        divided_ok = np.isclose(
            calculated_surprisal, divided_sum,
            atol=1e-6, equal_nan=True
        )

        surprisal_ok = np.isclose(
            calculated_surprisal, reference_surprisal,
            atol=1e-6, equal_nan=True
        )

        if not divided_ok or not surprisal_ok:
            b_mismatches += 1

            if b_mismatches <= 5:
                print(
                    f"    MISMATCH: {bigram_str} "
                    f"P={p:.6f} "
                    f"calculated={calculated_surprisal:.6f} "
                    f"Divided_Sum={divided_sum} "
                    f"Surprisal={reference_surprisal}"
                )

    print(f"  bigram surprisal mismatches={b_mismatches}")

    if b_mismatches > 0:
        FAIL = True

else:
    print("  (Divided_Sum / Surprisal columns not found in lookup)")


# CHECK C: Phoneme entropy
print("\nCHECK C: phoneme entropy vs ar_phoneme_entropy.csv")

phoneme_next = {}
phoneme_total = {}

for _, row in df.iterrows():
    freq = float(row["raw_frequency"])
    phonemes = str(row[PHONEMES_COL]).split()

    for i in range(len(phonemes) - 1):
        pn = phonemes[i]
        nn = phonemes[i + 1]

        phoneme_next.setdefault(pn, {})
        phoneme_next[pn][nn] = phoneme_next[pn].get(nn, 0) + freq

        phoneme_total[pn] = phoneme_total.get(pn, 0) + freq

entropy_df = pd.read_csv(PHONEME_ENTROPY)
print(f"  reference entropy rows={len(entropy_df)}")

e_mismatches = 0
missing_entropy = 0

for _, row in entropy_df.iterrows():
    phoneme = row["phoneme"]
    ref_entropy = row["entropy"]

    if phoneme not in phoneme_next:
        missing_entropy += 1
        continue

    total = phoneme_total[phoneme]

    p_dist = {
        next_p: cnt / total
        for next_p, cnt in phoneme_next[phoneme].items()
    }

    got_entropy = -sum(
        p * math.log2(p)
        for p in p_dist.values()
        if p > 0
    )

    if not np.isclose(got_entropy, ref_entropy, atol=1e-4):
        e_mismatches += 1

        if e_mismatches <= 5:
            print(
                f"    MISMATCH: {phoneme} "
                f"computed={got_entropy:.6f} "
                f"ref={ref_entropy:.6f}"
            )

print(f"  entropy mismatches={e_mismatches}")
print(f"  phonemes without computed entropy={missing_entropy}")

if e_mismatches > 0 or missing_entropy > 0:
    FAIL = True


# CHECK D: Average_Surprisal reconstruction
print("\nCHECK D: Average_Surprisal reconstruction")

surprisal_per_word = {}

for _, row in df.iterrows():
    word = row["word"]
    phonemes = str(row[PHONEMES_COL]).split()

    surps = []

    for i in range(len(phonemes) - 1):
        bigram = (phonemes[i], phonemes[i + 1])

        count = bigram_counts.get(bigram, 0)
        left = bigram[0]

        left_total = left_totals.get(left, 0)

        p = count / left_total if left_total > 0 else 0

        s = -math.log2(p) if p > 0 else float("inf")
        surps.append(s)

    if surps:
        avg_surp = np.mean(surps)
        first_surp = surps[0]
        last_surp = surps[-1]
        max_surp = max(surps)
    else:
        avg_surp = first_surp = last_surp = max_surp = float("nan")

    surprisal_per_word[word] = {
        "Average_Surprisal": avg_surp,
        "First_Surprisal": first_surp,
        "Last_Surprisal": last_surp,
        "Max_Surprisal": max_surp
    }

actual_avg = df["Average_Surprisal"].values

rebuilt_avg = np.array([
    surprisal_per_word.get(w, {}).get("Average_Surprisal", np.nan)
    for w in df["word"]
])

match = np.allclose(
    actual_avg,
    rebuilt_avg,
    equal_nan=True
)

print(f"  np.allclose Average_Surprisal: {match}")

if not match:
    diff = np.abs(actual_avg - rebuilt_avg)
    bad = np.where(
        ~np.isclose(actual_avg, rebuilt_avg, atol=1e-4, equal_nan=True)
    )[0]

    print(
        f"  {len(bad)} words with diff > 1e-4; "
        f"first few: {bad[:5]}"
    )

    FAIL = True


# CHECK E: Regression of metrics on n_phon
print("\nCHECK E: Regression of metrics on n_phon")

phoneme_entropy = {}

for pn in phoneme_next:
    total = phoneme_total[pn]

    p_dist = {
        next_p: cnt / total
        for next_p, cnt in phoneme_next[pn].items()
    }

    phoneme_entropy[pn] = -sum(
        p * math.log2(p)
        for p in p_dist.values()
        if p > 0
    )

word_entropies = {}

for _, row in df.iterrows():
    word = row["word"]
    phonemes = str(row[PHONEMES_COL]).split()

    entropies = [
        phoneme_entropy[left]
        for i in range(len(phonemes) - 1)
        if (left := phonemes[i]) in phoneme_entropy
    ]

    word_entropies[word] = (
        np.mean(entropies) if entropies else np.nan
    )

metrics = [
    "First_Surprisal",
    "Last_Surprisal",
    "Average_Surprisal",
    "Max_Surprisal",
    "First_Entropy",
    "Last_Entropy",
    "Average_Entropy",
    "Max_Entropy"
]

reg_df = pd.read_csv(REGRESSIONS)
all_pass = True

for metric in metrics:

    actual = pd.to_numeric(df[metric], errors="coerce").values
    n_phon = pd.to_numeric(df[N_PHON_COL], errors="coerce").values

    valid = np.isfinite(actual) & np.isfinite(n_phon)

    if valid.sum() < 2 or len(np.unique(n_phon[valid])) < 2:
        print(f"  {metric}: insufficient valid data for regression")
        all_pass = False
        continue

    slope, intercept, r_value, p_value, std_err = stats.linregress(
        n_phon[valid],
        actual[valid]
    )

    r2 = r_value ** 2

    ref_row = (
        reg_df[reg_df["Metric"] == metric]
        if "Metric" in reg_df.columns
        else None
    )

    if ref_row is not None and len(ref_row) > 0:

        ref_slope = ref_row["slope"].values[0]
        ref_r2 = ref_row["R2"].values[0]

        slope_ok = abs(slope - ref_slope) < 1e-4
        r2_ok = abs(r2 - ref_r2) < 1e-4

        print(
            f"  {metric}: "
            f"slope={slope:.6f} (ref {ref_slope:.6f}) "
            f"R2={r2:.6f} (ref {ref_r2:.6f}) "
            f"slope_ok={slope_ok} r2_ok={r2_ok}"
        )

        if not slope_ok or not r2_ok:
            all_pass = False

            print(
                f"    MISMATCH: "
                f"slope diff={abs(slope-ref_slope):.6f} "
                f"r2 diff={abs(r2-ref_r2):.6f}"
            )

    else:
        print(
            f"  {metric}: slope={slope:.6f} "
            f"R2={r2:.6f} (no reference found)"
        )

if all_pass:
    print("  ALL 8 regressions match reference")
else:
    FAIL = True


# FINAL RESULT
print("\n" + "=" * 60)

if FAIL:
    print("RESULT: FAIL - one or more checks failed")
else:
    print("RESULT: PASS - all checks passed")

print("=" * 60)
