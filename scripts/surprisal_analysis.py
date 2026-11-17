#!/usr/bin/env python3
"""
Average surprisal as a predictor of word frequency and length in Arabic.

Run from the project root:
    py scripts/surprisal_analysis.py --data-dir data --out results --fig figures

Needs: pandas numpy scipy matplotlib statsmodels
    py -m pip install pandas numpy scipy matplotlib statsmodels

Stages (all run in order):
  1. verify   rebuild the original pipeline from `phonemes_str` and check it matches your files exactly
  2. recompute  re-tokenize `IPA` with the four dropped phonemes restored (h-bar, eth, theta, chi);
                compute four versions of surprisal (token-weighted / type-based, each also leave-one-out)
  3. models   frequency (zipf) and length (n_phon) from average surprisal, with checks
  4. figures  five PNG figures
  5. summary  results/final_summary.md with every number filled in from the outputs
Never modifies the input files.
"""
import argparse
import collections
import re
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

matplotlib.use("Agg")
import matplotlib.pyplot as plt

METRICS = ["First_Surprisal", "Last_Surprisal", "Average_Surprisal", "Max_Surprisal",
           "First_Entropy", "Last_Entropy", "Average_Entropy", "Max_Entropy"]
VERSIONS = ["token_weighted", "token_weighted_loo", "type", "type_loo"]
MISSING = "\u0127\u00f0\u03b8\u03c7"  # h-bar, eth, theta, chi
UNIT = re.compile(r"[^\u032A\u02E4\u02D0][\u032A\u02E4\u02D0]*")  # base char + modifiers
CHECKS = []  # (name, passed, detail)


def check(name, passed, detail=""):
    CHECKS.append((name, bool(passed), detail))
    print(f"[{'PASS' if passed else 'FAIL'}] {name}  {detail}")
    return bool(passed)


