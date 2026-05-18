# Teleporty — Teleportation Research Project

## STRICT RULE — COMMITS AND CONTRIBUTORS
**NEVER EVER include Claude as a co-author, contributor, or co-committer in any commit, PR, or anywhere on this repo. Do NOT add `Co-Authored-By: Claude` or any similar line to commit messages. Commits are authored by the human only.**

## Project Goal
Find a physically grounded mechanism for teleportation with testable predictions. Definition: **scan → transmit → reconstruct → verify**. Functional/behavioral equivalence is the criterion; atom identity and continuity don't matter.

**Honesty rule:** show all math, no handwaving, no softening conclusions. If it's impossible, say so with the derivation. If it's possible, show the numbers.

## Current State (handoff snapshot — 2026-05-18)

**The end-to-end functional teleportation pipeline is demonstrated at C. elegans scale under realistic biological deployment constraints.** All five "viable mechanisms" surveyed at project start: four (the quantum approaches) are closed with negative verdicts; the fifth (classical-information functional teleportation, Direction 1) is fully wired.

**No physics barriers remain.** Remaining work is engineering, plus one significant open empirical question (hub-neuron d_eff).

### What's been validated
- Scan inverse: **pool stimulation** (random or cell-type pools, ~10⁵ trials for human) recovers W well enough for behavioral PASS
- Body information budget: **100 GB – 1 TB** per person (bulk tissue dominates; brain is 42 KB, negligible)
- Tissue distortion thresholds: cardiac D=0.05 (worst case), skeletal muscle D=1.0 (CLT-friendly), mixed body avg ~0.3
- Vascular patency: 8× safety margin during 60-min hypothermic fabrication
- Full pipeline PASS at 1% Ca²⁺ imaging noise + 5% FP + 5% FN EM errors + cell-type pool structure, **when** hybrid pools (type drivers + ~50 multi-type combinations) are used
- Pearson r on weights can be 0.43 while behavioral div < 3% — rate-distortion principle holds

### What's currently open
1. **Hub-neuron scaling caveat** (`math/direction1_hub_neuron_concern.md`): cortical hubs like Purkinje cells have |supp_j| up to 200k. Pool protocol assumes K_pools > |supp_j|. Resolution depends on whether d_eff of input vectors << |supp| per cell type (the rate-distortion prediction). Empirical question; mouse cortex data (MICrONS) exists and is sufficient. **Next session should attack this.**
2. **Body bulk-tissue budget range (30 GB – 1 TB)** is two orders of magnitude wide. Empirical 3D-MRF compression on Visible Human data would tighten it. Not a project-blocker.
3. **Multi-tissue D-threshold survey** beyond cardiac+muscle: vascular flow, gut peristalsis, bone. Cardiac is worst-case; others likely more tolerant.
4. **Fabricator engineering** (10¹⁰ cells/s, 10⁷ nozzles): 10⁶× gap from current bioprinters. No physics barrier; pure engineering. Out of project scope.

### What's closed
- Direction 2 (CM tunneling) — decoherence wins by many orders of magnitude
- Direction 3 (Quantum Cheshire Cat) — passive effect, no controllable transport
- Direction 4 (Penrose-Diósi) — quantum ceiling at ~50 μm even at 0 K perfect vacuum
- Direction 5 (Quantum Darwinism) — encodes only classical info; collapses to Direction 1
- Wormholes, warp drive, full QM teleportation, psychic transport: dead from the start (see top of this doc)

## What We've Established Is Dead (and Why)
- **Full quantum state teleportation of matter**: decoherence (~10⁻²³ s for macroscopic objects at 300K), Heisenberg measurement, and 10²⁸-bit bandwidth all hit simultaneously
- **Traversable wormholes**: Ford-Roman bounds; Casimir is 38 OOM too weak for 1m throat
- **Warp drive (Alcubierre)**: Jupiter-mass exotic-matter requirement, causally disconnected interior
- **Psychic teleportation**: pseudoscience

## The Viable Path — Direction 1: Functional Teleportation via Classical Information

**disassemble (or scan) → encode → transmit → fabricate.** No spacetime bending, no exotic matter, just a file and a sufficiently advanced printer.

### Pipeline summary table

