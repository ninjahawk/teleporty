# Direction 1 — Mega-Hub Limitation (open, honest negative result)

## Summary

The pool-stim pipeline **passes** at C. elegans (N=300) and a small Drosophila
mushroom body subset (N=797). It **fails** at a larger Drosophila mushroom
body subset (N=2000) — and the failure is NOT a coverage problem. This is an
honest limitation that the overnight "generalizes to arbitrary networks"
claim did not anticipate.

## The data

`run_flywire_pool_subset.py` on FlyWire MB_CA_R neuropil, subsampling the
top-N neurons by total degree:

| N | max \|supp\| | K_pools | K·M/N | skipped | Pearson r | behavioral div | verdict |
|---|---|---|---|---|---|---|---|
| 797  | 686  | 75  | 1.41 | 74 | 0.37 | 0.003–0.015 | **PASS** |
| 2000 | 1703 | 75  | 0.56 | 160 | 0.30 | 0.13 | FAIL |
| 2000 | 1703 | 134 | 1.00 | 117 | 0.36 | 0.13 | FAIL |
| 2000 | 1703 | 400 | 3.00 | 81  | 0.39 | 0.13 | FAIL |

**Behavioral divergence is flat at 0.13 across a 5× change in K_pools.**
Coverage (the K·M/N ratio) is not the controlling variable here. Increasing
K from 75 to 400 cut the skipped-neuron count (160 → 81) and nudged Pearson
(0.30 → 0.39), but did nothing to the behavioral divergence. The failure is
structural.

## Why the subsets differ

The test subsamples the **top-N neurons by degree**. This is hub-enriched
by construction:

  N=797  subset: max \|supp\| = 686
  N=2000 subset: max \|supp\| = 1703

The larger subset includes mega-hubs with \|supp\| in the thousands. The
per-neuron support-aware regression — even with the strong-ridge fallback
(λ=0.5) — cannot reconstruct a weight vector of length 1703 from K=400 pool
observations. The strong ridge produces a heavily shrunk, biased estimate;
16-30 such mega-hubs collectively bias the whole network's gain, producing
the systematic ~0.13 divergence.

## What this means for the hub-neuron concern

The hub-neuron concern (`direction1_hub_neuron_concern.md`) is **NOT fully
resolved**. The findings there still stand:
  - d_eff of hub input vectors is small (FlyWire: 25-58; C. elegans: 3.7)
  - This means the *information* needed to specify hub weights is small

But exploiting that low d_eff requires a **working multi-task reconstruction**
that fits all hubs of a type jointly. The implementations tested
(`run_multitask_pool_stim.py` ALS, `run_multitask_v2.py` SVD-shrinkage) were
marginal — they did not beat independent fits. The strong-ridge fallback
helps for moderate hubs (|supp| ≤ ~700, as at N=797) but not for mega-hubs
(|supp| > 1000).

**Honest status:** the pipeline is demonstrated at N ≤ 800 with realistic
hub structure. It is NOT demonstrated at N = 2000 with mega-hubs. The gap is
a real reconstruction-algorithm problem, not a physics barrier — but it is
unsolved in this repo.

## What would close it

A genuine multi-task / low-rank reconstruction:
  - Group neurons by cell type (FlyWire has type annotations; not used here)
  - For each type, jointly fit all members' weight vectors as B·C where B is
    an N×r basis and C is r×n_type coefficients, r ≈ d_eff(type)
  - Solve with a proper trace-norm-penalized objective (not ad-hoc ALS),
    e.g. via the singular value thresholding algorithm of Cai-Candès-Shen 2010
  - This needs r·n_type observations, not |supp|·n_type — for mega-hubs that
    is the difference between feasible and infeasible

This is standard low-rank matrix recovery. It is well-posed (the d_eff
measurements prove the low-rank structure exists). It was not implemented
to a working standard in this session. **It is the top open problem.**

## Honest revision to project claims

Previously claimed (overnight + morning):
  "End-to-end pipeline demonstrated; generalizes to arbitrary networks
   (5/5 synthetic PASS, real C. elegans + Drosophila subset PASS)."

Corrected:
  "End-to-end pipeline demonstrated at N ≤ 800 including a real Drosophila
   mushroom body subset. Synthetic networks up to N=1000 pass. Real
   hub-enriched subsets at N=2000 FAIL — mega-hubs (|supp| > 1000) are not
   reconstructed by the current per-neuron protocol. A working multi-task
   low-rank reconstruction is required and remains unimplemented."

The physics conclusion is unchanged (no fundamental barrier; the information
is present, the low-rank structure is measured). But the *engineering* claim
that the protocol "works" must be scoped to N ≤ 800 / moderate hubs until
the multi-task reconstruction is built and tested.

## Files
  - `simulation/run_flywire_pool_subset.py` — the test that exposed this
  - `simulation/results/flywire_pool_subset.txt` — latest (N=2000 FAIL)
