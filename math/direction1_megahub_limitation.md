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

  N=797  subset: max \|supp\| = 686,  74 skipped (vj.sum() < 5)
  N=2000 subset: max \|supp\| = 1703, 81 skipped at K=400

## Cause not yet definitively isolated (honest status)

The first draft of this note attributed the failure to mega-hubs (|supp| in
the thousands defeating the per-neuron regression). **A direct synthetic test
of that hypothesis did NOT reproduce the failure** (`run_megahub_svt.py`):

  Synthetic N=600, 20 mega-hubs |supp|=250, K=80 (K ≪ |supp|):
    per-neuron strong-ridge: behavioral div = 0.016, **PASS**
    SVT multi-task:          behavioral div = 0.016, PASS

When there is no skipping, per-neuron strong-ridge handles K ≪ |supp| fine.
So "mega-hubs alone" is NOT the confirmed cause.

The more likely culprit is the **81 skipped neurons** at N=2000. A skipped
neuron (vj.sum() < 5 — fewer than 5 valid observations) gets W_hat column = 0,
i.e. it is reconstructed as receiving zero chemical input. 81 silenced
neurons in a 2000-network, if any sit on the test-stimulus propagation
paths, would produce a systematic behavioral divergence. This is consistent
with the flat div ≈ 0.13 across all K (the skipped count only dropped from
160 → 81 as K went 75 → 400; it never reached zero).

**Why do neurons get skipped even at K·M/N = 3?** A neuron is skipped when,
even after being in several pools, it produces < 5 valid timesteps. Valid
requires: postsynaptic rate above EPS, the arctanh target in range, and the
source state not saturated. Neurons that are intrinsically near-silent or
near-saturated under the probe protocol never yield valid rows. These are a
*observability* failure, not a coverage or hub failure.

## Diagnostic result — cause isolated (`run_flywire_pool_subset.py`)

The diagnostic was run (N=2000, K=134). For each candidate cause, substitute
W_TRUE for those columns and re-test behavior:

| Substitution | # columns | div_mean | result |
|---|---|---|---|
| Baseline (nothing) | 0 | 0.14 | FAIL |
| W_TRUE for skipped neurons | 146 | **0.042** | near-PASS |
| W_TRUE for mega-hubs (\|supp\|>500) | **2** | **0.042** | near-PASS |
| W_TRUE for skipped + mega-hubs | 146 | 0.042 | near-PASS |

**Decisive finding:** substituting just **2 mega-hub columns** gives the
*identical* improvement (0.14 → 0.042) as substituting all 146 skipped
columns. The two fixes are redundant — which means **the 2 mega-hubs are
themselves among the 146 skipped neurons**, and they alone account for
~0.10 of the 0.14 divergence.

**The mega-hubs ARE the dominant cause** — confirming the original
hypothesis — but via a mechanism the synthetic test missed:

  The 2 mega-hubs (|supp| up to 1703) are **unobservable** under the probe
  protocol. A neuron receiving 1703 inputs is driven into **saturation**
  (rate pinned near 1.0) whenever its many presynaptic neurons are
  co-activated by the pools. Saturated samples fail the validity filter
  (X > SAT_HI), so the mega-hub accumulates < 5 valid observations and is
  *skipped* — its W_hat column is left at zero. A zeroed mega-hub column
  means that hub receives no chemical input in the reconstruction; since
  mega-hubs are high-influence integrators, silencing 2 of them distorts
  the whole network's behavior by ~0.10.

The synthetic mega-hub test (`run_megahub_svt.py`) did NOT reproduce this
because the synthetic hubs were never saturated/skipped — the failure is
an **observability** failure, not a regression under-determination failure.

## The residual 0.042

Even with mega-hubs fixed, div_mean = 0.042 — borderline (some test stimuli
still > 0.05). This residual is general bulk-reconstruction error: at N=2000,
K=134, the overall Pearson r is only 0.29 (vs 0.99 on C. elegans). The bulk
network needs more pool trials (higher K) and/or more reps. This is the
ordinary coverage/SNR axis — solvable by more data, unlike the mega-hub
observability problem which needs a protocol change.

## The fix

Mega-hubs must be kept **out of saturation** during probing so they yield
valid observations:

  1. **Lower-amplitude probes** for pools containing many of a mega-hub's
     presynaptic neurons — keep the hub's rate in [0.05, 0.85].
  2. **Sparse targeted probes** that activate only a fraction of a mega-hub's
     inputs at once, so the hub stays in its linear regime.
  3. **Adaptive amplitude:** detect saturation in real time and back off.

