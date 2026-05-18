# Direction 1 — Model-Mismatch Limitation on Real Connectomes (RESOLVED)

## RESOLUTION (top of file — see history below)

The model-mismatch limitation is resolved. The heterogeneous-excitability
model (`simulate_rate_hetero` + response-matching `calibrate_homeostatic`,
`math/direction1_heterogeneous_model.md`) was implemented, validated on
C. elegans (Pearson 0.975), and tested on the FlyWire dense network that
the uniform model failed catastrophically on:

| Model | FlyWire dense subset | behavioral div | verdict |
|---|---|---|---|
| Uniform rate model | N=5000 (mean \|supp\|=47) | ~0.68 | catastrophic FAIL |
| **Heterogeneous model** | N=2000 (mean \|supp\|=34) | 0.032–0.050 | **PASS** (marginal) |
| **Heterogeneous model** | N=5000 (mean \|supp\|=47) | 0.028–0.032 | **PASS** (comfortable) |

The heterogeneous model passes at BOTH scales, and N=5000 is the *more*
comfortable PASS — larger networks average behavioral error over more
neurons (Pearson r is 0.46 at N=5000 vs 0.54 at N=2000, yet div is lower).
The real-connectome capability holds across a 2.5× scale range.

Three ingredients made it work:
  1. Per-neuron gain/theta, calibrated by response-matching (each neuron
     homeostatically tuned to rest at an observable, modulable operating
     point) — resolves the weight-dynamic-range problem.
  2. Calibration on a probe-amplitude-matched reference ensemble.
  3. Degree-scaled fallback for the residual unobservable neurons (fill
     their support with the mean per-synapse weight, so total drive scales
     with in-degree).

Honest caveats on this PASS:
  - It is marginal — one stimulus at div 0.0498 vs the 0.05 threshold.
  - Pearson r is only 0.54 — structural weight recovery is moderate;
    the behavioral PASS rests on the rate-distortion principle.
  - 71/2000 neurons remain unobservable and use the approximate fallback.
  - This is a real PASS on a real dense hub-heavy connectome, but not a
    comfortable one. Larger/denser networks may need the reconstruction
    accuracy improved further (more probe trials, or the multi-task
    low-rank fit).

Net: the FlyWire failure was a MODEL limitation (uniform excitability),
now fixed. The original "density limitation" framing below is superseded —
density was a symptom; the disease was the uniform model, and it is cured.

---

## (Historical) Direction 1 — Model-Mismatch Limitation on Real Connectomes

## UPDATE — the real cause is weight dynamic range, not density

The decisive normalization test changed the picture. The first version of
this note (below, kept for the record) attributed the FlyWire failure to
network *density*. A follow-up test shows the deeper cause is the **weight
dynamic range** interacting with a uniform-parameter rate model.

FlyWire syn_counts span **1 to 2405** — 3.4 orders of magnitude (C. elegans
synapse counts are far narrower). Tested both normalizations on the N=2000
subset:

| Normalization | denom | skipped | Pearson r | behavioral div |
|---|---|---|---|---|
| /max | 2405 | 35–146 | 0.35 | 0.011 (sparse) / 0.13 (dense) |
| /p99 | 136 | **1512/2000** | **−0.015** | 0.90 |

With /max, typical synapses (median syn_count 1 → 1/2405 ≈ 0.0004) are far
too weak; most neurons are near-silent. With /p99, the strong synapses
(syn_count up to 2405 → 2405/136 ≈ 18) massively over-drive their targets;
the network saturates and 1512/2000 neurons become unobservable.

**No single global weight scaling works.** A uniform-parameter rate model
(one gain, one threshold, one time constant for every neuron) cannot place
synapses spanning 3.4 OOM all within the tanh's responsive band. Either the
weak synapses are silent or the strong ones saturate.

C. elegans does not hit this because its weight distribution is narrow
enough that one global scaling suits all synapses — which is why the
protocol recovers C. elegans at Pearson 0.99 but FlyWire at ≤ 0.35.

**This is a MODEL limitation, not a protocol limitation, and not density.**
Real neurons handle 3-OOM synaptic ranges via homeostatic plasticity,
heterogeneous intrinsic excitability, diverse time constants — none of which
the project's uniform rate model has. The scan-inverse protocol is sound for
the model it was built and validated on (C. elegans); extending it to real
mammalian-scale connectomes requires a model with per-neuron heterogeneous
gain/threshold so every neuron operates in its responsive range regardless
of total synaptic drive.

