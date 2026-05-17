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

**Full pipeline simulation — DONE (simulation/run_teleportation_pipeline.py):**
- Path B (compression round-trip on ideal W): PASS at <0.01% behavioral divergence on tap and chem.
- Path A (full scan → compress → reconstruct → verify): FAIL at the SCAN stage.
- Compression: 70× ratio (10 KB spec for C. elegans, vs 700 KB raw).
- Transmit: ~80 μs over Wifi.

**Scan inverse problem — PARTIAL (simulation/run_scan_inverse_problem.py):**
Six approaches tested for recovering a unified W from activity recordings:
- Combined ridge, weighted blend, iterative refinement, modular variants: all fail (r ≤ 0.11).
- Support-aware combined regression (D): r = 0.72, chem div = 0.056 (just over 5% threshold), tap div = 0.57.
- Knowing the binary topology (from a separate structural EM scan) cuts unknowns from N² to ~12 per neuron — this is the single most important lever.
- Remaining bottleneck: small-signal circuits (tap weights are 27× smaller than mean) get washed out under joint regression. This is a measurement / observability problem, not an information-theoretic one.

**Updated picture: the binding constraints are now TWO problems, not one.**
1. **Fabricator** (engineering): 10¹⁰ cells/s, 10⁷ nozzles. No physics barrier.
2. **Scan inverse problem** (algorithm): recovering a unified sparse W that simultaneously reproduces all behaviors. Open at C. elegans scale; tap circuit remains a blocker even with structural support known.

**Open questions / next steps:**
1. Scan inverse problem: better stimulus design (frequency-rich, behavior-class-specific high-amplitude probes), or circuit-decomposition reconstruction (different W slices per functional module).
2. Body information budget: extend d_eff / rate-distortion framework to non-neural somatic cells. Is the body really 1–2 orders of magnitude harder than the brain, or more?
3. Vascular lumen patency: simulate 8 μm capillary lumen collapse dynamics under hypothermic fabrication. The 60-min window assumes immediate perfusion; verify this engineering assumption holds.

### Direction 2: Center-of-Mass Tunneling of Macroscopic Bound States
**Status: Not started.** Levitated nanoparticle experiments are measuring this now. The scaling theory (tunneling amplitude vs. mass, barrier geometry, decoherence rate) is missing.

### Direction 3: Quantum Cheshire Cat Scaling
**Status: Not started.** Effect is real (Denkmayr 2014). Whether it generalizes beyond spin is unknown. Two-state vector formalism needs to be worked through.

### Direction 4: Penrose-Diósi Gravitational Collapse Threshold
**Status: Not started.** τ ≈ ℏ/E_G is calculable. Sets a hard ceiling for quantum teleportation approaches. Should be done before investing in quantum methods.

### Direction 5: Quantum Darwinism Reconstruction
**Status: Not started.** Most speculative. Do last.

## Priority Order
1. **Scan inverse problem** — close the C. elegans gap (current best: r=0.72, tap div=0.57). Next attacks: frequency-rich probes, circuit decomposition, lasso/sparse priors on the support.
2. **Direction 1 body information budget** — quantify the non-neural piece.
3. **Direction 4 (Penrose-Diósi)** — sets the hard quantum ceiling before going deeper on quantum directions.
4. **Direction 2 (CM tunneling)** — real ongoing experiments, missing scaling theory.
5. **Directions 3 and 5** — lower priority.

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
- `simulation/run_teleportation_pipeline.py` — **end-to-end pipeline: scan → compress → transmit → reconstruct → verify + fabricator projection**
- `simulation/run_scan_inverse_problem.py` — **unified-W scan reconstruction (6 approaches, support-aware best)**
- `simulation/run_circuit_diagnostic.py` — gap junction ablation + weight analysis
- `simulation/rate_model.py` — firing rate model (tanh, not LIF)
- `simulation/load_connectome.py` — Cook et al. 2019 loader

### Math
- `math/direction1_rate_distortion.md` — Shannon R-D derivation (42 KB result)
- `math/direction1_scaling_law.md` — three-organism d_eff data and scaling law
- `math/direction1_scanner_revised.md` — compressed sensing reframe of scanner problem
- `math/apple_pipeline.md` — apple proof-of-concept teleportation pipeline model
- `math/direction1_fabricator.md` — **human-scale fabricator: resolution, throughput, Krogh+DHCA vascular constraint**

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
