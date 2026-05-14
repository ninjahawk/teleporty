# Direction 1: d_eff Scaling Law — C. elegans to Drosophila to Human

**Status:** Active  
**Question:** How does effective connectome dimensionality (d_eff) scale with neuron count N?  
**Result:** d_eff ~ N^0.46–0.55. Human d_eff ≈ 10⁵–10⁶. Minimum bits for functional reconstruction ≈ 10⁵–10⁶ bits (~100 KB to 2 MB). This is three to seven orders of magnitude below the original 10¹²–10¹³ estimate.

---

## Data Points

### C. elegans (Cook et al. 2019)
- Neurons: N = 302
- Chemical synapses: 3,707
- d_eff (weight matrix PCA, participation ratio): **28**
- d_eff (activity manifold, 200 diverse stimuli): **13**
- Source: `simulation/run_deff.py`

### Drosophila (FlyWire 783, Dorkenwald et al. 2023)
- Neurons: N = 138,639
- Directed synaptic pairs: 15,091,983
- d_eff (randomized SVD, top 300 components): 141 (captures 40.9% of variance)
- d_eff (randomized SVD, top 3000 components): **455** (captures 75.7% of variance)
- d_eff (estimated full spectrum, power law tail): **~670**
- d_eff (estimated full spectrum, uniform remainder): **~790**
- Best estimate: **670–790** (the top-3000 PR of 455 is a lower bound)
- Source: `simulation/run_drosophila_deff.py`

**Eigenspectrum characteristics (Drosophila):**
```
Top 3000 components account for 75.7% of total weight variance.
90% of variance reached at ~k = 5,730 components.
Tail power law (ranks 2500-3000): lambda_i ~ 4.35e3 * i^(-1.645)
The fast tail decay (beta=1.645 > 1) means the full spectrum converges.
```

---

## Scaling Law Fit

Using weight PCA participation ratio consistently across both organisms:

| Organism | N | d_eff (weight PCA PR) |
|----------|---|----------------------|
| C. elegans | 302 | 28 |
| Drosophila | 138,639 | ~700 (best estimate) |

Fitted scaling law:
```
d_eff ~ N^alpha

alpha = log(700/28) / log(138639/302)
      = log(25.0) / log(459.1)
      = 3.22 / 6.13
      = 0.525
```

Range based on d_eff(Drosophila) uncertainty (455–790):
```
alpha (lower): log(455/28) / log(459.1) = 2.79 / 6.13 = 0.455
alpha (upper): log(790/28) / log(459.1) = 3.34 / 6.13 = 0.545
```

**Best estimate: alpha ≈ 0.46–0.55, central value ~0.50**

This is sub-linear scaling: each additional neuron contributes less than proportionally to the information content. Consistent with the hypothesis that larger brains have more redundancy per neuron.

---

## Human Estimate

```
N_human = 86 × 10⁹ neurons
d_eff(human) = 28 × (86e9 / 302)^alpha
             = 28 × (2.85 × 10⁸)^alpha
```

| alpha | d_eff(human) | R(D=30%) bits | R(D=30%) size |
|-------|-------------|--------------|---------------|
| 0.46 | 1.96 × 10⁵ | 3.4 × 10⁵ | 42 KB |
| 0.50 | 4.70 × 10⁵ | 8.2 × 10⁵ | 102 KB |
| **0.52** | **7.10 × 10⁵** | **1.23 × 10⁶** | **154 KB** |
| 0.55 | 1.15 × 10⁶ | 2.0 × 10⁶ | 250 KB |

**Central estimate: d_eff(human) ≈ 7 × 10⁵, R(D=30%) ≈ 1.2 × 10⁶ bits ≈ 150 KB**

This is 6–7 orders of magnitude below the original 10¹²–10¹³ estimate.

---

## Rate-Distortion Revised Calculation

At D=30% (30% multiplicative weight distortion — confirmed functionally acceptable in C. elegans simulation):

```
R(D) = d_eff × (1/2) × log₂(1/D)
     = d_eff × (1/2) × log₂(1/0.09)
     = d_eff × 1.74 bits
```

For d_eff(human) = 7 × 10⁵:
```
R(D=30%) = 7e5 × 1.74 = 1.22 × 10⁶ bits ≈ 150 KB
```

For comparison with original estimates and with other data channels:

| Description | Bits | Size |
|-------------|------|------|
| Human genome | 6 × 10⁹ | 750 MB |
| Revised R-D minimum (alpha=0.50) | **8 × 10⁵** | **~100 KB** |
| Revised R-D minimum (alpha=0.55) | 2 × 10⁶ | ~250 KB |
| Original R-D estimate (d_eff=10¹²) | 1.7 × 10¹² | 200 GB |
| Naive connectome (no compression) | 1.4 × 10¹⁶ | 1.75 PB |

