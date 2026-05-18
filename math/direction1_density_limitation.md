# Direction 1 — Density Limitation (open, honest negative result)

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