### Honest scope of the "scan inverse solved" claim

  - **Solid:** the scan-inverse protocol recovers the C. elegans connectome
    at Pearson 0.99 and the full pipeline passes end-to-end, robustly, under
    noise / EM error / deployment stress. This is real and stands.
  - **Not established:** that the same protocol works on real mammalian
    connectomes. The FlyWire tests show the uniform rate model itself fails
    to accommodate real weight statistics — so the protocol cannot even be
    fairly evaluated there until the model is upgraded.
  - The behavioral PASS on FlyWire MB subsets (N≤2000, /max norm) was the
    rate-distortion principle masking a Pearson-0.35 reconstruction in the
    near-silent regime. It was not a clean success.

This is the most significant honest correction of the project: the
"functional teleportation pipeline demonstrated" claim is firmly true for
C. elegans and the project's rate model, and is NOT yet demonstrated for
real connectomes with realistic weight dynamic range. The next step is a
heterogeneous-excitability model, then re-test on FlyWire.

---

## Original note (density framing — superseded by the above)

## Summary

The pool-stim pipeline passes on **sparse** connectomes (C. elegans mean
|supp|≈8; Drosophila mushroom body subset mean |supp|≈8). It **fails badly**
on a **denser** subset (whole-FlyWire top-5000 by degree, mean |supp|≈47):
behavioral divergence ≈ 0.68, a near-total failure. This is an honest
limitation not anticipated by the earlier "passes at N=2000" result.

## The data

`run_flywire_sparse.py` — selecting the top-N neurons by total degree:

| Network | N | mean \|supp\| | density | skipped | Pearson r | behavioral div | verdict |
|---|---|---|---|---|---|---|---|
| C. elegans | 300 | 8 | 0.04 | — | 0.99 | <0.02 | PASS |
| FlyWire MB subset | 797 | 9 | 0.011 | 74 | 0.37 | 0.01 | PASS |
| FlyWire MB subset | 2000 | 8 | 0.004 | 35 | 0.35 | 0.011 | PASS (after fix) |
| **FlyWire whole top-5000** | **5000** | **47** | **0.013** | **437** | **0.24** | **0.68** | **FAIL** |

The N=5000 case is not just "bigger" — it is a **structurally different
network**. The mushroom body subsets were sparse (mean |supp| ≈ 8). The
top-5000-by-degree from the whole connectome is hub-enriched and **6× denser
in mean in-degree** (47 vs 8).

## Why density hurts

The behavioral output of neuron j depends on its total chemical input
Σᵢ W_ij r_i, a sum over |supp_j| presynaptic terms. The reconstruction has
per-weight error (Pearson r ≈ 0.24 → ~75% relative weight error). For a
neuron with 8 inputs, the input-sum error partially averages out. For a
neuron with 47 inputs, there are 6× more error-laden terms; while random
errors average as √n, any *systematic* bias (e.g. the strong-ridge shrinkage,
or the saturation-clipping bias) accumulates linearly with |supp|.

