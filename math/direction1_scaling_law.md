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

## The Critical Next Experiment

**MICrONS cubic millimeter dataset** (Lee et al. 2021, available at microns-explorer.org):
- ~75,000 neurons, ~200 million synapses in 1 mm³ of mouse V1
- NOT the full mouse brain, but large enough to measure d_eff at intermediate scale
- Would give a third point at N ≈ 75,000 (between C. elegans and Drosophila in size, similar scale to Drosophila)

Actually more useful: **any complete mouse connectome** when available. Current estimates:
- Mouse brain: ~70 million neurons
- Scaling from N=138,639 (Drosophila) to N=70,000,000 is a 500× increase
- Predicted d_eff(mouse, alpha=0.5) = 700 × √500 ≈ 15,650
- If measured and consistent: strong validation of the power law

---

## Summary

```
d_eff(C. elegans)  = 28        at N = 302
d_eff(Drosophila)  = 455–790   at N = 138,639

Scaling: d_eff ~ N^0.50  (best fit, range 0.46–0.55)

d_eff(human) ~ 7 × 10⁵  (range: 2×10⁵ to 10⁶)

R(D=30%) for human ~ 1.2 × 10⁶ bits ~ 150 KB

vs. original estimate: 10¹²–10¹³ bits (200 GB to 1 TB)
vs. naive connectome:  1.4 × 10¹⁶ bits (1.75 PB)

REVISED MINIMUM: ~10⁵–10⁶ bits (~100 KB to 2 MB)
Revision factor: 6–7 orders of magnitude below original estimate.
```

The scanner needs to measure ~10⁷ informative quantities, not 10¹⁴ synapses.
The transmission is trivial (microseconds at any modern bandwidth).
The binding constraint is still the scanner and the reconstruction, not the information volume.
