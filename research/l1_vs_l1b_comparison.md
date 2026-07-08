# Gate comparison: 4B (L1) vs 27B (L1)

- 4B: domain **fail**, contention=psalm
- 27B: domain **fail**, contention=none

| hypothesis | 4B value | 27B value | Δ | threshold | 4B pass | 27B pass | context (27B) |
|---|---|---|---|---|---|---|---|
| H_bands | 0.3061 | 0.2694 | -0.0367 | 0.15 | True | True | bands=[[0, 8], [8, 54], [54, 64]] |
| H_modulation | 0.1000 | 0.5500 | +0.4500 | 0.5 | False | True | null=0.06824999999999999, band n=21 |
| H_report | 0.1800 | 0.1243 | -0.0557 | 0.4 | False | False | p=1.00e-04, last-layer ρ=0.3534 |
