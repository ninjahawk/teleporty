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

Nobody ruled these out. Nobody did the work. That's why we're here.

**🟢 Direction 1 — Reframe what you're actually copying** ← *active now*
Every approach assumes you need the quantum state of every particle (~10²⁸ bits). You don't. A person's functional identity is encoded in their connectome + biochemistry — classical information, ~10¹⁶ bits. The quantum barriers completely disappear. Nobody built the rigorous information model. We did: [→ math/direction1_functional_teleportation.md](math/direction1_functional_teleportation.md)

**🟡 Direction 2 — Center-of-mass tunneling of bound states**
Superconductors and BECs already exhibit macroscopic quantum tunneling. Levitated nanoparticle experiments have put 10⁷-atom objects into genuine spatial superpositions. The scaling math for composite objects with internal temperature hasn't been done. We're going to do it.

**🟡 Direction 3 — Quantum Cheshire Cat**
Denkmayr et al. (2014) experimentally separated a neutron's spin from the neutron itself. Verified. Measured. Nobody asked whether it scales or whether it constitutes a physically meaningful form of property transport. Probably a dead end but needs the math first.

**🟡 Direction 4 — Gravitational decoherence ceiling**
If the Penrose-Diósi model is correct, gravity collapses wavefunctions. That sets a hard calculable mass limit on all quantum approaches. If it's wrong, the ceiling is much higher. Experiments are live right now (AION, MAGIS-100). We need the teleportation-specific predictions extracted from the model.

**⚪ Direction 5 — Quantum Darwinism reconstruction**
Every object continuously broadcasts classical copies of its state into the environment via scattered photons and air molecule interactions. A proper analysis of how much is recoverable and at what fidelity has never been done. May feed into Direction 1.

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

10⁸ electron microscopes don't exist (there are ~10,000 in the world today). But **there is no physics that forbids building them**. This is a manufacturing and economics problem. The same way there were no transistors in 1940 and now there are 10²³.

**For a living scan** (non-destructive, nm resolution): doesn't exist yet. No known fundamental barrier to building one, but also no clear path. This is the hardest open engineering question in the project.

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

## 📂 Files

### Math & Calculations
| File | What's In It |
|------|-------------|
| [math/direction1_functional_teleportation.md](math/direction1_functional_teleportation.md) | Full information budget, transmission times, assembly energy, scanner analysis, identity discussion |

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

### In Progress
- `math/` — Direction 2 (CM tunneling), Direction 4 (Penrose-Diósi)
- `architecture/` — system design once a direction matures

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