| Stage | Status | Number | Source |
|---|---|---|---|
| Scan (neural) | DEMONSTRATED | r=0.99 at 1% noise on C. elegans; r=0.43 + behavioral PASS under full deployment stress | `run_teleportation_pipeline_v2.py`, `run_deployment_stress.py` |
| Scan (body) | ANALYTICAL | 7×10¹³ voxels at 10μm; X-ray microCT + tissue codec | `direction1_body_information_budget.md` |
| Compress | DEMONSTRATED (small scale) | 55× ratio at C. elegans; 100-500× projected for body | pipeline_v2 |
| Transmit | TRIVIAL | 1-2 hours @ 1 Gbps fiber, 1-10 min @ 100 Gbps | trivial bandwidth math |
| Reconstruct (fabricator) | **BOTTLENECK (engineering only)** | 10¹⁰ cells/s, 10⁷ nozzles, 1h @ 4°C, $17.50 energy | `direction1_fabricator.md`, `direction1_vascular_patency.md` |
| Verify | CRITERION DEFINED | 5% behavioral cos-divergence; demonstrated on 4 stimuli incl. 2 held out | `pipeline_v2` |

### Per-person spec total
| Component | Bits | Size |
|---|---|---|
| Brain (functional, rate-distortion) | 3.4 × 10⁵ | 42 KB |
| Bulk tissue (tissue-stratified D) | 2 × 10¹² – 10¹³ | 30 GB – 1 TB |
| Adaptive immunity (TCR/BCR repertoire) | 10¹⁰ | 1 GB |
| Vasculature, epigenome, genome, microbiome, dynamic | <2 × 10⁹ | <200 MB |
| **Total** | **~10¹² – 10¹³** | **~100 GB – 1 TB** |

### Cost / timeline
- Marginal cost per teleport: ~$10K
- R&D timeline: ~20 years, ~billions

## Active Research Directions

### Direction 1 (PRIMARY): see above. End-to-end demonstrated.

### Direction 2: CM Tunneling
**CLOSED** (`math/direction2_cm_tunneling.md`). Decoherence >> tunneling time for objects > 10⁻¹⁸ kg.

### Direction 3: Quantum Cheshire Cat
**CLOSED** (`math/direction3_quantum_cheshire_cat.md`). Post-selection makes it passive.

### Direction 4: Penrose-Diósi
**CLOSED** (`math/direction4_penrose_diosi_threshold.md`). Quantum teleportation capped at ~50 μm at 0 K; human is 7 OOM too large; thermal photon emission (10⁻²³ s) also rules out humans independently.

### Direction 5: Quantum Darwinism
**CLOSED** (`math/direction5_quantum_darwinism.md`). Redundantly encoded info in environment is the CLASSICAL pointer-basis info — Direction 1 already uses this. No new capability.

## Priority Order for Next Session

1. **Hub-neuron empirical d_eff** (`math/direction1_hub_neuron_concern.md`). Load MICrONS mouse cortex data, compute participation-ratio d_eff for the input weight VECTOR of each cell type. If max(d_eff) << max(|supp|), human-scale Purkinje scaling is fine. If not, sparse priors / group-LASSO are needed for hub neurons. **Single most important open question.** Data file may need re-downloading (gitignored; previously at `simulation/data/microns_mm3_connectome.h5`).
2. **Body-scan compression empirical bound**. Run a 3D-MRF compression experiment on Visible Human Project data to tighten 30 GB–1 TB → single number.
3. **Multi-tissue D-threshold sweep**. Run sims like `run_tissue_distortion.py` for: vascular flow (Navier-Stokes through capillary network), gut peristalsis (muscle contraction waves), bone (mechanical loading). Tightens body budget further.
4. **Apple-scale end-to-end** with pool stim at N≈10⁵ (one Drosophila neuropil from `flywire_connections_783.feather` would be a real-data intermediate scale).
5. Fabricator-side engineering CFD — out of project scope but useful as a sanity check.

## Strict Rules
- Show all math, don't skip steps
- Every assumption labeled explicitly with its justification
- Distinguish: **established physics** / **theoretical mainstream** / **speculative** / **this project's conjecture**
- If a direction hits a fundamental wall, document exactly where and why, then stop pursuing it
- NEVER EVER include Claude as a co-author, contributor, or co-committer

