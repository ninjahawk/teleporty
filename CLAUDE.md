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

## File Structure
- `CLAUDE.md` — this file
- `research/` — background literature, government docs, paper notes
- `research/unconventional_angles.md` — detailed treatment of the 5 active directions
- `math/` — derivations, calculations, numerical simulations
- `architecture/` — design docs for a conceptual system once a direction shows promise
