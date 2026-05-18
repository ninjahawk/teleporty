# Direction 1 — Heterogeneous-Excitability Rate Model (design note)

**Status:** Design only — not implemented. This note specifies the model
upgrade needed to extend the scan-inverse protocol from C. elegans to real
mammalian-scale connectomes.

## Why this is needed

`direction1_density_limitation.md` established that the project's uniform
rate model fails on FlyWire because real synapse weights span 3.4 orders of
magnitude (syn_count 1–2405). With one global gain/threshold/time-constant,
no weight normalization keeps both weak and strong synapses in the tanh's
responsive band: /max → near-silent, /p99 → saturated.

Real neurons solve this with **homeostatic regulation**: each neuron tunes
its intrinsic excitability so that, given its typical synaptic drive, it
operates around the middle of its input-output curve. A neuron receiving
1703 strong inputs is not saturated in a real brain — it has a higher
threshold / lower gain to compensate.

The model must replicate this.

## Current model

```
tau dr_i/dt = -r_i + tanh( gain * ( Σ_j W_ij r_j + I_gap_i + I_ext_i + bias ) )
```

Single scalar `gain`, single scalar `bias`, single `tau` for all i.

## Proposed heterogeneous model

```
tau_i dr_i/dt = -r_i + tanh( gain_i * ( Σ_j W_ij r_j + I_gap_i + I_ext_i − theta_i ) )
```

Per-neuron parameters `gain_i`, `theta_i` (threshold), optionally `tau_i`.

### Setting the per-neuron parameters (homeostatic calibration)

The parameters are not free — they are fixed by a homeostatic principle:
**each neuron should sit near the middle of its responsive range at its
baseline operating point.**

Procedure:
1. Run the network at rest (no external input) or under a reference
   stimulus ensemble. Record each neuron's mean total synaptic drive
   `h_i^bar = ⟨ Σ_j W_ij r_j + I_gap_i ⟩`.
2. Set `theta_i = h_i^bar` — the threshold equals the typical drive, so the
   neuron's *deviations* from baseline (which carry the signal) are centered
   on the tanh's steep, responsive region.
3. Set `gain_i` so the neuron's drive *fluctuations* `σ(h_i)` map onto the
   responsive band: `gain_i = c / σ(h_i)` for a constant c ≈ 1–2. A neuron
   with large drive variance gets low gain; one with small variance gets
   high gain. Both end up equally responsive.

This is a fixed-point calibration (parameters depend on activity, activity
depends on parameters) — solve by iteration: calibrate, simulate, recalibrate,
~3–5 rounds to convergence. This mirrors real homeostatic plasticity, which
also operates as a slow feedback loop.

### Effect on the scan-inverse protocol

The scan-inverse regression currently inverts:
```
z_j = arctanh(r_j)/gain − I_gap_j − I_ext_j = Σ_i W_ij r_i
```

With per-neuron parameters this becomes:
```
z_j = arctanh(r_j)/gain_j + theta_j − I_gap_j − I_ext_j = Σ_i W_ij r_i
```

`gain_j` and `theta_j` are known to the scanner (they are intrinsic
properties measured during the structural/physiological scan, alongside the
connectome topology). So the regression is unchanged in form — just uses
per-neuron constants. The pool-stim protocol, coverage rule, mixed-amplitude
ladder, and strong-ridge fallback all carry over directly.

The key benefit: with homeostatic calibration, **every neuron is observable**
— none are stuck silent or saturated regardless of how many inputs they have
or how their weights are distributed. The saturation/skipping failure modes
(`megahub_limitation.md`) and the weight-dynamic-range failure
(`density_limitation.md`) both disappear, because excitability now adapts to
drive.

## Validation plan

1. **Implement** `simulate_rate_hetero` in `rate_model.py` with per-neuron
   `gain_i`, `theta_i`, plus a `calibrate_homeostatic(W, G)` routine.
2. **C. elegans regression test:** the heterogeneous model must still recover
   the C. elegans connectome at Pearson ≈ 0.99. (With C. elegans's narrow
   weight distribution the per-neuron parameters will all be similar, so this
   should reduce to the current result. If it does not, the calibration is
   wrong.)
