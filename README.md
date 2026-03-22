# Empirical Characterization of an Autonomous Accessibility Flow

**Paper III — Kaelion OTOC KB Series**

> E. F. Perez-Eugenio (2026). *Empirical Characterization of an Autonomous Accessibility Flow: A Universal β-Function and Continuous IR Fixed-Point Spectrum from Out-of-Time-Order Correlators.* Zenodo. DOI: [to be assigned]

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

---

## Overview

This repository contains simulation data, analysis scripts, and figures for Paper III of the Kaelion OTOC KB series.

We report the first systematic empirical characterization of an **autonomous accessibility flow** extracted from out-of-time-ordered correlators (OTOCs) across eleven quantum many-body models spanning four dynamical classes.

**Key results:**
- The effective β-function β_eff(Ω) collapses onto the universal logistic form β = −c Ω(1−Ω) across models (slope = 1.003, χ²/dof = 1.11, p = 0.31)
- The scaling exponent c spans c ∈ [0.17, 4.30], resolving models into Luttinger (c ≈ 1), generic chaotic (c ≈ 2–3), and Schwarzian/JT (c ≈ 4) classes
- Pre-registered prediction c ∈ [1, 4] confirmed with c = 3.41 ± 0.48 for power-law coupling J(r) = 1/r
- c is invariant under change of local observable (1.2%) and UV symmetry class (4%)

---

## Repository Structure

```
otoc-rg-flow/
├── paper3_main.tex                    # LaTeX source
├── kaelion_v8.bib                     # Bibliography
├── figures/                           # Publication figures (PDF)
│   ├── fig1_collapse.pdf              # β_eff/c universal collapse
│   ├── fig2_spectrum.pdf              # Continuous IR spectrum c
│   ├── fig3_prediction.pdf            # Pre-registered prediction confirmed
│   └── fig4_scaling.pdf              # Ω_late(N) scaling + log-log inset
├── data/                              # Simulation data (JSON)
│   ├── ki_J_intermedios.json          # KI J=0.5, 0.7, 1.0 (N=4-12)
│   ├── ki_J_densified.json            # KI J=0.3, 0.6, 0.8, 0.9 (N=4-12)
│   ├── ki_powerlaw_coupling.json      # KI J(r)=1/r (N=4-12)
│   ├── ki_chaotic_N20_5N.json         # KI J=1.0 N=4-20, D_MAX=5N (authoritative)
│   ├── observable_independence_test.json  # V=Z1 vs V=Z2 (N=4-12)
│   ├── syk_q4_results.json            # SYK q=4, 10 seeds (N=4-14)
│   └── syk_q6_results.json            # SYK q=6, 4 seeds (N=4-14)
├── code/                              # Analysis scripts
│   ├── beta_collapse_test.py          # Universal collapse (fig1)
│   ├── collapse_deep_analysis.py      # Detailed collapse analysis
│   └── Tarea_A_optimizada.py          # KI chaotic N=4-20 scaling (fig4)
├── .zenodo.json                       # Zenodo metadata
├── CITATION.cff                       # Citation metadata
├── .gitignore
└── README.md
```

---

## Models

| Model | c | σ(c) | IR Class |
|-------|---|------|----------|
| KI J=0.3 | 0.169 | — | Non-chaotic |
| KI J=0.5 | 0.356 | — | Non-chaotic |
| KI J=1.0 | 0.993 | 0.020 | Luttinger |
| KI J=0.9 | 1.260 | 0.050 | Luttinger |
| KI J=0.6 | 1.916 | — | Chaotic |
| KI J=0.7 | 2.719 | 0.039 | Chaotic |
| KI J=0.8 | 3.116 | 0.111 | Chaotic (max) |
| KI 1/r | 3.406 | 0.477 | Predicted ✓ |
| SYK q=4 | 3.901 | 0.238 | Schwarzian/JT |
| KI mixing | 4.170 | — | Inverse flow |
| SYK q=6 | 4.300 | 0.191 | Schwarzian/JT |

**Methodological note:** `D_MAX = 5N` is mandatory for KI J=1.0.
`D_MAX = 3N` produces a 64% artifact in Ω_late for slow-scrambling models (c ≈ 1).

---

## Data Format

All simulation data is stored as JSON. The authoritative KI chaotic series:

```json
{
  "model": "ki_chaotic",
  "parameters": {"J": 1.0, "h": 0.5, "b": 0.5, "bc": "OBC"},
  "N_values": [4, 6, 8, 10, 12, 14, 16, 18, 20],
  "omega_late": [0.2801, 0.2151, 0.1587, 0.1348, 0.1189,
                 0.1027, 0.0907, 0.0814, 0.0721],
  "D_MAX_factor": 5,
  "fit": {"c": 0.993, "A": 0.642, "R2": 0.9973, "delta_AIC": -4.72}
}
```

---

## Companion Papers

- **Paper I:** Perez-Eugenio, E. F. (2026). *Probing Quantum Scrambling via OTOCs in Digital Circuits.* [10.5281/zenodo.18752608](https://doi.org/10.5281/zenodo.18752608)
- **Paper II:** Perez-Eugenio, E. F. (2026). *Spatial Scrambling Profiles and System-Size Scaling of Ω.* [10.5281/zenodo.19105623](https://doi.org/10.5281/zenodo.19105623)

---

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

---

## Author

**Erick Francisco Perez Eugenio**  
Independent Researcher, León, Guanajuato, Mexico  
ORCID: [0009-0006-3228-4847](https://orcid.org/0009-0006-3228-4847)
