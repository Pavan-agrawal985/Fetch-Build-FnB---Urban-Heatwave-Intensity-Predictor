# EDA — Theoretical Conclusions (aligned with `EDA Template_executed.ipynb`)

*Delhi-focused analysis on `india_weather_data.csv`. Below: **concise theory-first conclusions** for each major figure type, then a **short overall EDA synthesis**. Length is tuned to fit **~2 pages** when printed (normal body text).*

---

## Conclusions by graph / figure (theory)

| Figure (as in notebook) | Core statistical idea | What we conclude (theory) |
|---------------------------|------------------------|---------------------------|
| **Missing rate — horizontal bar (top 25)** | Marginal missingness per variable | Systematic gaps across several columns suggest **shared failure modes**, not random typos. This supports **missingness indicators** and **careful imputation**, and warns against **listwise deletion** that can bias rare-class learning. |
| **Missing rate — heatmap by month** | Non-stationarity of missingness | If intensity varies by month, data are likely **not MCAR**; naive global mean/median fill can bias **seasonal regimes** (often when heat/rain extremes matter). Prefer **season- or time-aware** fill rules fit on training data only. |
| **Histogram — `pressure_surface_level`** | Physical plausibility / QC | Pressure is a **row-level consistency check**. Heavy tails or impossible values imply **measurement or unit artefacts**; treat as **quality flags** before modeling rather than letting the algorithm “learn noise.” |
| **Count plot — `heatwave` (with NaN bucket if used)** | Class frequency / prior | Skewed priors imply **cost-sensitive metrics** (precision, recall, F1, PR-AUC); **accuracy is misleading**. Missing labels are **not** a third class to ignore—they shrink usable supervision. |
| **Line — heatwave rate vs month-of-year** | Seasonal stratification of \(P(y)\) | Strong month effects indicate **non-stationarity** and justify **calendar covariates** plus **time-based validation**. Month is a **proxy** for unobserved seasonal forcing—not a causal knob. |
| **Histogram — heatwave streak lengths (hours)** | Temporal clustering / persistence | Short streaks can reflect **true brevity** or **broken continuity** (duplicates, irregular sampling). Autocorrelation violates **i.i.d.** assumptions for naive CV; **time splits** and dependence-aware evaluation are theoretically required. |
| **Dual-axis — monthly rate vs monthly heatwave-hour counts** | Rate vs exposure | **Probability** (rate) and **mass** (counts) answer different questions; conflating them is a **Simpson-style interpretive error**. Both may matter for risk (probability) vs workload (counts). |
| **Grid — univariate histograms / KDEs** | Marginal shape: skew, multimodality | Mixtures and heavy tails imply **non-Gaussian** processes (regimes such as clear vs cloudy). Favour **robust statistics** (Spearman, IQR), **transformations**, or models that do not assume normality of inputs. |
| **Boxplots — features by `heatwave`** | Nonparametric group comparison | Differences in median/IQR show **separability** of \(F(x\mid y=1)\) vs \(F(x\mid y=0)\), not causation. Also reveals **heteroscedasticity**, relevant for linear models and loss choice. |
| **Bar chart — SMD ranking** | Univariate standardized mean shift | Large \|SMD\| flags **candidate predictors**; **multicollinearity** can make many variables look jointly important while individually substitutable. SMD is **screening**, not optimal subset selection. |
| **Heatmap — Spearman correlations** | Monotonic association / dependence | Blocks of correlation imply **latent common drivers** and **multicollinearity**. Good for understanding redundancy; **correlation \(\neq\)** causal effect on `heatwave`. |
| **Scatterplots — key pairs, hue = `heatwave`** | Joint geometry + class overlap | Overlap is expected in meteorology; it bounds **realistic AUC** and motivates **probabilistic** predictions. Curvature hints at **interactions** (non-additive structure). |
| **Line — \(P(\text{heatwave})\) vs binned `max_temperature`** | Nonparametric regression on bins | A rising curve supports a **monotone dose–response** story for temperature as a proxy; bin noise at extremes reflects **small-n** effects. Complement with multivariate models that adjust humidity, wind, and time. |

---

## Overall EDA report conclusion 

Taken together, the executed notebook supports a **structured view of learning feasibility and risk** rather than a single headline correlation. **Data quality is not an add-on:** missingness patterns over time, duplicate timestamps, and physical plausibility checks (pressure) define **which estimands are even well-defined** for a predictive model. The target `heatwave` behaves like a **rare(ish), temporally persistent event** in the Delhi slice; in such settings, classical **i.i.d. cross-validation** is theoretically inappropriate because it leaks **temporal structure** and exaggerates performance. The **right inferential object** is out-of-sample prediction under **forward-in-time** sampling, with metrics that reflect **precision–recall trade-offs** appropriate to early-warning use cases.

Substantively, meteorological inputs exhibit **strong mutual dependence** (temperature, moisture, radiation, clouds). Univariate evidence (boxplots, SMD) therefore **cannot** be read as a list of independent causal levers; it is evidence of **conditional association** with the label under the observed climate mix. That is exactly why the EDA chain moves from **marginals** → **bivariate geometry** → **correlation structure**: to separate **individual signal** from **shared variance** that multivariate models must allocate across features.

The theoretically correct “conclusion of EDA” is thus **conditional**: *if* cleaning respects time order and missing-data structure, *if* features are engineered without future leakage, and *if* evaluation respects temporal dependence, then the visual evidence is **consistent with learnable structure** for heatwave classification using weather covariates. **Causal claims** (e.g., that increasing vegetation would reduce heatwaves) are **out of scope** for this observational hourly panel; the appropriate next step is **predictive modeling with calibrated uncertainty**, not causal attribution.

---

*End — suitable for ~2 pages printed (adjust font/margins in your PDF export if needed).*
