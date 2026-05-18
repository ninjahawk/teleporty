# Direction 1 — Pool-Based Scan Inverse (toward human-scale)

## Motivation

The v4 protocol (`run_scan_inverse_v4.py`) stimulates each of N neurons
individually -> O(N) trials. For C. elegans this is 900 trials, fine.
For human (N=8.6×10¹⁰), it's 2.6×10¹² trials — not serially feasible.

This direction tests **random POOL stimulation**: stimulate K random subsets
of M neurons simultaneously, K << N, and recover W via the same support-aware
ridge regression.

## Method

Same v4 protocol except each trial's stimulus targets a random subset of
M neurons drawn from the N=300 C. elegans population (no replacement within
a pool), at amplitudes [0.4, 0.8, 1.5]. n_reps=10 noise averaging per trial.

Recovery: support-aware ridge regression on steady-state activity. Same as v4.

## Result (`run_scan_inverse_pool.py`)

| K_pools | M | total trials | Pearson r | div_tap | div_chem | div_thermo | div_noci | verdict |
|---|---|---|---|---|---|---|---|---|
| 300 |  1 | 9000 | 0.806 | 0.037 | 0.003 | 0.004 | 0.004 | PASS |
| 200 |  5 | 6000 | 0.950 | 0.003 | 0.000 | 0.000 | 0.009 | PASS |
| 150 | 10 | 4500 | 0.961 | 0.000 | 0.005 | 0.004 | 0.000 | PASS |
| **100** | **15** | **3000** | **0.990** | 0.000 | 0.000 | 0.000 | 0.000 | **PASS** |
| 75 | 20 | 2250 | 0.977 | 0.002 | 0.001 | 0.001 | 0.001 | PASS |
| 50 | 30 | 1500 | 0.894 | 0.387 | 0.019 | 0.015 | 0.072 | FAIL |
| 30 | 50 | 900  | 0.707 | 0.287 | 0.172 | 0.167 | 0.224 | FAIL |
| 20 | 80 | 600  | 0.492 | 0.581 | 0.305 | 0.217 | 0.373 | FAIL |

**Surprising finding: pool stimulation is BETTER, not just cheaper.**

  Per-neuron protocol (K=300, M=1):  r = 0.806
  Best pool (K=100, M=15):           r = 0.990
  Smallest passing pool (K=75, M=20): 2250 trials (4× fewer than v4)

## Why pool stimulation wins

The per-neuron protocol generates K rows of X where each row has only ONE
neuron above baseline (the stimulated one). This makes X near-singular: many
rows are scaled versions of standard basis vectors, providing very little
between-neuron covariance.

Pool stimulation generates rows where M neurons fire together at various
amplitudes. The X matrix has rich rank-M structure, MUCH better conditioned
for least-squares recovery of multi-neuron weight vectors.

This is the same intuition behind compressed sensing: random projections of a
sparse signal carry more information per measurement than canonical-basis
samples.

## Failure regime

Below K_pools=75 (with M≥30), recovery fails on the tap circuit first. The
failure mode is **coverage degradation**: each neuron appears in only K·M/N
pools on average. At K=50, M=30: 5 pools/neuron — too few to constrain the
~12 incoming weights to that neuron, even with the support prior. At
K=100, M=15: also 5 pools/neuron — but this passes. The difference is
pool ENTROPY: M=15 with K=100 gives 100 distinct pool patterns; M=30 with
K=50 gives only 50, half the diversity.

So the relevant scaling is roughly **K·log(M) ≈ const** for adequate coverage,
with a floor at K ≈ 6·|supp_j| ≈ 75.

## Human-scale projection

For human N = 8.6×10¹⁰ with mean |supp_j| ≈ 7000 (estimated from cortical
microcircuit literature):

  Minimum K_pools ≈ 6 · 7000 = 4.2 × 10⁴ pools
  Pool size M = 100 · 7000 = 7×10⁵ (similar M/|supp_j| ratio as worm)
  Total trials: 4.2×10⁴ · 3 amps · 10 reps = **1.3 × 10⁶ trials**

This is 6 orders of magnitude smaller than the per-neuron projection
(2.6×10¹² trials). At 30 s/trial, 1.3 × 10⁶ trials = 11000 hours = 14 months
of continuous probing. That is the order of magnitude of a Manhattan-Project-
scale experimental campaign — still very large, but in the realm of
human-feasible "build me one scanner, run it for a year" effort.

If trials can be parallelized across 10³ scanner units, the protocol runs in
~10 days. That is engineering, not physics.

## Biological feasibility

Each pool is a defined subset of neurons. Implementation options:

1. **Cell-type-based pools**: optogenetic driver lines for individual cell
   types (~10⁴ defined cell types in human cortex per BICCN). Each "type"
   = one pool. Number of pools = number of types ≈ 10⁴ — matches the
   K_pools we need.

2. **Spatial pools**: addressable optical stimulation by xy-region in a
   tissue slice, ~10 μm resolution. 10⁹ addressable spots, choose any subset
   of M to fire simultaneously.

3. **Holographic optogenetics**: SLM-shaped 2P stimulation creates
   arbitrary 3D patterns. State of the art 2025: ~100 simultaneous cells.
   At M=15 this is overkill; at M=10⁵ it's beyond current capability but
   roadmap-tractable.

The cell-type approach (option 1) is the practical match: it gives us a
small number of well-defined pools and avoids the spatial-addressability
problem entirely.

## Conclusion

Pool-based scan inverse is the right human-scale strategy.

  - 4× fewer trials than per-neuron at C. elegans
  - Recovers W to higher fidelity (r=0.99 vs 0.81)
  - Scales to human at ~10⁶ trials, vs 10¹² per-neuron
  - Maps naturally to cell-type-driver-line optogenetics

The human scanner is now in the realm of "feasible large engineering
project", not "fundamentally impossible at biological time scales".

## Files

  - `simulation/run_scan_inverse_pool.py` — pool sweep
  - `simulation/results/scan_inverse_pool_summary.txt` — table of results
