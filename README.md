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
| 🟢 **1 — Reframe the information requirement** | **Active** | Classical info approach. Quantum barriers gone. Real path. |
| 🔴 **2 — CM tunneling of bound states** | **Closed** | Tunneling probability is exp(−10⁸) for 100 nm sphere. Decoherence wins by 30+ orders of magnitude. |
| 🔴 **3 — Quantum Cheshire Cat** | **Closed** | Post-selection is passive — you can't force outcomes. No-communication theorem holds. |
| 🟡 **4 — Penrose-Diósi threshold** | **Calculated** | Sets hard ceiling for all quantum approaches. Confirms Direction 1. |
| ⚪ **5 — Quantum Darwinism** | **Feeds into 1** | Encodes pointer states only, not molecular structure. Narrows the info budget question. |

**All five directions have been worked.** Three are closed. One confirms the only viable path. One is that path.

---

## 📐 Direction 4: The Quantum Ceiling

*From [math/direction4_penrose_diosi_threshold.md](math/direction4_penrose_diosi_threshold.md)*

This was the most important calculation before committing to any quantum approach. The Penrose-Diósi model predicts wavefunction collapse from gravitational self-energy:

```
τ_PD = ℏ / E_G     where     E_G = 6Gm² / (5R)     (fully separated superposition)
```

| Object | Mass | τ_PD | τ_thermal (10⁻¹⁰ Pa vacuum) |
|--------|------|------|------------------------------|
| Large virus (100 nm) | 10⁻¹⁸ kg | **26 minutes** | ~5 minutes |
| Bacterium (1 μm) | 10⁻¹⁵ kg | **15 ms** | ~0.3 s |
| Small cell (10 μm) | 10⁻¹² kg | **155 ns** | ~1.4 ms |
| Human body | 70 kg | **6.7 × 10⁻²⁹ s** | **3.8 × 10⁻²³ s** |

The human body emits ~2.6 × 10²² thermal photons per second at body temperature. Each one collapses a quantum superposition. At room temperature in vacuum, a human-scale quantum superposition cannot exist for even 10⁻²² seconds. No vacuum pump fixes this — the body itself is the thermal source.

**The ceiling, regardless of Penrose-Diósi:**

| Condition | Max mass for quantum teleportation |
|-----------|-----------------------------------|
| Room temp, best achievable vacuum | ~10⁻¹⁸ kg (~100 nm sphere) |
| 0 K, perfect vacuum, PD real | ~7.5 × 10⁻¹⁶ kg (~430 nm sphere) |
| 0 K, perfect vacuum, PD false | ~10⁻⁸ kg (~50 μm sphere) |
| **Human (70 kg)** | **Impossible by any quantum approach** |

**This closes Directions 2 and 3, and confirms Direction 1 is the only viable path.**

---

## 🧮 Direction 1: What the Numbers Actually Say

*From [math/direction1_functional_teleportation.md](math/direction1_functional_teleportation.md)*

### The Information Budget

| What You're Copying | Bits | Bytes | Notes |
|--------------------|------|-------|-------|
| Connectome + cell map (L0) | **1.4 × 10¹⁶** | 1.75 PB | ~17 Libraries of Congress |
| Full molecular map (L1) | ~2 × 10²⁴ | 250 ZB | ~2.5× all data humanity has ever stored |
| Full atomic map, classical (L2) | ~8 × 10²⁹ | — | Unrealistic to transmit |

**The quantum information problem (~10²⁸ bits) just isn't the relevant problem once you drop the quantum requirement.**

### How Long to Send It

At L0 (1.75 petabytes = 1.4 × 10¹⁶ bits):

| Channel | Transfer Time |
|---------|--------------|
| 1 Tbps (near-term fiber) | **3.9 hours** |
| 330 Tbps (theoretical optical max) | **42 seconds** |
| 22.9 Pbps (2024 lab record, 1 km) | **0.6 milliseconds** |

Transmission is a near-solved problem at connectome level.

### How Much Energy to Reassemble

Building a human body from raw atoms, bond by bond:

```
E_assembly = 7×10²⁷ atoms × 1.5 bonds/atom × 3.7 eV/bond
           ≈ 6.2 GJ
           ≈ 1,720 kWh
           ≈ $206 at average US electricity prices
```

For comparison, the rest-mass energy (E = mc²) of a 70 kg person is 6.3 × 10¹⁸ J — **nine orders of magnitude more** than what assembly actually costs. The energy is not the problem.

### How Much Do the Raw Materials Cost

| Element | % of body | Cost (bulk) |
|---------|-----------|-------------|
| Oxygen (65%) | 45.5 kg | ~$14 |
| Carbon (18%) | 12.6 kg | ~$1.26 |
| Hydrogen (10%) | 7.0 kg | ~$17.50 |
| Nitrogen (3%) | 2.1 kg | ~$0.63 |
| Everything else | 4.8 kg | ~$9 |
| **Total** | **70 kg** | **~$42** |

A human being costs $42 in raw ingredients. The universe is doing something impressive with that $42.

### The Identity Question

Does connectome-level fidelity make a functionally equivalent person? Honestly: probably yes, but it's unresolved.

- Neurons replace their molecules every few weeks while identity persists — suggesting function > quantum state
- No known mechanism for single-particle quantum states to influence cognition
- Decoherence in warm wet neurons: ~10⁻¹³ s — orders of magnitude faster than any neural computation
- Counter-argument: philosophical (Penrose-Hameroff). Not supported by experimental evidence.

We proceed with connectome-level = functional equivalence as a working hypothesis. If this is wrong, the project terminates — no classical approach works. We'll say so if evidence changes.

