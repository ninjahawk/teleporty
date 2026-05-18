# Teleporty — Teleportation Research Project

## STRICT RULE — COMMITS AND CONTRIBUTORS
**NEVER EVER include Claude as a co-author, contributor, or co-committer in any commit, PR, or anywhere on this repo. Do NOT add `Co-Authored-By: Claude` or any similar line to commit messages. Commits are authored by the human only.**

## Project Goal
Find a mechanism, reframing, or approach to teleportation that is physically grounded, has not been seriously pursued, and produces a simulation with testable predictions. The goal is discovery, not literature review.

The working definition of teleportation: **scan → transmit → reconstruct → verify**. The reconstructed object is functionally identical to the original. Atom identity doesn't matter. Continuity of the original doesn't matter. Behavioral/functional equivalence is the criterion.

**Honesty rule:** This is math and science. Do not produce results to make the user feel good. If something is impossible, say so with the math that shows why. If something is possible, show the derivation. No rounding off, no handwaving, no softening conclusions.

## What We've Established Is Dead (and Why)
- **Full quantum state teleportation of matter**: decoherence (~10⁻²³ s for macroscopic objects at room temp), Heisenberg measurement problem, and 10²⁸-bit bandwidth requirement hit simultaneously. Not an engineering problem — a fundamental one.
- **Traversable wormholes**: Ford-Roman quantum inequalities bound negative energy density too tightly. The Casimir effect is ~38 orders of magnitude too weak for a 1 m throat. Not a materials problem.
- **Warp drive (Alcubierre)**: same exotic matter wall. White's 2012 geometry still requires Jupiter-mass negative energy and is causally disconnected from the interior.
- **Psychic teleportation**: pseudoscience. Not considered further.

## The Viable Path
**Functional teleportation via classical information.** The quantum barriers apply to copying every quantum state of every particle. Functional identity is encoded in classical information: connectome structure, cell types, molecular composition, spatial arrangement. None of the quantum barriers apply at the classical level.

The only physically honest mechanism for teleportation is: **disassemble (or scan) → encode → transmit → fabricate**. No spacetime bending. No exotic matter. Just a file and a sufficiently advanced printer.

## Active Research Directions

### Direction 1: Functional Teleportation — Complete Pipeline (PRIMARY)

**Status: In progress. Neural scanner confirmed. Apple pipeline quantified. Fabricator is the bottleneck.**

**What has been established (neural scanner):**

Three connectomes processed, d_eff extracted via weight-matrix PCA (participation ratio):

| Organism | N neurons | d_eff | Source |
|----------|-----------|-------|--------|
| C. elegans | 302 | 28 | Cook et al. 2019 (wormwiring.org) |
| Mouse V1 | 50,943 | 146 | MICrONS mm3 portion 65 (Zenodo 16744240) |
| Drosophila | 138,639 | ~700 | FlyWire 783 (Zenodo 10676866) |

Scaling law fit (three-point, log-log): **d_eff = 1.85 × N^0.459**

Human extrapolation (N = 86×10⁹): **d_eff ≈ 2×10⁵**

Minimum bits for functional reconstruction (D=30% distortion): **R ≈ 42 KB** (revised from original 10¹²–10¹³ bits — 7–8 orders of magnitude compression)

The 30% distortion tolerance is empirically confirmed in C. elegans simulation (behavioral divergence <2% at D=0.30).

**Generative model — CONFIRMED (Prediction 3):**

Activity recordings can reconstruct synaptic weights well enough to reproduce behavior. Final result: **K = 1 dedicated probe condition per behavior class** suffices.

- div_tap = 0.5% at K=1 (tap-targeted pulsed condition) ✓
- div_chem = 0.5% at K=2 (chem-targeted pulsed condition) ✓

Training protocol: pulsed stimuli targeting relevant sensory neurons at moderate amplitude (avoids saturation, captures linear-regime transients). Not random stimulation.

Key finding: tap sensor chemical weights are 27× smaller than global mean → joint regression over all behaviors fails (large-signal circuits wash out small-signal ones). Modular approach (fit per behavior class, combine per-neuron by best-activating condition) resolves this.

