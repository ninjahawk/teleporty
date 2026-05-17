# Scan Inverse Problem: Recovering a Unified Connectome

**Status:** [THIS PROJECT] — partial result. Best approach gets r=0.72 on C. elegans
weight matrix, with chemotaxis behavior nearly preserved but tap-circuit reconstruction
still failing. Identifies the next concrete bottleneck in Direction 1.

**Date:** 2026-05-17

---

## The Problem

A neural scanner produces activity recordings `r(t)` from K probe conditions. We want
to recover the synaptic weight matrix W such that `r(t+1) = f(W r(t) + G r(t) + I(t))`
where f is the network's nonlinearity, G is the gap-junction matrix (assumed known
from structural EM), and I(t) are the applied stimuli.

The standalone per-class K=1 result (`run_generative_model_targeted_pulse.py`) shows
that a SINGLE behavior can be reconstructed from a single targeted probe condition:
- K=1 tap-targeted: div_tap = 0.005 ✓ (great), div_chem = 0.44 ✗
- K=1 chem-targeted: div_chem = 0.007 ✓ (great), div_tap not tested in isolation

The teleportation pipeline requires a **unified W** that drives ALL behaviors of the
target organism simultaneously, because the reconstructed body has one connectome,
not one per behavior. The unified-W problem is harder than the per-class problem.

---

## Approaches Tested

Setup: C. elegans, N=300 neurons, 3707 chemical synapses, 2188 gap junctions.
K=20 probe conditions: 2 tap-targeted + 2 chem-targeted + 16 compositional
(random subsets of 30-80 neurons at moderate amplitude). All approaches use ridge
regression with adaptive λ.

| Approach | Mechanism | r | div_tap | div_chem |
|----------|-----------|---|---------|----------|
| A — combined ridge | All K=20 conditions stacked, regularized least squares over full N=300 unknowns per neuron | 0.11 | 0.71 ✗ | 0.51 ✗ |
| B — weighted blend | Per-condition per-neuron W_hat_k, softmax-weighted blend by score | 0.06 | 0.72 ✗ | 0.50 ✗ |
| C — iterative refinement | Score-weighted iterative least squares, 3 passes | 0.06 | 0.71 ✗ | 0.51 ✗ |
| **D — support-aware combined** | **Restrict regression to known support (~12 unknowns/neuron), use all K conditions** | **0.72** | **0.57 ✗** | **0.056 ✗** |
| E — support + condition-weighted | D + per-neuron condition variance weighting | 0.62 | 0.58 ✗ | 0.11 ✗ |
| F — support-aware modular | D + per-neuron pick best condition by variance | 0.02 | 0.67 ✗ | 0.33 ✗ |

**Verdict:** D is the clear winner. Knowing the binary topology (which synapses exist,
even without knowing their weights) is enormously informative.

---

## Key Finding: Structural Support Is the Dominant Lever

Approach A vs D: same data, same regression machinery. The only difference is whether
the binary support is known a priori.

```
A (unknown support, N unknowns/neuron):  r = 0.11
D (known support, ~12 unknowns/neuron):  r = 0.72
```

**A 6.5× improvement in Pearson r purely from knowing the connectome topology.**

This validates the two-scan model for neural reconstruction:
1. **Structural scan:** electron microscopy of synaptic contacts. Provides binary
   topology (which neuron contacts which). Already feasible for ≤1 mm³ tissue
   blocks (MICrONS, FlyWire).
2. **Functional scan:** activity recording under structured probe stimuli. Provides
   weights at the known-topology positions.

Combined, these two scans give a much better unified W than activity alone.

**[ESTABLISHED]** EM-based connectome topology recovery is the state of the art for
small organisms (Cook 2019, MICrONS 2024, FlyWire 2024).
**[THIS PROJECT]** Quantifying how much the topology constraint helps the inverse
problem — 6.5× in Pearson r, ~10× in chemotaxis divergence (0.51 → 0.056).

---

## Why Tap Still Fails

The chem circuit nearly passes (div_chem = 0.056, just over the 5% threshold).
The tap circuit remains far from passing (div_tap = 0.57).