### The Actual Bottleneck

It's not transmission. It's not energy. It's not materials.

**It's the scanner.**

The only existing technology that achieves nanometer resolution in biological tissue is electron microscopy — which requires the sample to be dead. The H01 project (Google/Harvard 2021) took **3 years** to scan 1 mm³ of human cortex. A full brain is ~1.2 × 10⁶ mm³.

```
Single EM setup: 3.6 million years
10⁶ parallel microscopes: 3.6 years
10⁷ parallel microscopes: 130 days  
10⁸ parallel microscopes: 13 days
```

10⁸ electron microscopes don't exist (~10,000 in the world today). But **there is no physics that forbids building them**. This is a manufacturing and economics problem.

### Two Paths Forward

*From [math/direction1_scanner_roadmap.md](math/direction1_scanner_roadmap.md)*

**Path A — Destructive (accept the original is destroyed):**  
Expansion microscopy at 10× + light-sheet imaging gets to ~25 nm effective resolution at ~10× the throughput of ssEM. With 10⁷ parallel setups (~$1T at current prices, ~$100B at scale): scan in ~13 days. Manufacturing problem. TRL 4–5.

**Path B — Two-tier non-destructive:**  
1. Full-brain functional imaging captures the d_eff-dimensional activity manifold (the "program" the brain runs). Current: ~10⁶ neurons. Required: ~10¹⁰–10¹¹.  
2. Small destructive EM calibration sample (~1 cm³) trains a generative model: activity → structural weights.  
3. Reconstruct full connectome from functional recording + generative model.

This is the only path that preserves the original. Physics allows live nm-resolution imaging with STED (~10–20 nm) — but current methods are too slow for whole-brain volume. The fundamental radiation dose barrier prevents live X-ray at nm resolution; light-based methods are exempt. TRL 2–3.

**The hard open question:** Building a device that records from ~10¹⁰–10¹¹ neurons simultaneously in a living human. No physics forbids it. No current technology achieves it.

---

## ⚡ Key Numbers

| Quantity | Value | Source |
|----------|-------|--------|
| Human body atoms | ~7 × 10²⁷ | — |
| Connectome information (L0) | ~1.4 × 10¹⁶ bits | Calculated — [Direction 1](math/direction1_functional_teleportation.md) |
| Molecular map information (L1) | ~2 × 10²⁴ bits | Calculated |
| Assembly energy (from raw atoms) | ~6.2 GJ (~$206) | Calculated |
| Raw material cost (human body) | **~$42** | Bulk elemental pricing |
| Rest-mass energy (70 kg) | 6.3 × 10¹⁸ J | E = mc² — irrelevant for chemistry |
| Wormhole exotic matter (1 m throat) | ~−2 × 10²⁷ kg | Visser 1989–1995 |
| Casimir effect (1 μm plates) | ~−1.3 × 10⁻³ J/m³ | 38 orders too small |
| Decoherence time (macro body, 300 K) | ~10⁻²³ s | Thermal decoherence |
| QT distance record | 1,400 km | Pan et al., Nature 2017 |
| QT fidelity (2024) | ~90% | Northwestern, over live internet |

---

---

## 🗺️ Where We Are

```
Phase 1: Survey existing approaches          ✅ done — all dead or lead to Direction 1
Phase 2: Work all five alleyways             ✅ done — 3 closed, 1 active, 1 feeds in
Phase 3: Full math for Direction 1           ✅ done — info budget, energy, scanner analysis
Phase 4: Rate-distortion lower bound         ✅ done — minimum 10¹²–10¹³ bits vs naive 10¹⁶
Phase 5: Scanner technology roadmap          ✅ done — bottleneck is manufacturing, not physics
Phase 6: Reconstruction system design        ✅ done — no physics barriers, C. elegans test is MVP
Phase 7: Testable simulation                 ← next — end goal
```

---

## 📂 Files

### Math & Calculations
| File | Status | What's In It |
|------|--------|-------------|
| [math/direction1_functional_teleportation.md](math/direction1_functional_teleportation.md) | ✅ Done | Info budget (L0–L2), transmission times, assembly energy, scanner analysis |
| [math/direction4_penrose_diosi_threshold.md](math/direction4_penrose_diosi_threshold.md) | ✅ Done | Full PD calculation, thermal decoherence, quantum ceiling table |
| [math/direction2_cm_tunneling.md](math/direction2_cm_tunneling.md) | ✅ Closed | Why CM tunneling doesn't work — the numbers |
| [math/direction3_quantum_cheshire_cat.md](math/direction3_quantum_cheshire_cat.md) | ✅ Closed | TSVF formalism, post-selection constraint, why it can't transport anything |
| [math/direction1_rate_distortion.md](math/direction1_rate_distortion.md) | ✅ Done | Shannon R-D bound: minimum 10¹²–10¹³ bits, d_eff analysis, compressed sensing argument |
| [math/direction1_scanner_roadmap.md](math/direction1_scanner_roadmap.md) | ✅ Done | All scanning technologies, radiation dose barrier, two viable paths, technology timeline |

### Background Research
| File | What's In It |
|------|-------------|
| [research/unconventional_angles.md](research/unconventional_angles.md) | Detailed treatment of all 5 directions with honest math assessments |
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
| File | Status | What's In It |
|------|--------|-------------|
| [architecture/reconstruction_system.md](architecture/reconstruction_system.md) | ✅ Done | Feedstock → molecular → cellular → whole-body assembly. Critical path: synapse-level weight convergence. MVP: C. elegans test. |

---

## 🚫 What Physics Actually Forbids

**These are real, proven, not going anywhere:**
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