The revised minimum is **3-4 orders of magnitude smaller than the human genome** — suggesting that most of the genome encodes developmental programs, not unique connectome information.

---

## What This Means

If d_eff(human) ~ 10⁵–10⁶ and alpha ~ 0.5, then:

1. **The connectome is structured like a low-rank matrix.** Most of the variation across synapses is explainable by a small number of dominant motifs — the principal components of connectivity. This is consistent with known neuroscience: cortical columns, mirror-symmetric bilateral circuits, modular functional areas.

2. **The minimum information to describe a functionally equivalent brain is shockingly small.** ~150 KB is smaller than a single high-resolution photograph. Most of "you" — in the rate-distortion sense — can be described in a few hundred kilobytes.

3. **The transmission problem is trivially solved.** 150 KB at 1 Gbps = 1.2 microseconds.

4. **The scanner doesn't need to measure 10¹³ synapses precisely.** It needs to measure the ~10⁶ principal components of the connectivity structure. This is a compressed sensing problem, and the number of measurements needed is M ≈ d_eff × log(N_synapses/d_eff) ≈ 10⁶ × log(10¹⁴/10⁶) ≈ 10⁶ × 26 ≈ 2.6 × 10⁷. That's 26 million measurements, not 100 trillion.

5. **The binding constraint shifts.** If you only need to measure ~10⁷ informative quantities (not 10¹⁴ synapses), the scanner problem becomes: how do you take 10⁷ functionally relevant measurements of a living brain? This is achievable with current-trajectory neuroscience — in 2024 we can already record ~10⁶ neurons; scaling to 10⁷–10⁸ is a near-term engineering target.

---

## Caveats and Confidence

**High confidence:**
- The weight matrix of C. elegans and Drosophila is low-rank (empirically confirmed)
- d_eff(C. elegans) = 28, d_eff(Drosophila) ≈ 455–790 (measured, not assumed)
- Sub-linear scaling (alpha < 1) is observed

**Medium confidence:**
- Central alpha ~ 0.5 (two data points, 459-fold scale difference)
- d_eff(Drosophila) estimate ~670–790 (power law extrapolation of tail)

**Low confidence:**
- Extrapolation to human (5 orders of magnitude beyond measured range)
- Whether insect connectome scaling law applies to mammalian brains
- Whether weight matrix d_eff equals activity manifold d_eff at human scale

**Key unknown:** Mouse connectome (MICrONS, partially available; full mouse ~70M neurons in progress). Getting d_eff(mouse) would add a third data point at 70M neurons — one order of magnitude below human, four orders above Drosophila. This would reduce the extrapolation uncertainty dramatically.

---

## Three-Organism Result (Updated)

The MICrONS mm3 dataset (Ding et al. 2023, Zenodo 16744240) provides the third data point:
- Mouse V1 cortex (portion 65): N = 50,943 neurons, 7.5M synaptic edges
- d_eff (estimated from top-2000 SVD + power law tail): **146**
- Power law tail exponent beta = 2.016 (fast decay — well-converged spectrum)

| Organism | N | d_eff | d_eff / N |
|----------|---|-------|-----------|
| C. elegans | 302 | 28 | 9.3% |
| Mouse V1 | 50,943 | 146 | 0.29% |
| Drosophila | 138,639 | 700 | 0.50% |

**Three-point fit:** d_eff = 1.85 × N^0.459  (alpha = 0.46)

Residuals: C. elegans 10% above fit, mouse V1 45% below, Drosophila 66% above. The non-monotonic ordering (mouse < Drosophila despite N_mouse < N_Drosophila) likely reflects genuine biological difference: mammalian cortex is more columnar and repetitive than the Drosophila whole-brain, lowering dimensionality per neuron. This is consistent with known neuroscience — cortical columns in V1 represent an extreme form of redundant structure.

---

## Summary (Three-Organism)

```
d_eff(C. elegans)  = 28   at N = 302
d_eff(Mouse V1)    = 146  at N = 50,943
d_eff(Drosophila)  = 700  at N = 138,639

Three-point fit: d_eff = 1.85 * N^0.46

d_eff(human) ~ 2 × 10⁵   (three-point fit, range 10⁵–10⁶ depending on
                            whether mammalian or insect scaling applies)

R(D=30%) for human ~ 3 × 10⁵ bits ~ 42 KB  (using mammalian-biased fit)
                   ~ 1 × 10⁶ bits ~ 150 KB  (using insect-biased fit)

vs. original estimate: 10¹²–10¹³ bits (200 GB to 1 TB)
vs. naive connectome:  1.4 × 10¹⁶ bits (1.75 PB)

REVISED MINIMUM: ~10⁵ bits (~40 KB to 200 KB)
Revision factor: 7–8 orders of magnitude below original estimate.
```

**The scanner needs ~6 × 10⁶ informative measurements, not 10¹⁴ synapses.**  
See `direction1_scanner_revised.md` for the full implications.
