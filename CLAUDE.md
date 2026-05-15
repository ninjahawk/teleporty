# Teleporty — Teleportation Research Project

## STRICT RULE — COMMITS AND CONTRIBUTORS
**NEVER EVER include Claude as a co-author, contributor, or co-committer in any commit, PR, or anywhere on this repo. Do NOT add `Co-Authored-By: Claude` or any similar line to commit messages. Commits are authored by the human only.**



## Project Goal
Find a mechanism, reframing, or approach to teleportation that is physically grounded, has not been seriously pursued, and produces a simulation with testable predictions. The goal is discovery, not literature review.

**Honesty rule:** This is math and science. Do not produce results to make the user feel good. If something is impossible, say so with the math that shows why. If something is possible, show the derivation. No rounding off, no handwaving, no softening conclusions.

## What We've Established Is Dead (and Why)
- **Full quantum state teleportation of matter**: decoherence (~10⁻²³ s for macroscopic objects at room temp), Heisenberg measurement problem, and 10²⁸-bit bandwidth requirement hit simultaneously. Not an engineering problem — a fundamental one.
- **Traversable wormholes**: Ford-Roman quantum inequalities bound negative energy density too tightly. The Casimir effect is ~38 orders of magnitude too weak for a 1 m throat. Not a materials problem.
- **Warp drive (Alcubierre)**: same exotic matter wall. White's 2012 geometry still requires Jupiter-mass negative energy and is causally disconnected from the interior.
- **Psychic teleportation**: pseudoscience. Not considered further.

## Active Research Directions (the alleyways)

### Direction 1: Functional Teleportation — Minimum Information Reframing
The quantum barriers apply to copying every quantum state of every particle. But functional identity is probably encoded in classical information: connectome (~10¹⁵ bits), molecular composition, biochemistry. At the classical level, none of the quantum barriers apply.

**Open question:** What is the minimum classical information required for functional equivalence, and what is the physical lower bound on reconstruction fidelity? Nobody has built a rigorous model of this.

**Goal:** Build an information-theoretic model. Calculate: minimum bits, transmission time at various bandwidths, reconstruction energy from raw atoms, error tolerance.

### Direction 2: Center-of-Mass Tunneling of Macroscopic Bound States
Composite objects have a center-of-mass wavefunction that is distinct from the internal degrees of freedom. A BEC or superconductor tunnels as a unit. Levitated nanoparticle experiments have placed ~10⁷-atom objects in spatial superpositions.

**Open question:** What is the tunneling amplitude for a composite bound object as a function of mass, internal temperature, barrier geometry, and decoherence rate? How does it scale? Where is the practical cutoff?

**Goal:** Derive the center-of-mass tunneling amplitude for a composite object with internal thermal noise. Compare to levitated particle experimental results. Find the feasible mass/distance regime.

### Direction 3: Quantum Cheshire Cat Scaling
Denkmayr et al. 2014 demonstrated experimentally that a neutron's spin was found in a spatially separate location from the neutron. The effect is real and measured. The mechanism is pre/post-selection in an interferometer.

**Open question:** Does this effect generalize beyond spin? Can it apply to mass, charge, or other properties? Is there a sense in which a property "relocates" that is physically meaningful for transport?

**Goal:** Work through the mathematical formalism (two-state vector formalism, weak measurements). Determine what the effect can and cannot transmit. If it can transmit anything useful, characterize the conditions.

### Direction 4: Penrose-Diósi Gravitational Collapse Threshold
If objective gravitational collapse is real (Penrose-Diósi model), the decoherence timescale for a superposition is:

τ ≈ ℏ / E_G

where E_G = G ∫∫ [ρ_A(r) - ρ_B(r)]² / |r - r'| d³r d³r'

This gives a hard, calculable mass-dependent ceiling on how long a quantum superposition can exist — and therefore the maximum scale of quantum teleportation.

**Goal:** Calculate τ as a function of object mass and superposition separation. Compare to current nanoparticle experiments. Determine whether this is the binding constraint or whether thermal decoherence wins first.

