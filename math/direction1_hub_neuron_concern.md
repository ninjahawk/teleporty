# Direction 1 — Hub-Neuron Scaling Concern (open caveat)

## Issue

The pool-stim protocol assumes K_pools > |supp_j| for every neuron j —
otherwise the support-aware ridge regression is under-determined for that
neuron. The deployment projection uses K_pools = 8 · mean|supp_j|.

But |supp_j| is **not uniform**. Some neurons receive vastly more inputs
than the mean:

| Region | Mean |supp_j| | Max |supp_j| | Ratio |
|---|---|---|---|
| C. elegans          | 12    | 50      | 4× |
| Cortical pyramidal (mammals) | 7000  | 20000   | 3× |
| Cerebellar granule cells (receivers from mossy fibers) | 4 | ~10 | — |
| Cerebellar Purkinje cells | ~150000 | ~200000 | — |
| Striatal medium spiny neurons | 5000  | 30000   | 6× |

**Cerebellar Purkinje cells have |supp_j| up to ~200000 inputs.**

If K_pools = 8 × 7000 = 56000 (set by cortical mean), Purkinje recovery
needs K > 200000. The pool protocol is under-determined for Purkinje cells
by 3.5×.

## Why this might or might not matter

**Argument it matters:**

Purkinje cells are the sole output of the cerebellar cortex. Their weights
determine motor learning, balance, fine coordination. If we can't
reconstruct them, the teleported person has cerebellar deficits.

**Argument it does NOT matter:**

Purkinje cells receive ~200k inputs from parallel fibers, but the function
is dominated by the few hundred CLIMBING-fiber inputs and the population
average of parallel-fiber inputs. The information needed is the
distribution and gross weighting, not the individual per-fiber weight.

In rate-distortion terms: parallel-fiber weights are highly redundant
(each granule cell carries ~bit/sec of information; 200k of them is gross
over-sampling). The functional spec is the linear-projection coefficients
in a ~few-hundred-dimensional space, not the 200k individual weights.

This is the **same brain rate-distortion argument** from
`math/direction1_rate_distortion.md` applied locally: d_eff for the
Purkinje cell's input matrix is ~few hundred, not 200k.

If true, we don't need K > |supp_j|; we need K > d_eff_j.

## What's needed to close this

Empirical: compute the d_eff (participation ratio) of the weight VECTOR
for each cell type in a representative connectome.

  Predicted: d_eff_Purkinje ≈ 100-500 (much smaller than 200k).
  If confirmed: K_pools = 8 × max(d_eff over cell types) ≈ 8 × 500 = 4000
                — far smaller than the worst-case K = 8 × max(|supp|).

  If d_eff_Purkinje ≈ 50000 (high): protocol scales poorly for cerebellum.

This is the single most important open empirical question for human-scale
scaling. It cannot be resolved from C. elegans data alone — C. elegans
doesn't have anything like a Purkinje cell.

## How to attack it

1. **Use MICrONS mouse cortex data.** Compute per-cell-type d_eff for the
   weight VECTORS (each row of W is the inputs to one neuron). If all cell
   types have d_eff < a few hundred even when |supp| is in thousands,
   the protocol scales. This is a reanalysis of existing data; doable
   in days.

2. **Test pool stim on a hub neuron synthetic model.** Build a network
   with one Purkinje-like cell receiving 1000+ inputs and verify that
   pool stim recovers behavior even with K < |supp|. If yes, the d_eff
   argument is confirmed. If no, hubs require a different strategy.

3. **Use sparse priors (L1) for hub neurons** if d_eff turns out to be
   high. Group-LASSO over functional input clusters could exploit the
   redundancy among parallel-fiber inputs.

## Verdict

This is a **conditional caveat**, not a confirmed failure. The pool
protocol is demonstrated robustly at C. elegans scale (no hubs of the
problematic type exist). At human scale, the protocol succeeds if
d_eff(cell-type) << |supp|(cell-type) for all cell types.

The rate-distortion analysis predicts this is true (the brain operates
in a low-dimensional functional space relative to its raw connectivity),
but empirical confirmation on mammalian data is the next step before any
human-scale deployment.

If d_eff is in fact small for hub neurons: the protocol scales as
already projected (~2 × 10⁶ trials for human).

If d_eff is large for hub neurons: the protocol scales as 8 × max(d_eff)
which could be 10× larger trials count for some cell types, but probably
not the fundamental obstacle.

Worst case: 10× more trials for the high-d_eff cell types, bringing the
human-scale projection from 2 × 10⁶ to 2 × 10⁷ trials. At 100× scanner
parallelism, that's 1 week instead of 1 day. Still tractable.

**Not a project-blocker. A scaling refinement.**
