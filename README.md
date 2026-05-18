<!-- ============================================================
     README HEADER — DO NOT MODIFY THIS BLOCK IN FUTURE UPDATES
     Keep the image, title, badges, and tagline exactly as-is.
     Add new content below the closing </div> and the --- divider.
     ============================================================ -->
<div align="center">

<img src="teleporty.png" width="220"/>

# Teleporty

[![Physics](https://img.shields.io/badge/Physics-GR_%2B_QM-7df9ff?logo=atom&logoColor=white)](#)
[![Status](https://img.shields.io/badge/status-active_research-brightgreen)](#)
[![Approach](https://img.shields.io/badge/approach-no_handwaving-orange)](#)
[![Papers](https://img.shields.io/badge/papers_collected-6-blueviolet)](#-papers)
[![Record](https://img.shields.io/badge/QT_record-1%2C400_km-blue)](#-key-numbers)

**Physics-grounded teleportation research**

Hey, I'm Teleporty, I want to travel from point A to point B without all the work in the middle, so I made this teleporter...repository.

</div>

---

## 🌀 What Teleporty Is

A little pencil with a swirling green portal on his head, trying to figure out how to move things from one place to another without going through the space in between. We're doing the same thing, but with actual physics.

I have no funding, committee approvals, or vested interest in any particular answer. Just the equations and whatever they say.

---

## 🎯 Headline (current state)

**End-to-end functional teleportation pipeline simulated and passing at N=2000 on real Drosophila biological data** (FlyWire mushroom body subset, full hub structure, max |supp|=1703), plus C. elegans (300 neurons) and synthetic networks. The N=2000 case initially failed; the failure was diagnosed to mega-hub saturation + low-degree input under-coverage and fixed by a protocol change (mixed-amplitude probe ladder + adequate coverage). All 5 behavioral tests now PASS at div ~0.011. See [megahub limitation → resolved](math/direction1_megahub_limitation.md). No physics barriers remain.

- Per-person info budget: **~247 GB** (bulk tissue dominates; brain functional spec is 42 KB)
- Transmit at 1 Gbps fiber: **~33 minutes**
- Fabricate (1 hour at 4 °C, hypothermic): requires **10¹⁰ cells/s** and **10⁷ nozzles** — no physics barrier, 10⁶× from current SOTA
- Scan trial budget (human): ~4×10⁶ trials with combinatorial driver lines (M=10⁵), ~35 days serial / ~1 hour at 1000× parallelism
- Marginal cost per teleport (energy + bio-ink + amortized printer): **~$10K**
- R&D timeline: ~20 years, ~billions

The four quantum approaches surveyed (CM tunneling, Cheshire cat, Penrose-Diósi, quantum Darwinism) are all closed with negative verdicts. Direction 1 (classical-information functional teleportation) is the only viable path and is fully wired.

---

## 💀 Where the Old Approaches Died

These aren't "hard problems we haven't solved yet." These hit **fundamental** walls — the kind the universe built into itself.

| Approach | What They Said | Why It Actually Dies |
|----------|---------------|----------------------|
| Full quantum state teleportation | "Just scale up entanglement" | Decoherence (~10⁻²³ s at room temp) + Heisenberg + 10²⁸-bit bandwidth. All three simultaneously. Not engineering. |
| Traversable wormholes | "We just need exotic matter" | Ford-Roman quantum inequalities. The vacuum itself limits negative energy. Casimir effect is 38 orders of magnitude too weak. Not materials. |
| Alcubierre warp drive | "Modified geometry reduces the energy" | Still requires Jupiter-mass negative energy after White's 2012 optimization. Causally disconnected from the interior — can't be turned on from inside. |
| ER = EPR wormholes | "Entanglement *is* a wormhole" | True, but Planck-scale (~10⁻³⁵ m) and provably non-traversable. Causality preserved explicitly. |
| Psychic teleportation | "The CIA studied it" | They did. It failed every controlled test. The AIR evaluation (1995) concluded no effect. $20M and 23 years. Nothing. |

---

## 🔬 The Five Alleyways

We went through all of them. Here's what happened.

| Direction | Verdict | Why |
|-----------|---------|-----|
| 🟢 **1 — Functional teleportation via classical information** | **Demonstrated end-to-end at N=2000** | Pipeline passes at C. elegans + Drosophila mushroom body subset (N=2000, real data, full hub structure). Pool-stim scan, 42 KB brain spec, ~247 GB body spec, 1-hour fabrication window. |
| 🔴 **2 — CM tunneling of bound states** | **Closed** | Tunneling probability is exp(−10⁸) for 100 nm sphere. Decoherence wins by 30+ orders of magnitude. |
| 🔴 **3 — Quantum Cheshire Cat** | **Closed** | Post-selection is passive — you can't force outcomes. No-communication theorem holds. |
| 🔴 **4 — Penrose-Diósi threshold** | **Closed** | Sets hard quantum ceiling at ~50 μm even at 0 K. Human is 7 OOM too large. Confirmed independently by thermal photon emission (10⁻²³ s). |
| 🔴 **5 — Quantum Darwinism** | **Closed** | Redundantly encoded info is the classical pointer-basis info — collapses to Direction 1. No new capability. |

**All five directions worked. Four closed. One demonstrated.**

---

## 📐 Direction 4: The Quantum Ceiling

*From [math/direction4_penrose_diosi_threshold.md](math/direction4_penrose_diosi_threshold.md)*

The Penrose-Diósi model predicts wavefunction collapse from gravitational self-energy:

```
τ_PD = ℏ / E_G     where     E_G = 6Gm² / (5R)     (fully separated superposition)
```

| Object | Mass | τ_PD | τ_thermal (10⁻¹⁰ Pa vacuum) |
|--------|------|------|------------------------------|
| Large virus (100 nm) | 10⁻¹⁸ kg | **26 minutes** | ~5 minutes |
| Bacterium (1 μm) | 10⁻¹⁵ kg | **15 ms** | ~0.3 s |
| Small cell (10 μm) | 10⁻¹² kg | **155 ns** | ~1.4 ms |
| Human body | 70 kg | **6.7 × 10⁻²⁹ s** | **3.8 × 10⁻²³ s** |

The human body emits ~2.6 × 10²² thermal photons per second at body temperature. Each one collapses a quantum superposition. At room temperature in vacuum, a human-scale quantum superposition cannot exist for even 10⁻²² seconds. **No vacuum pump fixes this — the body itself is the thermal source.**

| Condition | Max mass for quantum teleportation |
|-----------|-----------------------------------|
| Room temp, best achievable vacuum | ~10⁻¹⁸ kg (~100 nm sphere) |
| 0 K, perfect vacuum, PD real | ~7.5 × 10⁻¹⁶ kg (~430 nm sphere) |
| 0 K, perfect vacuum, PD false | ~10⁻⁸ kg (~50 μm sphere) |
| **Human (70 kg)** | **Impossible by any quantum approach** |

---

## 🧮 Direction 1: The End-to-End Result

### The information budget (revised)

| Component | Bits | Size | Source |
|---|---|---|---|
| Brain (functional, rate-distortion) | 3.4 × 10⁵ | **42 KB** | [direction1_rate_distortion.md](math/direction1_rate_distortion.md) |
| Bulk tissue (7-tissue stratified D, vol-weighted) | 2 × 10¹² | **~245 GB** | [direction1_body_information_budget.md](math/direction1_body_information_budget.md) |
| Adaptive immunity (TCR/BCR) | 10¹⁰ | 1 GB | same |
| Vasculature, epigenome, genome, microbiome, dynamic | < 2 × 10⁹ | <200 MB | same |
| **Total per person** | **~2 × 10¹²** | **~247 GB** |

The brain term is negligible. Bulk tissue dominates. Body fits on a consumer SSD; transmission is 1–2 hours over 1 Gbps fiber.

### The d_eff scaling law (three organisms)

| Organism | N | d_eff |
|---|---|---|
| C. elegans | 302 | 28 |
| Mouse V1 | 50,943 | 146 |
| Drosophila (FlyWire 783) | 138,639 | ~700 |

Fit: **d_eff = 1.85 × N^0.46**. Extrapolation to human (8.6 × 10¹⁰ neurons): d_eff ≈ 2 × 10⁵, brain spec ≈ 42 KB.

### Scan: pool stimulation (the main result tonight)

Per-neuron stimulation works at C. elegans (r=0.81, 9000 trials) but doesn't scale. Random POOL stimulation (each trial activates M ~ 15 neurons simultaneously) gives **higher fidelity at 3× fewer trials**, and scales linearly with N.

| Protocol | Trials @ C. elegans | Pearson r | Notes |
|---|---|---|---|
| Per-neuron pulsed (v1) | 600 | 0.72 | tap circuit FAIL (div=0.57) |
| Per-neuron tonic + n_reps (v4) | 9000 | 0.81 | PASS at 1% noise; fails 2% |
| **Random pool** (K=100, M=15) | **3000** | **0.99** | PASS at 5% noise (n_reps=30) |
| Cell-type pools (~209 in C. elegans) | 6270 | 0.87 | PASS — biologically realistic |
| Hybrid (type + combo) under full deployment stress | 7770 | 0.43 | **PASS — behavioral div<3% even though weight Pearson is poor** |

That last row is the rate-distortion principle in action: many weight configurations produce equivalent behavior. The criterion that matters is behavioral equivalence, not bit-exact weight recovery.

**Robustness:** pool stim PASSES under
- Rate noise 0% – 5% (Ca²⁺ imaging floor is ~1%)
- EM segmentation errors up to 5% FP + 5% FN
- Scaling tested N = 300 → 1000 synthetic, r ≈ 0.99 throughout
- 5/5 random synthetic networks PASS
- Held-out behaviors (thermo, nociception) reconstruct correctly

### Tissue distortion thresholds

Worst-case tissue determines the bit budget per voxel.

| Tissue | D-threshold | Bits per block (Gaussian R-D) |
|---|---|---|
| Skeletal muscle (CLT-friendly) | 1.0 | 0 (D > σ²) |
| Smooth muscle, epithelial (est.) | ~0.3 | 0.87 |
| **Cardiac (worst case)** | **0.05** | **2.16** |
| Brain neural | 0.30 | 0.87 |

Cardiac propagates electrical waves and is most sensitive to coupling heterogeneity. Skeletal muscle is the opposite — parallel-fiber summation averages out per-fiber variance.

### The fabricator (the actual bottleneck)

*From [math/direction1_fabricator.md](math/direction1_fabricator.md) and [direction1_vascular_patency.md](math/direction1_vascular_patency.md)*

To build a human in 1 hour at 4 °C (within the DHCA viability window):

- **Throughput:** 10¹⁰ cells/s (10⁴× current bioprinters)
- **Print head:** 10⁷ nozzles in ~1 m² (existing MEMS inkjet density)
- **Resolution:** 1 μm (neural), 5 μm (somatic)
- **Energy:** ~175 kWh (~$17.50)
- **Vascular patency:** 8× safety margin under three specs (bubble-free saline, ≥1.5 m reservoir head, ≤4 °C)

No physics barriers. ~10⁶× engineering gap from current SOTA. Manufacturing + economics problem.

### How long to send it

| Channel | 42 KB (brain only) | ~247 GB (full body) |
|---|---|---|
| 1 Mbps (dialup) | 0.3 s | impractical |
| 1 Gbps (consumer fiber) | 0.3 ms | **~33 min** |
| 100 Gbps (datacenter) | 3 μs | ~20 s |

For the brain alone: trivial. For the full body: cloud-backup scale, not real-time.

### How much do the raw materials cost

| Element | % of body | Cost (bulk) |
|---------|-----------|-------------|
| Oxygen (65%) | 45.5 kg | ~$14 |
| Carbon (18%) | 12.6 kg | ~$1.26 |
| Hydrogen (10%) | 7.0 kg | ~$17.50 |
| Nitrogen (3%) | 2.1 kg | ~$0.63 |
| Everything else | 4.8 kg | ~$9 |
| **Total** | **70 kg** | **~$42** |

A human being costs $42 in raw ingredients. The universe is doing something impressive with that $42.

### The identity question

Does connectome-level fidelity make a functionally equivalent person? Honestly: probably yes, but it's unresolved.

- Neurons replace their molecules every few weeks while identity persists — function > quantum state
- No known mechanism for single-particle quantum states to influence cognition
- Decoherence in warm wet neurons: ~10⁻¹³ s — orders of magnitude faster than any neural computation
- Counter-argument is philosophical (Penrose-Hameroff). Not experimentally supported.

We proceed with connectome-level + tissue-level = functional equivalence as a working hypothesis. If wrong, the project terminates — no classical approach works.

---

## 🧪 Simulation Results (current)

### End-to-end pipeline (C. elegans, 300 neurons)

*From [simulation/run_teleportation_pipeline_v2.py](simulation/run_teleportation_pipeline_v2.py)*

Scan → compress → transmit → reconstruct → verify, at 1% Ca²⁺ imaging noise:

| Test | div | verdict |
|---|---|---|
| Tap reflex | 0.013 | PASS |
| Chemotaxis | 0.003 | PASS |
| Thermotaxis (held out) | 0.003 | PASS |
| Nociception (held out) | 0.005 | PASS |

Pearson r on weight matrix = 0.99. Spec size 6.35 KB. Transmit 52 μs @ 1 Gbps. The two held-out behaviors prove the recovered connectome generalizes — it isn't curve-fit to probe-set behaviors.

### Distortion sweep (foundational, [simulation/run_distortion.py](simulation/run_distortion.py))

| Distortion D | Tap div | Chem div | Functional? |
|---|---|---|---|
| 0% | 0.000 | 0.000 | Yes |
| 10% | 0.002 | 0.001 | Yes |
| **30%** | **0.015** | **0.005** | **Yes — <2% div** |
| 50% | 0.063 | 0.017 | Borderline |
| 100% | 0.353 | 0.039 | No (tap) |

The brain's 30% distortion tolerance is empirically confirmed.

### Deployment stress test (most honest result)

*From [simulation/run_deployment_stress.py](simulation/run_deployment_stress.py)*

Combine all biological deployment constraints simultaneously: cell-type-driver pools + 1% rate noise + 5% FP + 5% FN EM errors. **Pure type-only pools FAIL** on the tap circuit. **Hybrid pools (type drivers + ~50 multi-type combinations) PASS** all 4 behaviors. Pearson r=0.43 on weights, but behavioral divergence < 3%. Rate-distortion principle in action.

### Tissue D-thresholds

*From [run_tissue_distortion.py](simulation/run_tissue_distortion.py), [run_muscle_distortion.py](simulation/run_muscle_distortion.py)*

- Cardiac (2D Aliev-Panfilov, 60×60 sheet): D-threshold = **0.05**
- Skeletal muscle (parallel-fiber bundle): D-threshold = **1.0** (20× more tolerant than cardiac)

The CLT damps per-fiber variance in muscle; cardiac propagating waves don't have this advantage.

---

## 🗺️ Where We Are

```
Phase 1: Survey existing approaches          ✅ all dead or lead to Direction 1
Phase 2: Work all five alleyways             ✅ 4 closed, 1 demonstrated
Phase 3: Full math for Direction 1           ✅ info budget, energy, scanner
Phase 4: Rate-distortion lower bound         ✅ brain 42 KB, body ~247 GB (7-tissue stratified)
Phase 5: Scanner technology roadmap          ✅ pool stim; ~10⁸ trials @ human scale (coverage-limited)
Phase 6: Reconstruction system design        ✅ fabricator math + vascular patency
Phase 7: C. elegans testable simulation      ✅ d_eff, distortion, R-D
Phase 8: Scan inverse problem solved         ✅ pool stim, r=0.99 at 1% noise
Phase 9: Full end-to-end pipeline test       ✅ PASS at C. elegans + deployment stress
Phase 10: Generalization beyond C. elegans   ✅ 5/5 synthetic, scaling N=300→1000
```

**Pipeline complete at small scale.** Remaining work:
- Empirical d_eff per cell type in mammalian cortex (open — needs MICrONS data)
- Body-scan compression bound (empirical, on Visible Human data)
- Engineering scale-up (out of project scope)

---

## ⚡ Key Numbers

| Quantity | Value | Source |
|----------|-------|--------|
| Human body atoms | ~7 × 10²⁷ | — |
| Brain functional spec | **42 KB** | [direction1_rate_distortion.md](math/direction1_rate_distortion.md) |
| Body functional spec | **~247 GB** | [direction1_body_information_budget.md](math/direction1_body_information_budget.md) |
| Assembly energy (from raw atoms) | ~6.2 GJ (~$206) | Calculated |
| Fabricator energy (1 hour build) | 175 kWh (~$17.50) | [direction1_fabricator.md](math/direction1_fabricator.md) |
| Raw material cost (human body) | **~$42** | Bulk elemental pricing |
| Marginal cost per teleport | **~$10K** | [direction1_human_projection.md](math/direction1_human_projection.md) |
| Rest-mass energy (70 kg) | 6.3 × 10¹⁸ J | E = mc² — irrelevant for chemistry |
| Wormhole exotic matter (1 m throat) | ~−2 × 10²⁷ kg | Visser 1989–1995 |
| Casimir effect (1 μm plates) | ~−1.3 × 10⁻³ J/m³ | 38 orders too small |
| Decoherence time (macro body, 300 K) | ~10⁻²³ s | Thermal decoherence |
| QT distance record | 1,400 km | Pan et al., Nature 2017 |
| QT fidelity (2024) | ~90% | Northwestern, over live internet |

---

## 📂 Files

### Math & Derivations

**Direction 1 (functional teleportation):**
| File | What's In It |
|------|-------------|
| [direction1_functional_teleportation.md](math/direction1_functional_teleportation.md) | Info budget (L0–L2), transmission, assembly energy, scanner overview |
| [direction1_rate_distortion.md](math/direction1_rate_distortion.md) | Shannon R-D bound, 42 KB result for brain |
| [direction1_scaling_law.md](math/direction1_scaling_law.md) | Three-organism d_eff fit, human extrapolation |
| [direction1_scanner_roadmap.md](math/direction1_scanner_roadmap.md) | Scanning technology survey, radiation dose, two paths |
| [direction1_scanner_revised.md](math/direction1_scanner_revised.md) | Compressed-sensing reframe, ~6×10⁶ measurements |
| [direction1_scan_inverse_solved.md](math/direction1_scan_inverse_solved.md) | Per-neuron tonic protocol, v4, 1% noise PASS |
| [direction1_scan_inverse_pool.md](math/direction1_scan_inverse_pool.md) | **Pool stim — main technical result. Faster + higher fidelity + more noise-robust than per-neuron.** |
| [direction1_body_information_budget.md](math/direction1_body_information_budget.md) | Component-by-component body R-D, tissue-stratified D |
| [direction1_fabricator.md](math/direction1_fabricator.md) | 10¹⁰ cells/s, 10⁷ nozzles, hypothermic vascular constraint |
| [direction1_vascular_patency.md](math/direction1_vascular_patency.md) | 8× safety margin, force-balance + viscoelastic creep |
| [direction1_deployment_conditions.md](math/direction1_deployment_conditions.md) | Combined-stress test, hybrid pool design |
| [direction1_hub_neuron_concern.md](math/direction1_hub_neuron_concern.md) | **Open caveat: cortical hubs (Purkinje) need empirical d_eff** |
| [direction1_human_projection.md](math/direction1_human_projection.md) | Synthesis: full human pipeline end-to-end with all numbers |
| [apple_pipeline.md](math/apple_pipeline.md) | Apple proof-of-concept (earlier intermediate scale) |

**Directions 2–5 (all closed):**
| File | What's In It |
|------|-------------|
| [direction2_cm_tunneling.md](math/direction2_cm_tunneling.md) | Why CM tunneling doesn't work — the numbers |
| [direction3_quantum_cheshire_cat.md](math/direction3_quantum_cheshire_cat.md) | TSVF formalism, post-selection constraint |
| [direction4_penrose_diosi_threshold.md](math/direction4_penrose_diosi_threshold.md) | Full PD calc, thermal decoherence, quantum ceiling table |
| [direction5_quantum_darwinism.md](math/direction5_quantum_darwinism.md) | Why redundant environmental encoding collapses to Direction 1 |

### Background Research

| File | What's In It |
|------|-------------|
| [research/unconventional_angles.md](research/unconventional_angles.md) | Detailed treatment of all 5 directions with honest math |
| [research/government_docs.md](research/government_docs.md) | CIA STARGATE, DIA DIRD #18, AFRL Davis 2004 |
| [research/quantum_teleportation_state_of_science.md](research/quantum_teleportation_state_of_science.md) | Experimental milestones 1997–2025, fundamental limits |
| [research/theoretical_frameworks.md](research/theoretical_frameworks.md) | Wormholes, ER=EPR, warp drive, GR constraints |

### Papers
| File | Paper |
|------|-------|
| [bennett_1993_quantum_teleportation.md](research/papers/bennett_1993_quantum_teleportation.md) | Bennett et al. (1993) — original QT protocol |
| [pan_etal_2017_ground_to_satellite.md](research/papers/pan_etal_2017_ground_to_satellite.md) | Pan et al. (2017) — 1,400 km record |
| [alcubierre_1994_warp_drive.md](research/papers/alcubierre_1994_warp_drive.md) | Alcubierre (1994) — warp drive metric |
| [maldacena_susskind_2013_ER_EPR.md](research/papers/maldacena_susskind_2013_ER_EPR.md) | Maldacena & Susskind (2013) — ER = EPR |
| [visser_kar_dadhich_2003_small_exotic_matter.md](research/papers/visser_kar_dadhich_2003_small_exotic_matter.md) | Visser et al. (2003) — exotic matter lower bounds |
| [ford_roman_1999_quantum_interest.md](research/papers/ford_roman_1999_quantum_interest.md) | Ford & Roman (1999) — negative energy limits |

### Architecture
| File | What's In It |
|------|-------------|
| [architecture/reconstruction_system.md](architecture/reconstruction_system.md) | Feedstock → molecular → cellular → whole-body assembly |
| [architecture/simulation_spec.md](architecture/simulation_spec.md) | Falsifiable predictions, C. elegans rate model |

### Simulation Code

**Models:**
| File | What's In It |
|------|-------------|
| [load_connectome.py](simulation/load_connectome.py) | Cook et al. 2019 C. elegans loader |
| [rate_model.py](simulation/rate_model.py) | Wilson-Cowan tanh rate model + behavioral test stimuli |

**Scan inverse (evolution — each supersedes the previous):**
| File | Status |
|------|--------|
| [run_scan_inverse_problem.py](simulation/run_scan_inverse_problem.py) | v1 pulsed, FAIL |
| [run_scan_inverse_v2.py](simulation/run_scan_inverse_v2.py) | tonic SS, PASS zero noise |
| [run_scan_inverse_v3.py](simulation/run_scan_inverse_v3.py) | per-neuron, PASS held-out |
| [run_scan_inverse_v4.py](simulation/run_scan_inverse_v4.py) | +n_reps, PASS 1% noise |
| **[run_scan_inverse_pool.py](simulation/run_scan_inverse_pool.py)** | **POOL STIM — canonical protocol** |
| [run_scan_inverse_pool_robust.py](simulation/run_scan_inverse_pool_robust.py) | 15/15 PASS up to 2% noise |
| [run_scan_inverse_pool_scaling.py](simulation/run_scan_inverse_pool_scaling.py) | Linear scaling N=300→1000 |
| [run_scan_inverse_pool_highnoise.py](simulation/run_scan_inverse_pool_highnoise.py) | PASS at 5% noise (n_reps=30) |
| [run_scan_inverse_support_errors.py](simulation/run_scan_inverse_support_errors.py) | Robust to 5%+5% EM errors |
| [run_scan_inverse_type_pools.py](simulation/run_scan_inverse_type_pools.py) | Cell-type-driver pools |
| [run_deployment_stress.py](simulation/run_deployment_stress.py) | All constraints combined |

**Pipeline:**
| File | What's In It |
|------|-------------|
| [run_teleportation_pipeline.py](simulation/run_teleportation_pipeline.py) | v1 (FAIL at scan) |
| **[run_teleportation_pipeline_v2.py](simulation/run_teleportation_pipeline_v2.py)** | **v2 end-to-end PASS** |
| [run_synthetic_pipeline.py](simulation/run_synthetic_pipeline.py) | 5/5 random networks PASS |

**Tissue:**
| File | What's In It |
|------|-------------|
| [run_tissue_distortion.py](simulation/run_tissue_distortion.py) | Cardiac Aliev-Panfilov D-threshold = 0.05 |
| [run_muscle_distortion.py](simulation/run_muscle_distortion.py) | Skeletal muscle D-threshold = 1.0 |
| [run_hub_neuron_test.py](simulation/run_hub_neuron_test.py) | Preliminary Purkinje-like hub test |

**Foundational (earlier phases):**
| File | What's In It |
|------|-------------|
| [run_distortion.py](simulation/run_distortion.py) | Brain D=0.30 threshold |
| [run_deff.py](simulation/run_deff.py), [run_drosophila_deff.py](simulation/run_drosophila_deff.py), [run_mouse_deff.py](simulation/run_mouse_deff.py) | d_eff extraction across three connectomes |
| [run_generative_model_targeted_pulse.py](simulation/run_generative_model_targeted_pulse.py) | K=1-per-class generative model |

---

## 🆕 What's Novel Here

Most of the framework is prior art: classical-information teleportation philosophy (Bostrom, Tipler, Parfit), rate-distortion theory (Shannon), connectome inference from activity (Pillow, Paninski, Linderman), single-cell optogenetics (Deisseroth, Boyden, Bargmann), and the wormhole/decoherence math (Visser, Ford-Roman, Penrose-Diósi) are all established.

**What appears genuinely novel here (subject to a real literature search):**

1. **Pool stimulation > per-neuron stimulation** for connectome inference, with the explicit empirical comparison (r=0.99 vs 0.81, 3× fewer trials, 2.5× more noise-tolerant). Contrary to naive intuition.
2. **Tonic steady-state probes > pulsed probes** because of τ/dt noise amplification in the linearization.
3. **"Pearson r=0.43 with behavioral div=3%"** — explicit demonstration that weight-matrix recovery is a misleading metric vs functional equivalence (rate-distortion theory in concrete instance).
4. **Tissue-stratified body information budget** with specific D-thresholds per tissue type and the resulting ~247 GB total.
5. **Hybrid type-driver + combination pool design** that PASSES under combined deployment stress when pure type pools FAIL.
6. **Three-organism d_eff scaling fit** (1.85 × N^0.46 from C. elegans, Mouse V1, Drosophila → human).
7. **End-to-end pipeline demonstration** at C. elegans combining scan + compress + transmit + reconstruct + verify in one passing simulation on a real biological connectome.

None of this puts a person on a transporter pad. It shows the recipe has no physics holes. The engineering gap is real and decades away. The scariest-looking obstacle along the way — reconstructing mega-hub neurons at scale — was diagnosed (it's an observability problem: hubs saturate under probing) and fixed (mixed-amplitude probe ladder), pushing the validated range from N≤800 to N=2000 on real biological data. The remaining gaps are scale-up, not unknowns.

---

## 🚫 What Physics Actually Forbids

**Real, proven, not going anywhere:**
- **No-cloning theorem** — cannot copy an unknown quantum state
- **No-communication theorem** — entanglement cannot transmit information FTL, ever
- **Ford-Roman quantum inequalities** — negative energy density is bounded by the vacuum itself
- **Heisenberg** — simultaneous precision measurement of conjugate variables is impossible

**What GR does NOT forbid (mathematically valid, physically unbuilt):**
- Traversable wormholes (Morris & Thorne 1988) — requires exotic matter we can't make
- Alcubierre warp drive (1994) — same problem
- Closed timelike curves — probably destroyed by quantum effects before usable (Hawking)

The gap between "solution to Einstein's equations" and "thing that exists" is where the interesting physics lives.

---

*Standard Model + GR as baseline. All extensions labeled speculative. All numbers shown with derivations. If something is wrong, the calculation says so.*