**Revised scanner prediction:**
- K = N_behavior_classes (order 100–1000 for humans), not K ~ d_eff = 10⁵
- Structured probe stimuli per behavior class, not random recording
- This is stronger than the original compressed sensing prediction

**What the apple pipeline established:**

Full scan→transmit→reconstruct→verify model for a non-neural biological object. Key numbers:

| Stage | Bottleneck? | Key number |
|-------|-------------|------------|
| Scan | No | 160 MB – 1.6 GB at 10 μm resolution |
| Transmit | No | <13s on broadband |
| Reconstruct | **YES** | Needs 10× resolution gain, 100× throughput gain over 2025 bioprinters |
| Verify | No | 24h: GC-MS, texture, nutrition |

Thermodynamic minimum for assembly: ~44 J (entropy cost, negligible). Practical fabricator energy: ~1 kWh. Energy is not the barrier.

Current bioprinting state (2025): ~100 μm resolution, ~10⁶ cells/min. Required: ~10 μm resolution, ~10⁸ cells/s. Neither gap is a physics barrier — both are engineering.

**Fabricator simulation — DONE (math/direction1_fabricator.md):**
- Resolution: 1 μm (neural), 5 μm (somatic)
- Throughput: 10¹⁰ cells/s for 1-hour human fabrication
- Print head: ~10⁷ nozzles in 1 m² array
- Vascular viability solved by hypothermic fabrication at 4 °C (DHCA window of 60 min)
- Energy: ~175 kWh per human (≈ $17.50). No physics barriers; all gaps are engineering.

**Full pipeline simulation — DONE (simulation/run_teleportation_pipeline_v2.py):**
- Path A (full scan → compress → reconstruct → verify): **PASS at 1% biological noise**.
- All 4 test behaviors under 5% divergence (tap, chem, thermo, nociception — last two HELD OUT of probe set).
- Spec size: 6.35 KB (compression ratio 55× vs raw float32).
- Transmit: 52 μs over 1 Gbps Wifi.
- Sim wall-time: 38s for 9k trials. Real-world wall-time at 30s/trial: 75 hours of optogenetic probing.

End-to-end functional teleportation works at C. elegans scale under realistic biological noise. **The complete pipeline is now demonstrated.**

**Scan inverse problem — SOLVED at C. elegans scale at biological noise (simulation/run_scan_inverse_v4.py + math/direction1_scan_inverse_solved.md):**

Protocol: **per-neuron tonic optogenetic perturbation** (N × 3 amplitudes × n_reps trials) + **support-aware ridge regression** on steady-state activity. Two key insights:
1. **Tonic steady-state probes** kill the numerical-difference noise of pulsed protocols (the τ/dt amplification of (r_{t+1}−r_t) noise was destroying tap-circuit small weights).
2. **Per-neuron stim** (rather than per-class) gives every column of W informative data, so held-out behaviors (thermo, nociception) reconstruct correctly.

Results, evaluated on 6 stimulus tests (tap, chem at two amplitudes each, plus held-out thermo and nociception — held out = not in probe set):

| Rate noise | Verdict | Pearson r | Notes |
|---|---|---|---|
| 0%   | PASS  | 0.992 | all 6 div < 0.002 |
| 1%   | PASS  | 0.923 | biological floor; all 6 div < 0.014 |
| 2%   | FAIL  | 0.78  | only tap fails (div_tap ≈ 0.10) at n_reps=10; PASS at n_reps=100 |
| 5%   | FAIL  | 0.85  | tap plateau at div ≈ 0.78 — clipping bias, not variance |

Tap-circuit weights are 27× smaller than global mean → first to break under noise.

**Updated picture: ONE remaining barrier, not two.**
1. **Fabricator** (engineering): 10¹⁰ cells/s, 10⁷ nozzles. No physics barrier.
2. ~~Scan inverse problem~~: solved at C. elegans scale at 1% biological noise.

**Body information budget — DONE (math/direction1_body_information_budget.md):**

Component-by-component rate-distortion analysis of all non-neural systems.