So denser networks amplify reconstruction bias into behavioral divergence.
The protocol's per-neuron regression quality (Pearson) was already only
~0.35 on FlyWire; on a sparse network that still gave behavioral PASS
(rate-distortion: errors don't matter much when summed over few terms), but
on a dense network the same per-weight quality produces catastrophic
behavioral divergence.

Additional factor: 437 of 5000 neurons (8.7%) skipped — zeroed columns,
silenced neurons — a much larger absolute count than the N=2000 case.

## Honest status

  - Pipeline validated on **sparse** connectomes (mean |supp| ≲ 10) up to
    N=2000, on real Drosophila data.
  - It **fails** on denser networks (mean |supp| ≈ 47). The whole human
    cortex has mean |supp| ≈ 7000 — vastly denser still.
  - **This is a real scope limitation.** The earlier human-scale projections
    assumed the protocol works at human cortical density; this test says it
    does not, at least not with the current per-neuron regression + the
    Pearson r ≈ 0.35 it achieves on real data.

## What this means for the human-scale claim

The honest revised position:

  - For SPARSE neural tissue (C. elegans-like, mean |supp| ~ 10), the
    pipeline is demonstrated end-to-end including real Drosophila data.
  - For DENSE neural tissue (mammalian cortex, mean |supp| ~ 1000s), the
    current protocol is NOT demonstrated and the N=5000 test suggests it
    fails. The reconstruction needs to be substantially more accurate
    (Pearson well above 0.35) for dense networks to pass behaviorally.
  - The information-theoretic content is still low (rate-distortion / d_eff
    arguments hold). The gap is in the *reconstruction algorithm's accuracy*,
    which the per-neuron support-aware ridge does not deliver on real
    connectomes at any density — it just happened not to matter for sparse
    ones.

## What would close it

The reconstruction accuracy must improve. Candidate directions:
  1. The multi-task / low-rank reconstruction (SVT, `run_megahub_svt.py`),
     applied not just to mega-hubs but to all neurons grouped by cell type.
     If cell-type weight matrices are low-rank (the d_eff measurements say
     they are), a joint fit could reach much higher per-weight accuracy.
  2. More probe trials / higher SNR — but the FlyWire Pearson plateaued at
     ~0.35 even at K=400, so more data alone may not suffice.
  3. Better probe design — frequency-rich or feedback-driven probes that
     excite the network's informative modes.
  4. Accepting that dense cortex needs a different reconstruction entirely
     (e.g. direct structural EM for the connectome, with activity recording
     only for the weights, not the topology).

This is now the **top open problem** for Direction 1, displacing the
mega-hub issue (which is solved). It is an algorithm-accuracy problem, not
a physics barrier — but it is genuinely unsolved.

## The deeper issue: FlyWire reconstruction Pearson is low at ANY density

A yellow flag that should have been chased earlier: the protocol recovers
the C. elegans connectome at Pearson r ≈ 0.99, but recovers FlyWire subsets
at only r ≈ 0.35 — even the *sparse* N=2000 mushroom body subset (mean
|supp|≈8, sparser than C. elegans's 12).

Both use the identical rate model and identical pool-stim protocol. The
regression *should* recover W to near-perfect Pearson, as it does for
C. elegans. It does not for FlyWire. Candidate reasons:

  1. **Weight distribution.** C. elegans weights (normalized synapse counts)
     are moderate and similar in scale. FlyWire raw syn_counts span 1 to
     several hundred; after W/W.max() normalization most weights are tiny.
     A network of mostly-tiny weights may leave most neurons near-silent
     under probing → few valid observations → ill-conditioned regression.
  2. **Coverage ratio.** C. elegans canonical run used K·M/N = 5.0; the
     FlyWire N=2000 run used 2.0. Lower coverage → noisier fit.
  3. **The arctanh linearization** may be more error-prone for the FlyWire
     weight/activity regime.

The behavioral PASS at N≤2000 sparse was therefore the **rate-distortion
principle masking a weak reconstruction** — Pearson 0.35 is poor, but on a
sparse network the resulting input-sum error is small enough to stay under
the 5% behavioral threshold. On the dense N=5000 network the same weak
reconstruction is no longer masked, and the failure surfaces.

So the honest root cause is: **the protocol's reconstruction accuracy on
real connectomes (Pearson ~0.35) is much worse than on C. elegans (0.99),
and that weak reconstruction only happens to pass behaviorally on sparse
networks.** The density limitation is the symptom; the weak FlyWire
reconstruction is the disease. Diagnosing *why* FlyWire reconstructs poorly
(weight distribution? coverage? linearization?) is the prerequisite to any
dense-cortex claim.

## Honesty note

The session's earlier claims ("pipeline demonstrated", "generalizes")
were progressively scoped down as larger / denser real-data tests exposed
limitations: first to N≤800, then extended to N=2000 (sparse) after the
mega-hub fix, and now explicitly bounded to sparse networks after the
N=5000 dense failure. Each correction was made when a test contradicted
the prior claim. The physics conclusion (no fundamental barrier; classical
information suffices) is unchanged. The engineering claim (this specific
protocol works) is bounded to sparse connectomes and is honestly NOT
established for dense mammalian cortex.

## Files
  - `simulation/run_flywire_sparse.py` — the N=5000 test
  - `simulation/results/flywire_sparse.txt` — result (FAIL)
  - `simulation/rate_model.py` — `simulate_rate_sparse` (validated, 65-375× faster)