**Why the asymmetry:** tap-sensor chemical weights are 27× smaller than the global
mean (from `run_circuit_diagnostic.py`). In combined regression — even support-aware —
the least-squares objective is dominated by larger-signal contributions. The tap
weights get pulled toward whatever pattern best fits the bulk of the data, which
includes mostly non-tap-driven dynamics.

This is the **small-signal washout problem**. Mathematically:

For a neuron j with two input pathways: pathway A with weight w_A and large input
variance σ_A², pathway B with weight w_B and small input variance σ_B², where
w_A σ_A² >> w_B σ_B², the joint regression's gradient with respect to w_B is small
relative to the noise floor. The estimator's variance on w_B is high.

```
Var(ŵ_B) ∝ σ_noise² / (σ_B² · T_effective)
```

For tap weights (small magnitudes, small tap-condition variance, only 2 of 20
conditions targeted): the estimator variance on tap weights is large.

---

## Paths to Close the Gap

Approaches that should be tried (not yet implemented):

1. **Behavior-class data oversampling.** Instead of 2 tap-targeted out of 20
   conditions, use 10+ tap-targeted conditions. Each tap-circuit neuron gets enough
   relevant data to overcome the small-signal floor.

2. **Frequency-rich stimuli.** 30 ms square pulses excite only a narrow band. Chirp
   stimuli, white-noise stimuli, or sinusoidal sweeps would excite more modes of the
   tap circuit and increase observability of all tap weights simultaneously.

3. **Circuit decomposition.** Identify tap-circuit neurons (structural definition:
   directly or indirectly downstream of tap sensors). Fit their weights using ONLY
   tap-targeted conditions. Combine with chem-circuit fit from chem conditions.
   This is the per-circuit modular approach applied within the support-aware framework.

4. **L1 / sparse priors.** Ridge regression shrinks toward zero uniformly. L1 priors
   (lasso) shrink toward exact zero, which matches the biological prior that some
   support-positions may actually be very weak or vestigial.

5. **Nonlinear identification.** The rate model has a tanh nonlinearity. Linear
   regression on the linearized form (via inverse-tanh transform) accumulates error
   when activity is near saturation. A direct nonlinear fit (gradient descent on
   the rate-model loss) would avoid this.

6. **Bayesian inference.** Posterior over W given activity data, with a prior that
   encodes known weight magnitude distributions (e.g., log-normal). The MAP estimate
   would automatically discount weights below the data's resolving power.

---

## Scaling Implications

For C. elegans (300 neurons, ~12 inputs per neuron): support-aware gets r=0.72.

For human (86 billion neurons, ~10⁴ inputs per neuron): the support-aware reduction
is even more dramatic — from 86e9 unknowns per neuron down to 10⁴. The structural EM
scan provides this. The activity scan then needs to estimate 10⁴ weights per neuron
from probe data.

**Conjecture [THIS PROJECT]:** At human scale, the structural-functional combined
approach should work AS LONG AS the small-signal washout problem is solved by stimulus
design. The 6.5× Pearson improvement at C. elegans scale should extrapolate to even
larger improvements at human scale, because the support-imposed sparsity is more
extreme (~10⁴ / 86e9 = 10⁻⁷ vs C. elegans 12/300 = 0.04).

The fundamental information-theoretic bound (42 KB per the rate-distortion derivation)
remains the floor. The question is whether the scanner can ACHIEVE that bound, not
whether the bound is correct.

---

## What This Means for the Project

The teleportation pipeline now has TWO open binding constraints:

1. **Fabricator** (engineering): 10¹⁰ cells/s, 10⁷ nozzles, hypothermic at 4 °C.
   No physics barrier. Building it is a generational engineering project, comparable
   to semiconductor fabs.

2. **Scan inverse problem** (algorithm + measurement): recovering a unified W that
   simultaneously drives all behaviors. Open at C. elegans scale; tap-circuit
   reconstruction is the immediate blocker. Solutions exist (see Paths above) but
   not yet implemented.

Before this work, only #1 was identified as the bottleneck. The scan was implicitly
assumed solved because the per-class K=1 result worked. The unified-W requirement
makes this a separate, real problem.

The compression and transmission stages remain solved at all scales tested.