| Component | Bits (functional) | Size |
|---|---|---|
| Brain functional spec | 3.4 × 10⁵ | 42 KB |
| Bulk tissue (tissue-stratified D: cardiac 0.05, muscle 1.0, mixed) | 10¹⁰–10¹¹ | 1–10 GB |
| Adaptive immunity (TCR/BCR) | 10¹⁰ | 1 GB |
| Vasculature (extra) | 10⁹ | 125 MB |
| Per-person genome variants | 10⁸ | 12 MB |
| Epigenome (functional) | 3 × 10⁸ | 40 MB |
| Microbiome composition | 10⁵ | 15 KB |
| Per-person dynamic state | 10³ | 100 B |
| **Total (functional, tissue-stratified)** | **~10¹⁰–10¹¹ bits** | **~1–10 GB** |

Key finding: body is **5–7 orders of magnitude larger than the brain** in
information (despite the brain being ~200× denser per cell), but fits on a
consumer SSD. At 1 Gbps consumer fiber, full human upload = 800 s.
**Transmission is not a bottleneck.** Fabricator remains the only barrier.

**Open questions / next steps:**
2. Scan inverse scaling: protocol requires N × 3 × n_reps = 9k trials for C. elegans. For human (N=86×10⁹) this is 2.6×10¹² trials — not serially feasible. Open: parallel optogenetic probing / sparse-population disambiguation.
3. ~~Vascular lumen patency~~ — **DONE (math/direction1_vascular_patency.md):** force-balance analysis shows 8× safety margin over 60-min window under three engineering requirements (bubble-free saline carrier, ≥1.5 m reservoir head, ≤4°C). Not a physics barrier.
4. Direction 4 (Penrose-Diósi): set the hard quantum ceiling before going deeper on quantum directions.

### Direction 2: Center-of-Mass Tunneling of Macroscopic Bound States
**Status: CLOSED (math/direction2_cm_tunneling.md).** Decoherence times are shorter than any realistic tunneling time by many orders of magnitude for objects > 10⁻¹⁸ kg. Not viable for teleportation.

### Direction 3: Quantum Cheshire Cat Scaling
**Status: CLOSED (math/direction3_quantum_cheshire_cat.md).** Effect is real but fundamentally passive — post-selection constraint makes it non-exploitable for controllable transport.

### Direction 4: Penrose-Diósi Gravitational Collapse Threshold
**Status: CLOSED (math/direction4_penrose_diosi_threshold.md).** Quantum teleportation ceiling at ~50 μm even at 0 K in perfect vacuum (1 second collapse time). Human-scale ruled out by Penrose-Diósi AND independently by thermal photon emission from a warm body (10⁻²³ s decoherence).

### Direction 5: Quantum Darwinism Reconstruction
**Status: CLOSED (math/direction5_quantum_darwinism.md).** Quantum Darwinism is real (Zurek, multiple experimental confirmations) and explains how classical objectivity emerges. But what's redundantly encoded in environmental fragments is the CLASSICAL pointer-basis information — exactly what Direction 1 already uses. Direction 5 collapses to Direction 1.

## Priority Order — REMAINING OPEN

The five quantum directions (2, 3, 4, 5) are all closed (verdicts in their
math files). Direction 1 is fully wired end-to-end at C. elegans scale.

The remaining open work is engineering-side characterization at scale:

1. **Bulk-tissue D-thresholds per tissue type.** Cardiac threshold is 0.05
   (`run_tissue_distortion.py`). Need: muscle contraction, vascular flow,
   bone mineralization, gut peristalsis. Likely all more tolerant than
   cardiac (the worst-case excitable medium). This would tighten the body
   information budget from the current 3–700 GB range.

2. **Apple-scale end-to-end pipeline** with v2 scan + pool stim, to validate
   the pipeline at one intermediate scale before claiming generalization
   to human.

3. **Fabricator-side engineering rigour.** The vascular patency analysis
   (`math/direction1_vascular_patency.md`) is force-balance only; a full
   CFD with soft-tissue FEM would close it rigorously. Same with the
   nozzle-array print-head — current model is throughput math, not real
   fluid dynamics of 10⁷ jets in parallel.

These are not project-blockers — they are engineering refinements that
will be needed when an actual scanner/fabricator is built.