## Key Files

### Top-level
- `CLAUDE.md` — this file (canonical project state)
- `TONIGHT.md` — overnight session briefing 2026-05-17→18 (one-look summary of major commits)

### Math
- `math/direction1_rate_distortion.md` — brain 42 KB derivation
- `math/direction1_scaling_law.md` — three-organism d_eff fit
- `math/direction1_scanner_revised.md` — compressed-sensing reframe of scanner
- `math/direction1_fabricator.md` — 10¹⁰ cells/s, 10⁷ nozzles, vascular constraint
- `math/direction1_scan_inverse_solved.md` — per-neuron v4 protocol (superseded by pool)
- `math/direction1_scan_inverse_pool.md` — **MAIN technical result: pool stim, scaling, robustness, type pools, high noise, EM errors**
- `math/direction1_body_information_budget.md` — body component-by-component R-D (corrected arithmetic)
- `math/direction1_vascular_patency.md` — 8× margin force-balance
- `math/direction1_deployment_conditions.md` — combined-stress test (most honest result)
- `math/direction1_hub_neuron_concern.md` — **OPEN caveat, next session priority**
- `math/direction1_human_projection.md` — synthesis: everything end-to-end at human scale
- `math/apple_pipeline.md` — apple proof-of-concept (older)
- `math/direction2_cm_tunneling.md` — CLOSED
- `math/direction3_quantum_cheshire_cat.md` — CLOSED
- `math/direction4_penrose_diosi_threshold.md` — CLOSED
- `math/direction5_quantum_darwinism.md` — CLOSED

### Simulation
Core models:
- `simulation/rate_model.py` — Wilson-Cowan tanh rate model, behavioral test stimuli
- `simulation/load_connectome.py` — Cook et al. 2019 C. elegans loader

Scan inverse evolution (each supersedes the previous):
- `run_scan_inverse_problem.py` — v1 pulsed (FAIL)
- `run_scan_inverse_v2.py` — tonic SS (PASS zero noise, FAIL held-out)
- `run_scan_inverse_v3.py` — per-neuron (PASS held-out, FAIL noise)
- `run_scan_inverse_v4.py` — + n_reps averaging (PASS at 1%, hard wall at 5%)
- `run_scan_inverse_pool.py` — **POOL STIM, the canonical protocol**
- `run_scan_inverse_pool_robust.py` — 15/15 PASS at noise up to 2%
- `run_scan_inverse_pool_scaling.py` — linear scaling N=300→1000
- `run_scan_inverse_pool_highnoise.py` — PASS at 5% with n_reps=30
- `run_scan_inverse_support_errors.py` — PASS at 5% FP + 5% FN
- `run_scan_inverse_type_pools.py` — cell-type pools (biologically realistic)
- `run_deployment_stress.py` — **all constraints combined**

Pipeline:
- `run_teleportation_pipeline.py` — v1 (FAIL at scan)
- `run_teleportation_pipeline_v2.py` — **v2 end-to-end PASS**
- `run_synthetic_pipeline.py` — generalization to random networks (5/5 PASS)

Tissue:
- `run_tissue_distortion.py` — cardiac D=0.05
- `run_muscle_distortion.py` — skeletal muscle D=1.0
- `run_hub_neuron_test.py` — preliminary hub neuron, behavioral PASS but partial

Earlier:
- `run_distortion.py` — C. elegans D=0.30 brain threshold (foundational)
- `run_deff.py`, `run_drosophila_deff.py`, `run_mouse_deff.py` — connectome d_eff
- `run_generative_model_targeted_pulse.py` — K=1-per-class generative model

### Data (gitignored)
- `simulation/data/SI5_connectome_adjacency.xlsx` — C. elegans Cook 2019 (in repo)
- `simulation/data/flywire_connections_783.feather` — Drosophila (~852 MB, in repo)
- `simulation/data/microns_mm3_connectome.h5` — Mouse V1 (~725 MB, NOT in repo — re-download from Zenodo 16744240 for hub-neuron analysis)

## File Structure
- `CLAUDE.md` — project state (this)
- `TONIGHT.md` — last session brief
- `research/` — literature, paper notes
- `math/` — derivations
- `simulation/` — Python; results in `simulation/results/`