None of these is hard. They are probe-design refinements. The mega-hub
problem is an **observability/protocol** issue, fully within engineering
scope — not a fundamental reconstruction-algorithm gap as the first draft
of this note feared.

## Two observability failure modes (`run_saturation_analysis.py`)

A controlled synthetic sweep (neurons spanning in-degree 5–400, probe
amplitude 0.05–3.0) shows observability is non-monotonic in amplitude and
depends strongly on in-degree:

| In-degree | Best amplitude | Max observable fraction |
|---|---|---|
| ~8   | 3.0 (highest) | 20% |
| ~30  | 1.5 | 56% |
| ~100 | 0.4 | 100% |
| ~300 | 0.1 (lowest) | 100% |

Two distinct failure modes:

1. **High in-degree → saturation.** A neuron with 300 inputs integrates so
   much drive that it pins at rate ≈ 1.0 unless the amplitude is very low
   (0.1). This is the mega-hub failure. Fix: low-amplitude probes.

2. **Low in-degree → under-drive.** A neuron with 8 inputs is observable only
   20% of the time even at the highest amplitude. Its few presynaptic
   neurons rarely land in a random pool of M=15, so it is seldom driven
   above the EPS floor. This is NOT a saturation problem — it's the
   *input-coverage* problem: a neuron is observable only when its SUPPORT
   SET is sampled, which is harder than the neuron itself being in a pool.

The diagnostic reconciles with this: of the 146 skipped neurons at N=2000,
~2 are saturated mega-hubs (high influence — fixing them recovers 0.10 of
divergence) and ~144 are under-driven low-degree neurons (low influence —
fixing all of them adds nothing beyond the 2 hubs). The behavioral fix is
the mega-hubs; the low-degree skips are behaviorally negligible but they
DO drag down the bulk Pearson (0.24–0.29 on FlyWire).

**Refined coverage rule:** the earlier K·M ≥ 3N rule ensures each *neuron*
lands in pools. The stronger requirement is that each neuron's *support set*
is collectively sampled. For low-degree neurons this needs either larger M
(more inputs covered per pool) or targeted probes that hit a chosen
neuron's specific inputs. The mixed-amplitude ladder addresses the
saturation mode; the input-coverage mode needs larger M or targeted probes.

## FIX VERIFIED — N=2000 now PASSES

The combined fix was implemented and tested:
  - **Mixed amplitude ladder** [0.05, 0.15, 0.4, 0.8, 1.5] — the low end
    (0.05–0.15) keeps mega-hubs out of saturation and observable; the high
    end (0.8–1.5) gives small-weight circuits adequate SNR.
  - **2× coverage** (K_pools = 267, K·M/N = 2.0) — addresses the
    input-coverage / bulk-SNR axis for low-degree neurons.

Result on the N=2000 FlyWire mushroom body subset:

| Config | skipped | Pearson r | behavioral div | verdict |
|---|---|---|---|---|
| default amps, K=75 | 160 | 0.30 | 0.13 | FAIL |
| default amps, K=400 | 81 | 0.39 | 0.13 | FAIL |
| low amps, K=134 | 85 | 0.24 | 0.040 | 3/5 PASS |
| **mixed amps, K=267** | **35** | **0.35** | **0.011** | **PASS (5/5)** |

All five behavioral tests pass at div 0.010–0.013 — a 12× reduction from
the 0.13 baseline. Skipped neurons fell 146 → 35.

**The pipeline is now demonstrated at N=2000 on real Drosophila biological
data with full hub structure (max |supp|=1703).** The validated range
extends from N≤800 to N=2000.

Note Pearson r is still only 0.35 — the structural weight recovery is
moderate — yet behavioral divergence is 0.011. This is, once again, the
rate-distortion principle: behavioral equivalence (the criterion that
matters) is achieved well before bit-exact weight recovery.

## Status (resolved)

  - Pipeline demonstrated at N=2000 on real Drosophila data. PASS.
  - The N=2000 failure was an observability problem (mega-hub saturation +
    low-degree input under-coverage), fully characterized and fixed by a
    protocol change (mixed-amplitude ladder + adequate coverage).
  - No physics barrier, no fundamental algorithm gap. The SVT multi-task
    solver built earlier was aimed at the wrong failure mode (under-
    determination) and turned out unnecessary — the real issue was
    observability, fixed by probe design.
  - Remaining: validate at the next scale (N=10⁴–10⁵, e.g. a full
    Drosophila neuropil or mouse cortex column). The protocol rules are
    now known: K·M ≥ 3N coverage, mixed-amplitude ladder, strong-ridge
    fallback for any residual under-determined neurons.

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