### Direction 5: Quantum Darwinism Reconstruction
Every physical object imprints redundant classical copies of its pointer states onto environmental photons, air molecules, and thermal radiation. Zurek's quantum Darwinism quantifies this.

**Open question:** What fraction of an object's classical state information is recoverable from environmental records within a finite spacetime volume? Is this sufficient for functional reconstruction?

**Goal:** Model information recovery from environmental imprints. Calculate the redundancy factor and accessible fidelity as a function of object size, environment density, and time.

## Priority Order
1. Direction 1 (functional teleportation reframing) — most honest near-term path, fewest assumptions
2. Direction 4 (Penrose-Diósi) — sets the hard ceiling for all quantum approaches; do this before investing heavily in quantum methods
3. Direction 2 (CM tunneling) — real physics, currently being measured, scaling math is missing
4. Direction 3 (Cheshire cat) — interesting but may be a dead end; check the formalism first
5. Direction 5 (Darwinism) — most speculative of the five; do last

## Strict Rules
- Show all math, don't skip steps
- Every assumption labeled explicitly with its justification
- Distinguish: **established physics** / **theoretical mainstream** / **speculative** / **this project's conjecture**
- If a direction hits a fundamental wall, document exactly where and why, then stop pursuing it
- NEVER EVER include Claude as a co-author, contributor, or co-committer in any commit, PR, or anywhere on this repo

## Current State of Direction 1 (as of 2026-05-15)

### What has been measured
Three connectomes processed, d_eff extracted via weight-matrix PCA (participation ratio):

| Organism | N neurons | d_eff | Source |
|----------|-----------|-------|--------|
| C. elegans | 302 | 28 | Cook et al. 2019 (wormwiring.org) |
| Mouse V1 | 50,943 | 146 | MICrONS mm3 portion 65 (Zenodo 16744240) |
| Drosophila | 138,639 | ~700 | FlyWire 783 (Zenodo 10676866) |

Scaling law fit (three-point, log-log): **d_eff = 1.85 × N^0.459**

Human extrapolation (N = 86×10⁹): **d_eff ≈ 2×10⁵**

Minimum bits for functional reconstruction (D=30% distortion): **R ≈ 42 KB**
vs. original assumption: 10¹²–10¹³ bits. Revised by 7–8 orders of magnitude.

The 30% distortion tolerance is empirically confirmed in C. elegans simulation (behavioral divergence <2% at D=0.30).

### Scanner problem (revised)
Compressed sensing measurement count: M = d_eff × log₂(N_s/d_eff) ≈ **6×10⁶ measurements** (not 10¹⁴ synapses).

Two viable paths:
1. **Functional recording** (living): ~10⁶ neurons distributed across brain × ~3 diverse behavioral conditions theoretically sufficient to span d_eff = 2×10⁵ activity manifold. Requires ~10,000 distributed electrode sites (1000× Neuralink scale).
2. **Sparse structural EM** (destructive): random 0.01% spatial subsample + matrix completion.

Current bottlenecks:
- Generative model (activity → structure): TRL 2–3, needs training data from paired functional+structural recordings
- Distributed electrode deployment at safe density: ~10,000 probes in living brain, physiological effects unknown
- Rapid whole-brain vitrification (destructive path): not demonstrated at human scale

### Generative Model Test — Prediction 3 (as of 2026-05-15)

**Status: Partially falsified. Critical refinement required.**

Ran `simulation/run_generative_model_test.py` — tests whether activity recordings under K stimulus conditions can reconstruct synaptic weights W well enough to reproduce behavior.

**What we tried (three versions):**

1. **Steady-state regression** (v1): Fit W from time-averaged activity at "steady state." Consistency error = 0.61 (huge). FAILED. Root cause: the network oscillates under constant drive — it never reaches a fixed point. The time-averaging approximation is fatally violated.

2. **Dynamical regression, shared A** (v2): Use time-series directly — at each valid step t, z_j(t) = atanh((r_j(t+1)-r_j(t))×tau/dt + r_j(t))/gain - I_gap_j - I_ext_j = Σ_i W[i,j] r_i(t) exactly. Consistency check = 7e-15 (machine precision). But behavioral divergence WORSENED with K. Root cause: zero-padding invalid entries (r_j(t+1)=0) in the shared A matrix created a biased regression that got worse as A grew.