def md_table(df, digits=3):
    cols = list(df.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        cells = [f"{v:.{digits}f}" if isinstance(v, (float, np.floating)) else str(v) for v in r]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


# ------------------------------------------------------------------ core computations
def tokenize_ipa(ipa):
    """Split IPA into phonemes: base char + modifiers; merge a+j / a+w into aj / aw; drop '.'."""
    units = UNIT.findall(ipa.replace(".", ""))
    out, i = [], 0
    while i < len(units):
        if units[i] == "a" and i + 1 < len(units) and units[i + 1] in ("j", "w"):
            out.append("a" + units[i + 1])
            i += 2
        else:
            out.append(units[i])
            i += 1
    return out


def count_tables(tokens, weights):
    c, left = collections.Counter(), collections.Counter()
    for t, w in zip(tokens, weights):
        for a, b in zip(t, t[1:]):
            c[(a, b)] += w
            left[a] += w
    return c, left


def surprisal_table(c, left):
    return {k: -np.log2(v / left[k[0]]) for k, v in c.items()}


def entropy_table(c, left):
    acc = collections.defaultdict(float)
    for (a, b), v in c.items():
        p = v / left[a]
        acc[a] -= p * np.log2(p)
    return dict(acc)


def surprisal_vectors(tokens, weights, c, left, loo):
    """Per-word array of bigram surprisals. loo=True removes the word's own contribution first."""
    out = []
    for t, w in zip(tokens, weights):
        bg = list(zip(t, t[1:]))
        if not bg:
            out.append(None)
            continue
        if loo:
            own_b = collections.Counter(bg)
            own_l = collections.Counter(a for a, _ in bg)
        s, bad = [], False
        for a, b in bg:
            cab, la = c[(a, b)], left[a]
            if loo:
                cab -= w * own_b[(a, b)]
                la -= w * own_l[a]
            if cab <= 0 or la <= 0:
                bad = True
                break
            s.append(-np.log2(cab / la))
        out.append(None if bad else np.array(s))
    return out


def summarise_s(vecs):
    cols = {k: [] for k in ("First", "Last", "Average", "Max")}
    for v in vecs:
        if v is None:
            for k in cols:
                cols[k].append(np.nan)
        else:
            cols["First"].append(v[0]); cols["Last"].append(v[-1])
            cols["Average"].append(v.mean()); cols["Max"].append(v.max())
    return {f"{k}_Surprisal": np.array(v) for k, v in cols.items()}


def entropy_metrics(tokens, H):
    rows = []
    for t in tokens:
        e = [H.get(a, np.nan) for a in t]
        rows.append((e[0], e[-1], np.nanmean(e), np.nanmax(e)) if e else (np.nan,) * 4)
    a = np.array(rows)
    return {"First_Entropy": a[:, 0], "Last_Entropy": a[:, 1], "Average_Entropy": a[:, 2], "Max_Entropy": a[:, 3]}


def regress(x, y):
    ok = ~(np.isnan(x) | np.isnan(y))
    r = stats.linregress(x[ok], y[ok])
    return r.slope, r.rvalue ** 2


# ------------------------------------------------------------------ stage 1
def stage_verify(df, lk, ent, reg, force):
    print("\n=== Stage 1: verify that the original pipeline can be reproduced ===")
    tokens = df.phonemes_str.str.split().tolist()
    w = df.raw_frequency.tolist()
    check("n_phon equals number of tokens in phonemes_str", np.array_equal(df.n_phon.values, [len(t) for t in tokens]))
    c, left = count_tables(tokens, w)
    ref = lk.set_index("bigram")["Sum_Total"]
    mine = pd.Series({f"{a}_{b}": v for (a, b), v in c.items()})
    ok = set(mine.index) == set(ref.index) and bool((mine.reindex(ref.index) == ref).all())
    check("A: rebuilt bigram counts equal Sum_Total", ok, f"({len(ref)} bigrams)")
    pairs = [tuple(b.split("_")) for b in lk.bigram]
    div = np.array([c[p] / left[p[0]] for p in pairs])
    check("B: rebuilt P(next|left) and surprisal match the lookup",
          np.allclose(div, lk.Divided_Sum) and np.allclose(-np.log2(div), lk.Surprisal))
    H = entropy_table(c, left)
    check("C: rebuilt phoneme entropy matches ar_phoneme_entropy.csv",
          np.allclose([H[p] for p in ent.Left_of_Underscore], ent.Entropy))
    S = surprisal_table(c, left)
    vecs = [np.array([S[(a, b)] for a, b in zip(t, t[1:])]) for t in tokens]
    m = {**summarise_s(vecs), **entropy_metrics(tokens, H)}
    bad = [k for k in METRICS if not np.allclose(m[k], df[k].values, equal_nan=True)]
    check("D: all 8 per-word metrics equal the columns in ar_comprehensive.csv", not bad, f"(differ: {bad})" if bad else "")
    if reg is None:
        print("[SKIP] E: regressions file not found, skipping the regression check")
    else:
        diffs = []
        for _, r in reg.iterrows():
            sl, r2 = regress(df.n_phon.values.astype(float), df[r.metric].values.astype(float))
            diffs.append(max(abs(sl - r.slope), abs(r2 - r.r_squared)))
        check("E: regressions on n_phon reproduce slopes and R2 (tolerance 1e-4)", max(diffs) < 1e-4, f"(max diff {max(diffs):.2e})")
    if not all(p for _, p, _ in CHECKS) and not force:
        sys.exit("Verification failed. Stopping (use --force to continue anyway). See messages above.")


# ------------------------------------------------------------------ stage 2
def stage_recompute(df, out):
    print("\n=== Stage 2: recompute with the four missing phonemes restored ===")
    toks = [tokenize_ipa(s) for s in df.IPA]
    joined = pd.Series([" ".join(t) for t in toks], index=df.index)
    aff = df.IPA.apply(lambda s: any(ch in s for ch in MISSING))
    check("V1: unaffected words: our tokens equal phonemes_str", (joined[~aff] == df.phonemes_str[~aff]).all(), f"({int((~aff).sum())} words)")
    stripped = pd.Series([" ".join(x for x in t if x[0] not in MISSING) for t in toks], index=df.index)
    check("V2: affected words: our tokens minus the four equal phonemes_str", (stripped[aff] == df.phonemes_str[aff]).all(), f"({int(aff.sum())} words)")
    n_new = np.array([len(t) for t in toks])
    inv_old = len({p for s in df.phonemes_str for p in s.split()})
    inv_new = len({p for t in toks for p in t})
    info = dict(n_affected=int(aff.sum()), pct_affected=100 * aff.mean(), inv_old=inv_old, inv_new=inv_new,
                mean_n_old=float(df.n_phon.mean()), mean_n_new=float(n_new.mean()))
    print(f"[INFO] V3: {info['n_affected']} words affected ({info['pct_affected']:.1f}%); inventory {inv_old} -> {inv_new}; "
          f"mean n_phon {info['mean_n_old']:.2f} -> {info['mean_n_new']:.2f} (README expects 6822, 42 -> 46, 8.06 -> 8.32)")

    f = df.raw_frequency.tolist()
    ones = [1] * len(f)
    c1, l1 = count_tables(toks, f)
    c0, l0 = count_tables(toks, ones)
    cor = pd.DataFrame({"word_original": df.word_original, "raw_frequency": df.raw_frequency, "zipf": df.zipf,
                        "phon_density": df.phon_density, "n_phon_original": df.n_phon, "n_phon_corrected": n_new,
                        "tokens": joined})
    loo_nan = {}
    for ver, (c, l, wts, loo) in {"token_weighted": (c1, l1, f, False), "token_weighted_loo": (c1, l1, f, True),
                                  "type": (c0, l0, ones, False), "type_loo": (c0, l0, ones, True)}.items():
        vec = surprisal_vectors(toks, wts, c, l, loo)
        for k, v in summarise_s(vec).items():
            cor[f"{k}_{ver}"] = v
        loo_nan[ver] = int(sum(v is None for v in vec))
        print(f"  {ver}: {loo_nan[ver]} words without a value")
    H1 = entropy_table(c1, l1)
    for k, v in entropy_metrics(toks, H1).items():
        cor[f"{k}_corrected"] = v
    cor.to_csv(out / "ar_corrected.csv", index=False)
    S1 = surprisal_table(c1, l1)
    pd.DataFrame([{"bigram": f"{a}_{b}", "Sum_Total": v, "Left_of_Underscore": a, "Divided_Sum": v / l1[a], "Surprisal": S1[(a, b)]}
                  for (a, b), v in sorted(c1.items())]).to_csv(out / "bigram_lookup_corrected.csv", index=False)
    pd.DataFrame({"Left_of_Underscore": list(H1), "Entropy": list(H1.values())}).to_csv(out / "phoneme_entropy_corrected.csv", index=False)

    rows = []
    for k in METRICS:
        sl0, r0 = regress(df.n_phon.values.astype(float), df[k].values.astype(float))
        newcol = f"{k}_token_weighted" if "Surprisal" in k else f"{k}_corrected"
        sl1, r1 = regress(n_new.astype(float), cor[newcol].values.astype(float))
        rows.append(dict(metric=k, slope_original=sl0, r2_original=r0, slope_corrected=sl1, r2_corrected=r1))
    regtab = pd.DataFrame(rows)
    regtab.to_csv(out / "regression_old_vs_corrected.csv", index=False)
    return cor, regtab, info, loo_nan


# ------------------------------------------------------------------ stage 3
def zs(x):
    return (x - x.mean()) / x.std(ddof=0)


def cv_r2(X, y, k=5, seed=0):
    idx = np.random.default_rng(seed).permutation(len(y))
    A = np.column_stack([np.ones(len(y)), X])
    pred = np.empty(len(y))
    for te in np.array_split(idx, k):
        tr = np.setdiff1d(idx, te)
        b = np.linalg.lstsq(A[tr], y[tr], rcond=None)[0]
        pred[te] = A[te] @ b
    return 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()


def fit_ols(data, y, xs, model, version, subset):
    d = data[[y] + xs].dropna()
    Z = d.apply(zs)
    res = sm.OLS(Z[y], sm.add_constant(Z[xs])).fit(cov_type="HC3")
    ci = res.conf_int()
    cv = cv_r2(Z[xs].values, Z[y].values)
    return [dict(model=model, version=version, subset=subset, outcome=y, n=len(d), term=t, beta=res.params[t],
                 ci_low=ci.loc[t, 0], ci_high=ci.loc[t, 1], p=res.pvalues[t], r2=res.rsquared, adj_r2=res.rsquared_adj,
                 aic=res.aic, cv_r2=cv) for t in xs], res.rsquared


SPECS = {"M1": ("zipf", ["S"]), "M2": ("zipf", ["S", "n_phon"]), "M3": ("zipf", ["S", "n_phon", "phon_density"]),
         "N1": ("n_phon", ["S"]), "N2": ("n_phon", ["S", "zipf"])}


def stage_models(cor, out):
    print("\n=== Stage 3: models ===")
    base = pd.DataFrame({"zipf": cor.zipf, "n_phon": cor.n_phon_corrected, "phon_density": cor.phon_density,
                         "raw_frequency": cor.raw_frequency})
    rows, pois, nonlin, lev = [], [], [], []
    for ver in VERSIONS:
        d = base.copy()
        d["S"] = cor[f"Average_Surprisal_{ver}"]
        for name, (y, xs) in SPECS.items():
            r, _ = fit_ols(d, y, xs, name, ver, "all")
            rows += r
        sub = d[(d.n_phon >= 3) & (d.n_phon <= 8)]
        for name in ("M1", "M2", "N1"):
            y, xs = SPECS[name]
            r, _ = fit_ols(sub, y, xs, name, ver, "3-8 phonemes")
            rows += r
        # Poisson for length (raw units)
        dd = d[["n_phon", "S"]].dropna()
        g = sm.GLM(dd.n_phon, sm.add_constant(dd[["S"]]), family=sm.families.Poisson()).fit(cov_type="HC3")
        ci = g.conf_int()
        pois.append(dict(version=ver, n=len(dd), coef_log_rate_per_bit=g.params["S"], ci_low=ci.loc["S", 0],
                         ci_high=ci.loc["S", 1], p=g.pvalues["S"], pseudo_r2=1 - g.deviance / g.null_deviance))
        # nonlinearity: add squared S
        for name in ("M1", "M2", "N1"):
            y, xs = SPECS[name]
            dn = d[[y] + xs].dropna().copy()
            _, r2a = fit_ols(dn, y, xs, name, ver, "tmp")
            dn["S2"] = dn["S"] ** 2
            _, r2b = fit_ols(dn, y, xs + ["S2"], name, ver, "tmp")
            nonlin.append(dict(model=name, version=ver, r2_linear=r2a, r2_with_S_squared=r2b, delta_r2=r2b - r2a))
        # leverage: remove 1% most frequent words, refit M2
        cut = d.raw_frequency.quantile(0.99)
        r_all, _ = fit_ols(d, "zipf", ["S", "n_phon"], "M2", ver, "all")
        r_cut, _ = fit_ols(d[d.raw_frequency < cut], "zipf", ["S", "n_phon"], "M2", ver, "without top 1% frequent")
        for a, b in zip(r_all, r_cut):
            lev.append(dict(version=ver, term=a["term"], beta_all=a["beta"], beta_without_top1pct=b["beta"],
                            r2_all=a["r2"], r2_without_top1pct=b["r2"], n_without=b["n"]))
    tab = pd.DataFrame(rows)
    tab.to_csv(out / "model_table.csv", index=False)
    pd.DataFrame(pois).to_csv(out / "poisson_table.csv", index=False)
    pd.DataFrame(nonlin).to_csv(out / "nonlinearity.csv", index=False)
    pd.DataFrame(lev).to_csv(out / "leverage_check.csv", index=False)
    print("  saved model_table.csv, poisson_table.csv, nonlinearity.csv, leverage_check.csv")
    return tab, pd.DataFrame(pois), pd.DataFrame(nonlin), pd.DataFrame(lev)


# ------------------------------------------------------------------ stage 4
GREYS = {"token_weighted": "0.1", "token_weighted_loo": "0.35", "type": "0.55", "type_loo": "0.75"}
MARK = {"token_weighted": "o", "token_weighted_loo": "s", "type": "^", "type_loo": "D"}


def stage_figures(cor, tab, regtab, figdir):
    print("\n=== Stage 4: figures ===")
    figdir.mkdir(exist_ok=True)
    # 1 hexbin
    d = cor[["zipf", "Average_Surprisal_type_loo"]].dropna()
    r = np.corrcoef(d.Average_Surprisal_type_loo, d.zipf)[0, 1]
    fig, ax = plt.subplots(figsize=(5, 4))
    hb = ax.hexbin(d.Average_Surprisal_type_loo, d.zipf, gridsize=40, cmap="Greys", mincnt=1, bins="log")
    b = np.polyfit(d.Average_Surprisal_type_loo, d.zipf, 1)
    xs = np.linspace(d.Average_Surprisal_type_loo.min(), d.Average_Surprisal_type_loo.max(), 50)
    ax.plot(xs, np.polyval(b, xs), color="black", lw=1.5, ls="--")
    ax.set_xlabel("Average surprisal (bits, type-based leave-one-out)")
    ax.set_ylabel("Word frequency (Zipf)")
    ax.set_title(f"Frequency vs surprisal (r = {r:.3f}, n = {len(d)})")
    fig.colorbar(hb, label="words (log scale)")
    fig.tight_layout(); fig.savefig(figdir / "fig1_zipf_vs_surprisal.png", dpi=300); plt.close(fig)
    # 2 surprisal by length
    g = cor.groupby("n_phon_corrected")["Average_Surprisal_type_loo"].agg(["mean", "sem", "count"]).reset_index()
    keep, dropped = g[g["count"] >= 30], g[g["count"] < 30]
    fig, ax = plt.subplots(figsize=(5.5, 4))
    ax.errorbar(keep.n_phon_corrected, keep["mean"], yerr=1.96 * keep["sem"], fmt="o-", color="black", capsize=3)
    for _, row in keep.iterrows():
        ax.annotate(f"N={int(row['count'])}", (row.n_phon_corrected, row["mean"]), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=6)
    ax.set_xlabel("Number of phonemes"); ax.set_ylabel("Mean average surprisal (bits)")
    ax.set_title("Surprisal by word length (95% CI)")
    fig.tight_layout(); fig.savefig(figdir / "fig2_surprisal_by_length.png", dpi=300); plt.close(fig)
    # 3 coefficients
    sub = tab[(tab.term == "S") & (tab.subset == "all")]
    models = ["M1", "M2", "M3", "N1", "N2"]
    fig, ax = plt.subplots(figsize=(6, 4))
    for i, ver in enumerate(VERSIONS):
        s = sub[sub.version == ver].set_index("model").reindex(models)
        x = np.arange(len(models)) + (i - 1.5) * 0.15
        ax.errorbar(x, s.beta, yerr=[s.beta - s.ci_low, s.ci_high - s.beta], fmt=MARK[ver], color=GREYS[ver],
                    mec="black", capsize=2, label=ver.replace("_", " "))
    ax.axhline(0, color="black", lw=0.5)
    ax.set_xticks(range(len(models))); ax.set_xticklabels(["M1\nzipf~S", "M2\n+n_phon", "M3\n+density", "N1\nn_phon~S", "N2\n+zipf"], fontsize=7)
    ax.set_ylabel("Standardized beta of surprisal (95% CI)"); ax.legend(fontsize=6)
    fig.tight_layout(); fig.savefig(figdir / "fig3_coefficients.png", dpi=300); plt.close(fig)
    # 4 correlations
    rs = [np.corrcoef(*cor[["zipf", f"Average_Surprisal_{v}"]].dropna().values.T)[0, 1] for v in VERSIONS]
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.bar(range(4), rs, color=[GREYS[v] for v in VERSIONS], edgecolor="black")
    for i, v in enumerate(rs):
        ax.text(i, v - 0.005, f"{v:.3f}", ha="center", va="top", fontsize=7)
    ax.set_xticks(range(4)); ax.set_xticklabels([v.replace("_", "\n") for v in VERSIONS], fontsize=7)
    ax.set_ylabel("r(zipf, average surprisal)")
    fig.tight_layout(); fig.savefig(figdir / "fig4_surprisal_versions.png", dpi=300); plt.close(fig)
    # 5 correction effect
    fig, ax = plt.subplots(figsize=(6, 4))
    y = np.arange(len(regtab))
    ax.scatter(regtab.slope_original, y, marker="o", color="white", edgecolor="black", label="original (42 phonemes)", zorder=3)
    ax.scatter(regtab.slope_corrected, y, marker="D", color="black", label="corrected (46 phonemes)", zorder=3)
    ax.axvline(0, color="grey", lw=0.5)
    ax.set_yticks(y); ax.set_yticklabels(regtab.metric, fontsize=7); ax.invert_yaxis()
    ax.set_xlabel("Slope on number of phonemes"); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(figdir / "fig5_correction_effect.png", dpi=300); plt.close(fig)
    print("  saved fig1..fig5 in", figdir)
    return dropped


# ------------------------------------------------------------------ stage 5
def stage_summary(cor, regtab, info, loo_nan, tab, pois, nonlin, lev, dropped, out):
    print("\n=== Stage 5: summary ===")
    L = ["# Results summary (generated by scripts/surprisal_analysis.py)", ""]
    L += ["## 1. Verification checks", "", md_table(pd.DataFrame(CHECKS, columns=["check", "passed", "detail"])), ""]
    L += ["## 2. Data and correction", "",
          f"- Words: {len(cor)}. Words whose IPA contains at least one of the four dropped phonemes: "
          f"{info['n_affected']} ({info['pct_affected']:.1f}%).",
          f"- Phoneme inventory: {info['inv_old']} (original) vs {info['inv_new']} (corrected). "
          f"Mean number of phonemes: {info['mean_n_old']:.2f} vs {info['mean_n_new']:.2f}.",
          "- Words without a value per surprisal version (leave-one-out removes words whose bigram occurs only in that word): "
          + ", ".join(f"{k}: {v}" for k, v in loo_nan.items()) + ".", "",
          "Regression of each metric on number of phonemes, original vs corrected phoneme sequences:", "",
          md_table(regtab, 4), ""]
    L += ["## 3. Methods (how the numbers were computed)", "",
          "Phoneme sequences were obtained by tokenizing the IPA column (base symbol plus length, dental and pharyngealization "
          "marks; a+j and a+w merged into diphthongs), which restores four phonemes dropped in the original sequences. "
          "For each adjacent phoneme pair, the count was the sum over words of the word's frequency (token-weighted) or of 1 "
          "(type-based) times its occurrences in the word. Surprisal of a bigram is -log2 of its count divided by the total count "
          "of bigrams with the same first phoneme. Leave-one-out versions remove a word's own contribution from the counts before "
          "computing its surprisal. A word's average surprisal is the mean over its bigrams. Frequency is on the Zipf scale. "
          "Models are OLS on standardized variables with HC3 robust standard errors; cross-validated R2 uses 5 folds (seed 0).", ""]
    t = tab[(tab.subset == "all")]
    rows = []
    for ver in VERSIONS:
        r = {"surprisal version": ver}
        v = t[t.version == ver]
        d = base_corr(cor, ver)
        r["r(zipf,S)"] = d
        for m in ("M1", "M2", "M3", "N1", "N2"):
            s = v[(v.model == m) & (v.term == "S")].iloc[0]
            r[f"{m} beta_S"] = s.beta
            r[f"{m} R2"] = s.r2
        rows.append(r)
    L += ["## 4. Main results (all words; beta_S = standardized coefficient of average surprisal)", "", md_table(pd.DataFrame(rows)), ""]
    L += ["Other terms in the models (standardized beta, type_loo version):", "",
          md_table(t[(t.version == "type_loo")][["model", "term", "n", "beta", "ci_low", "ci_high", "r2", "cv_r2"]]), ""]
    L += ["## 5. Checks on the models", "",
          "Words with 3 to 8 phonemes only:", "",
          md_table(tab[(tab.subset == "3-8 phonemes") & (tab.term == "S")][["model", "version", "n", "beta", "r2", "cv_r2"]]), "",
          "Poisson regression of the number of phonemes on surprisal (log-rate change per bit):", "", md_table(pois, 4), "",
          "Adding a squared surprisal term (change in R2):", "", md_table(nonlin, 4), "",
          "Refit of M2 without the 1% most frequent words:", "", md_table(lev, 3), ""]
    L += ["## 6. Figures", "",
          "- fig1_zipf_vs_surprisal.png, fig2_surprisal_by_length.png, fig3_coefficients.png, fig4_surprisal_versions.png, fig5_correction_effect.png",
          f"- Fig. 2 only shows lengths with at least 30 words; left out: "
          + (", ".join(f"{int(a)} phonemes (N={int(b)})" for a, b in zip(dropped.n_phon_corrected, dropped['count'])) or "none") + ".", ""]
    L += ["## 7. Limitations", "",
          "- The pronunciations in the data look partly automatic (for example, some vowels appear wrong); errors flow into every surprisal value. Check a sample.",
          "- Frequency has a floor (no word below 411 occurrences), so nothing can be said about rare words.",
          "- A bigram model ignores morphology and anything longer than two phonemes.",
          "- With about 30,000 words almost every coefficient is significant; interpret effect sizes and cross-validated R2.",
          "- About 90 words share an IPA transcription with another word. Token-weighted surprisal contains the word's own frequency (see the leave-one-out versions).", ""]
    (out / "final_summary.md").write_text("\n".join(L), encoding="utf-8")
    (out / "verification.md").write_text("# Verification\n\n" + md_table(pd.DataFrame(CHECKS, columns=["check", "passed", "detail"])), encoding="utf-8")
    print("  saved final_summary.md and verification.md")


def base_corr(cor, ver):
    d = cor[["zipf", f"Average_Surprisal_{ver}"]].dropna()
    return float(np.corrcoef(d.zipf, d[f"Average_Surprisal_{ver}"])[0, 1])


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--out", default="results")
    ap.add_argument("--fig", default="figures")
    ap.add_argument("--force", action="store_true", help="continue even if a verification check fails")
    ap.add_argument("--skip-figures", action="store_true")
    a = ap.parse_args()
    data, out, fig = Path(a.data_dir), Path(a.out), Path(a.fig)
    out.mkdir(exist_ok=True)
    need = ["ar_comprehensive.csv", "ar_bigram_lookup.csv", "ar_phoneme_entropy.csv"]
    miss = [n for n in need if not (data / n).exists()]
    if miss:
        sys.exit(f"Missing in {data}: {miss}")
    df = pd.read_csv(data / "ar_comprehensive.csv", low_memory=False)
    lk = pd.read_csv(data / "ar_bigram_lookup.csv")
    ent = pd.read_csv(data / "ar_phoneme_entropy.csv")
    reg = None
    for n in ("regressions_S_E_vs_n_phon.csv", "regressions_S&E_vs_n_phon.csv"):
        if (data / n).exists():
            reg = pd.read_csv(data / n)
            break
    stage_verify(df, lk, ent, reg, a.force)
    cor, regtab, info, loo_nan = stage_recompute(df, out)
    tab, pois, nonlin, lev = stage_models(cor, out)
    dropped = stage_figures(cor, tab, regtab, fig) if not a.skip_figures else pd.DataFrame({"n_phon_corrected": [], "count": []})
    stage_summary(cor, regtab, info, loo_nan, tab, pois, nonlin, lev, dropped, out)
    print("\nDone. Read results/final_summary.md first.")


if __name__ == "__main__":
    main()