## Strict Rules
- Show all math, don't skip steps
- Every assumption labeled explicitly with its justification
- Distinguish: **established physics** / **theoretical mainstream** / **speculative** / **this project's conjecture**
- If a direction hits a fundamental wall, document exactly where and why, then stop pursuing it
- NEVER EVER include Claude as a co-author, contributor, or co-committer in any commit, PR, or anywhere on this repo

## Key Files

### Simulation
- `simulation/run_distortion.py` — C. elegans distortion sweep (confirms 30% tolerance)
- `simulation/run_deff.py` — C. elegans d_eff extraction
- `simulation/run_drosophila_deff.py` — Drosophila d_eff
- `simulation/run_mouse_deff.py` — Mouse V1 d_eff + three-organism scaling law
- `simulation/run_generative_model_targeted_pulse.py` — per-class K=1 generative model result
- `simulation/run_teleportation_pipeline.py` — v1: end-to-end pipeline (Path A FAILS at scan)
- `simulation/run_teleportation_pipeline_v2.py` — **v2 end-to-end pipeline with v4 SCAN: Path A PASS at 1% biological noise on 4 behaviors (2 held out)**
- `simulation/run_scan_inverse_problem.py` — v1: unified-W scan reconstruction (6 approaches, support-aware best, FAIL)
- `simulation/run_scan_inverse_v2.py` — v2: tonic SS probes (PASS zero-noise, FAIL on held-out classes)
- `simulation/run_scan_inverse_v2_robust.py` — robustness check; revealed v2 noise failures
- `simulation/run_scan_inverse_v3.py` — v3: per-neuron probes (PASS all held-out at zero noise)
- `simulation/run_scan_inverse_v4.py` — **v4: per-neuron + n_reps averaging (PASS at 1% biological noise)**
- `simulation/run_scan_inverse_nreps_sweep.py` — n_reps requirements at 2%/5% noise
- `simulation/run_circuit_diagnostic.py` — gap junction ablation + weight analysis
- `simulation/rate_model.py` — firing rate model (tanh, not LIF)
- `simulation/load_connectome.py` — Cook et al. 2019 loader

### Math
- `math/direction1_rate_distortion.md` — Shannon R-D derivation (42 KB result)
- `math/direction1_scaling_law.md` — three-organism d_eff data and scaling law
- `math/direction1_scanner_revised.md` — compressed sensing reframe of scanner problem
- `math/apple_pipeline.md` — apple proof-of-concept teleportation pipeline model
- `math/direction1_fabricator.md` — **human-scale fabricator: resolution, throughput, Krogh+DHCA vascular constraint**
- `math/direction1_scan_inverse_solved.md` — **scan inverse problem solved at C. elegans scale + 1% biological noise**
- `math/direction1_body_information_budget.md` — **full body (non-neural) rate-distortion budget: 3–700 GB (revised w/ tissue D=0.05)**
- `math/direction1_scan_inverse_pool.md` — **pool-based scan inverse: 10⁶ trials for human (vs 10¹² per-neuron); higher fidelity than per-neuron**
- `math/direction1_vascular_patency.md` — **capillary patency under hypothermic fabrication: 8× safety margin if bubble-free + pressure-regulated**
- `simulation/run_scan_inverse_pool.py` — **pool stimulation sweep: K=100,M=15 → r=0.99 PASS**
- `simulation/run_tissue_distortion.py` — **2D cardiac propagation sim: tissue D-threshold = 0.05 (6× more sensitive than brain)**
- `simulation/run_muscle_distortion.py` — **muscle force production sim: skeletal muscle D-threshold = 1.0 (20× more tolerant than cardiac)**

### Data (gitignored, too large for GitHub)
- `simulation/data/SI5_connectome_adjacency.xlsx` — C. elegans Cook 2019
- `simulation/data/flywire_connections_783.feather` — Drosophila FlyWire 783 (~852 MB)
- `simulation/data/microns_mm3_connectome.h5` — Mouse V1 MICrONS mm3 (~725 MB)

## File Structure
- `CLAUDE.md` — this file
- `research/` — background literature, government docs, paper notes
- `math/` — derivations and calculations
- `architecture/` — design docs (use once a direction shows enough promise)
- `simulation/` — Python scripts; results go to `simulation/results/`