3. **Dynamical regression, per-neuron A_j** (v3, current best): For each target neuron j, compute A_j = A_all - A_invalid_j (subtract contribution of steps where neuron j was clipped to 0). Consistency still ~0. Results:
   - Pearson r improves with K: 0.28 (K=1) → 0.87 (K=50)
   - Frobenius error decreases: 0.97 → 0.59
   - **div_chem: 6.4% at K=3-5 with random training** (near 5% threshold)
   - **div_chem: 0.63% with 1 dedicated chem training condition** (CONFIRMED)
   - **div_tap: stuck at 60-70% regardless of K, even when tap condition explicitly added**

**Root cause of tap failure (diagnosed):**
The tap TEST stimulus is a 30ms pulse (transient). The tap TRAINING condition used constant drive, which saturates tap neurons at r≈0.97. Regression near saturation (tanh flat at ±1) is poorly conditioned — weight estimation becomes imprecise. The transient test probes dynamics that constant training didn't span.

This is NOT a fundamental failure of the method. It is a **training protocol problem**: the training stimuli must match the temporal structure (transient vs. sustained) of the behaviors being reconstructed, not just cover the right neurons.

**What this means for the scanner:**
- The "K ~ d_eff diverse conditions" prediction holds for behaviors where training matches test temporal structure (chemotaxis confirmed at 0.6% divergence)
- For transient behaviors (tap withdrawal, any reflexive response), training must include matching transient stimuli — not just random constant drives
- The correct scanner protocol is naturalistic behavioral recording (which naturally provides transient patterns), not random constant-input recording
- This is a REFINEMENT of the scanner prediction, not a failure

**Next step (highest priority):**
Re-run generative model test with PULSED training stimuli (matching the transient temporal structure of the test stimuli). Specific test: use K=5 pulsed random stimuli (30ms pulses at random neurons). Predict: div_tap drops to <5% for K ~ a few conditions.

If pulsed training works: write up the refined scanner prediction (naturalistic behavioral recording, pulsed stimuli, K~d_eff per behavior class).
If pulsed training fails: the C. elegans tap circuit has additional structure (e.g., gap junctions, history-dependent dynamics) that requires more data.

### Key simulation files
- `simulation/run_distortion.py` — C. elegans distortion sweep (confirms 30% tolerance)
- `simulation/run_deff.py` — C. elegans d_eff extraction
- `simulation/run_drosophila_deff.py` — Drosophila d_eff (randomized SVD k=3000)
- `simulation/run_mouse_deff.py` — Mouse V1 d_eff + three-organism scaling law
- `simulation/run_generative_model_test.py` — Prediction 3 test (v3, per-neuron A_j dynamical regression)
- `simulation/rate_model.py` — firing rate model (tanh, NOT LIF — LIF abandoned due to E/I classification requirement)
- `simulation/load_connectome.py` — Cook et al. 2019 loader

### Key math files
- `math/direction1_scaling_law.md` — three-organism d_eff data and scaling law fit
- `math/direction1_scanner_revised.md` — compressed sensing reframe of the scanner problem
- `math/direction1_rate_distortion.md` — Shannon R-D derivation

### Data files (gitignored, too large for GitHub)
- `simulation/data/SI5_connectome_adjacency.xlsx` — C. elegans Cook 2019
- `simulation/data/flywire_connections_783.feather` — Drosophila FlyWire 783 (~852 MB)
- `simulation/data/microns_mm3_connectome.h5` — Mouse V1 MICrONS mm3 (~725 MB)

## File Structure
- `CLAUDE.md` — this file
- `research/` — background literature, government docs, paper notes
- `research/unconventional_angles.md` — detailed treatment of the 5 active directions
- `math/` — derivations, calculations, numerical simulations
- `architecture/` — design docs for a conceptual system once a direction shows promise
- `simulation/` — Python scripts; results go to `simulation/results/`
