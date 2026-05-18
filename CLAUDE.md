# Teleporty — Teleportation Research Project

## STRICT RULE — COMMITS AND CONTRIBUTORS
**NEVER EVER include Claude as a co-author, contributor, or co-committer in any commit, PR, or anywhere on this repo. Do NOT add `Co-Authored-By: Claude` or any similar line to commit messages. Commits are authored by the human only.**

## Project Goal
Find a physically grounded mechanism for teleportation with testable predictions. Definition: **scan → transmit → reconstruct → verify**. Functional/behavioral equivalence is the criterion; atom identity and continuity don't matter.

**Honesty rule:** show all math, no handwaving, no softening conclusions. If it's impossible, say so with the derivation. If it's possible, show the numbers.

## Current State (handoff snapshot — 2026-05-18)

**The end-to-end functional teleportation pipeline is solidly demonstrated for C. elegans** (N=300) — the connectome and rate model the project was built and validated on: scan-inverse recovers W at Pearson 0.99, full pipeline passes end-to-end under noise / EM error / deployment stress.

**It is NOT yet demonstrated for real mammalian-scale connectomes.** FlyWire (Drosophila) tests revealed a MODEL limitation: FlyWire synapse counts span 1–2405 (3.4 orders of magnitude). The project's uniform-parameter rate model (one gain/threshold/time-constant for all neurons) cannot place synapses of such varied strength all in the responsive regime — /max normalization leaves typical synapses near-silent (Pearson 0.35); /p99 saturates the strong ones (Pearson −0.02). No single scaling works. The FlyWire MB "PASSes" at N≤2000 were the rate-distortion principle masking a weak (0.35) reconstruction. See `math/direction1_density_limitation.md`. This is the most significant honest correction of the project: the protocol is sound for the C. elegans model; extending to real connectomes needs a heterogeneous-excitability model first.

All five "viable mechanisms" surveyed at project start: four (quantum approaches) closed with negative verdicts; the fifth (Direction 1) is the viable path, with the classical-information / rate-distortion / fabricator analysis intact, the scan-inverse demonstrated for C. elegans, and the real-connectome extension blocked on a model upgrade.

**No physics barriers remain.** Remaining work is engineering — but one piece of that engineering (mega-hub reconstruction at scale) is genuinely unsolved in this repo, not just "scale up known methods." The low-rank structure that should make it solvable is measured; the algorithm to exploit it is not yet built.

### What's been validated
- Scan inverse: **pool stimulation** (random or cell-type pools, ~10⁵ trials for human) recovers W well enough for behavioral PASS
- Body information budget: **~247 GB per person** (7-tissue stratified, vol-weighted; was 100 GB – 1 TB range, now pinpointed)
- Tissue distortion thresholds: cardiac D=0.05 (worst case), skeletal muscle D=1.0 (CLT-friendly), mixed body avg ~0.3
- Vascular patency: 8× safety margin during 60-min hypothermic fabrication
- Full pipeline PASS at 1% Ca²⁺ imaging noise + 5% FP + 5% FN EM errors + cell-type pool structure, **when** hybrid pools (type drivers + ~50 multi-type combinations) are used
- Pearson r on weights can be 0.43 while behavioral div < 3% — rate-distortion principle holds
- **Real-data test (FlyWire mushroom body subset, N=797):** strong-ridge fallback for under-determined hubs gives PASS on all 5 random behavioral tests (div 0.003-0.015) even with Pearson r=0.37. Direct empirical confirmation of rate-distortion on real biological data.

### What's currently open
1. **Mega-hub reconstruction — OPEN, top priority** (`math/direction1_megahub_limitation.md`). The pipeline PASSES at N≤800 (C. elegans + small Drosophila subset, max |supp|≤686) but FAILS at N=2000 Drosophila subset (max |supp|=1703) — behavioral div stuck at 0.13 regardless of coverage. The hub d_eff IS low (FlyWire 25-58, C. elegans 3.72), so the information exists — but the strong-ridge fallback only handles moderate hubs. Mega-hubs (|supp|>1000) need a genuine multi-task low-rank reconstruction (trace-norm-penalized, fit all hubs of a type jointly). The ALS and SVD-shrinkage attempts this session were marginal. **This is the #1 unsolved engineering problem. Not a physics barrier — low-rank structure is measured — but unimplemented.**
2. ~~**Body bulk-tissue budget range**~~ — **EMPIRICALLY CONFIRMED 2026-05-18.** Theory R-D bound on 200³ synthetic voxel grid gives 0.031 bits/voxel → ~270 GB at full body scale (matches the body budget estimate). Gzip catastrophically over-counts (68 TB) because it's a 1D codec; a 3D-aware wavelet codec reaches theory. 100 GB – 1 TB range stands.
3. **Multi-tissue D-threshold survey** beyond cardiac+muscle: vascular flow (predicted D ≈ 0.01 due to Hagen-Poiseuille r⁴ sensitivity), gut peristalsis, bone. Cardiac is worst-case; others mostly more tolerant. Refinement, not blocker.
4. **Apple-scale end-to-end** on real biological data at intermediate N (10⁴–10⁵). Would use a Drosophila neuropil subset. Validates the pipeline at one real intermediate scale before claiming generalization to human.
5. **Fabricator engineering** (10¹⁰ cells/s, 10⁷ nozzles): 10⁶× gap from current bioprinters. No physics barrier; pure engineering. Out of project scope.

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
| Bulk tissue (7-tissue stratified D, vol-weighted) | 2 × 10¹² | **~245 GB** |
| Adaptive immunity (TCR/BCR repertoire) | 10¹⁰ | 1 GB |
| Vasculature, epigenome, genome, microbiome, dynamic | <2 × 10⁹ | <200 MB |
| **Total** | **~2 × 10¹²** | **~247 GB** |

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

1. **Heterogeneous-excitability rate model** (`math/direction1_density_limitation.md`). THE top open problem. Real connectomes (FlyWire) have synapse weights spanning 3.4 orders of magnitude. The project's uniform rate model can't accommodate that range — no global weight normalization puts weak and strong synapses both in the tanh responsive band. The fix: give each neuron its own gain / threshold / time constant (homeostatic-style), so every neuron operates in its responsive range regardless of total synaptic drive — as real neurons do. Then re-test the scan-inverse protocol on FlyWire. Until this is done, the real-connectome capability of the protocol is genuinely unestablished. The scan-inverse protocol itself (pool stim, coverage rule, mixed amplitudes, strong-ridge) is sound — demonstrated on C. elegans at Pearson 0.99 — and likely transfers once the model accommodates real weight statistics.
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
- `math/direction1_hub_neuron_concern.md` — hub d_eff measurements (low d_eff confirmed)
- `math/direction1_megahub_limitation.md` — **OPEN: N=2000 real-data FAIL; mega-hub multi-task reconstruction unsolved**
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

Hub-neuron analysis (added 2026-05-18):
- `run_hub_deff_flywire.py` — Drosophila hubs d_eff = 25 (n=200), 58 (n=1000)
- `run_celegans_hub_deff.py` — C. elegans command neurons d_eff = 3.72 with mean |supp|=45.6
- `run_multitask_pool_stim.py` — ALS multi-task synthetic (slow, marginal)
- `run_multitask_v2.py` — SVD-shrinkage post-processing (cleaner; strong-ridge alone gives r=0.31 at K=⅓·|supp|)

Body compression (added 2026-05-18):
- `run_body_compression.py` — theory R-D ~270 GB confirmed; gzip 68 TB (wrong codec)

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