3. **FlyWire test:** re-run `run_flywire_sparse.py` with the heterogeneous
   model. Prediction: skipped-neuron count drops near zero (all neurons
   observable), Pearson rises well above 0.35, behavioral divergence passes
   at N=2000 and N=5000.
4. **If FlyWire passes:** the real-connectome capability is established and
   the human-scale projections can be trusted. If not, the next layer
   (heterogeneous `tau_i`, or a spiking model) is needed.

## What this does and does not change

Does not change:
  - The classical-information reframing (Direction 1 core thesis)
  - The rate-distortion / d_eff / 42 KB brain budget
  - The body information budget (~247 GB)
  - The fabricator analysis
  - The quantum-direction closures (2,3,4,5)
  - The scan-inverse *protocol* (pool stim, coverage, amplitudes)

Changes:
  - The dynamical model the protocol runs on, so it can be fairly tested on
    real connectomes.

## Honest framing

This is the gap between "demonstrated for C. elegans" and "demonstrated for
real brains." It is a modeling problem with a clear, standard solution
(homeostatic excitability is textbook neuroscience — Turrigiano 2008). It is
not a physics barrier and not a fundamental obstacle. But it is real
unfinished work, and until it is done the project's real-connectome and
human-scale claims rest on an extrapolation from a single small organism
whose weight statistics are unrepresentative.

## First implementation attempt — FAILED (calibration bug)

`simulate_rate_hetero` and `calibrate_homeostatic` were implemented in
`rate_model.py` and validated on C. elegans (`run_hetero_validation.py`).
**The validation failed**, with a clear, diagnosed cause:

  Calibration output: gain_i mean = 92.6, range [4.4, **1500**]
  Result: 170/300 skipped, Pearson 0.19, behavioral div 1.0 — total failure.

The bug is in the calibration formula `gain_i = c / std(drive_i)`. Neurons
that are barely driven in the reference ensemble have `std(drive) ≈ 0`, so
their gain explodes to ~1500. A gain of 1500 makes tanh a step function —
the neuron saturates on any infinitesimal input deviation, destroying the
dynamics.

### Calibration iterations tried (all on C. elegans, must reach Pearson > 0.9)

| # | Calibration | gain range | skipped | Pearson | behavioral |
|---|---|---|---|---|---|
| 1 | gain = c/std (naive) | [4, 1500] | 170/300 | 0.19 | FAIL |
| 2 | gain capped [0.5,10], θ = mean drive | [4.4, 8.7] | 163/300 | **0.60** | tap PASS, chem FAIL |
| 3 | #2 + θ = mean − arctanh(0.3)/gain | [4.4, 8.7] | 80/300 | 0.27 | FAIL |

Iteration 2 is the current best (code is left in this state). None reaches
the Pearson > 0.9 bar.

**Diagnosis of why this is hard:** the calibration is a coupled problem.
- The gain cap (iter 1→2) fixed the divergence — clearly correct, Pearson
  0.19 → 0.60.
- The θ adjustment (iter 2→3) reduced unobservable neurons (163 → 80) but
  *worsened* reconstruction (0.60 → 0.27). Lowering θ keeps neurons
  observable but changes the dynamics in a way that hurts the regression.
- gain, θ, the resulting dynamics, and observability all interact. Quick
  one-variable patches each fix one symptom and break another.

**This needs a proper coupled treatment, not more one-line patches:**
  1. The reference ensemble must drive every neuron into a good range
     (the 20-random-pool ensemble leaves low-degree neurons silent — they
     dominate the skipped count regardless of θ).
  2. gain and θ should be jointly optimized so each neuron's *response*
     (not its drive) has good dynamic range AND stays observable — this is
     a 2-parameter-per-neuron fit, plausibly solved by matching each
     neuron's response distribution to a target (e.g. mean 0.3, std 0.15).
  3. Validate against C. elegans Pearson 0.99 at every step.

The conceptual model is sound; the calibration is a genuine sub-problem
that needs careful, fresh work — three deep-context patches did not crack
it. Honest status: **heterogeneous model implemented, calibration OPEN.**

**Next session: solve the calibration as a coupled 2-parameter-per-neuron
response-matching problem, validate on C. elegans, then test FlyWire.**

## Original validation plan
