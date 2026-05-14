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
[![Papers](https://img.shields.io/badge/papers_collected-6-blueviolet)](#research-files)
[![Record](https://img.shields.io/badge/QT_record-1%2C400_km-blue)](#key-numbers)

**Physics-grounded teleportation research**

The goal is not a literature review. The goal is to actually find something — a mechanism, a reframing, or an approach that nobody has seriously mapped out — and build a simulation with testable predictions. Strict honesty required: if the answer is that it's impossible, that's the answer.

</div>

---

## Where the Conventional Approaches Die

| Approach | Status | Why It Actually Fails |
|----------|--------|-----------------------|
| **Full quantum state teleportation** | Demonstrated for particles | Decoherence + Heisenberg + bandwidth. All three simultaneously. Not an engineering problem. |
| **Traversable wormholes** | Valid GR math | Ford-Roman quantum inequalities: negative energy density is bounded too tightly by the vacuum itself. Not a materials problem. |
| **Alcubierre warp drive** | Valid GR math | Same exotic matter wall. White's 2012 reduction still requires Jupiter-mass negative energy. |
| **ER = EPR wormholes** | Theoretical conjecture | The implied wormholes are Planck-scale and non-traversable. ER=EPR preserves causality explicitly. |
| **Psychic / remote teleportation** | Pseudoscience | No replicated evidence under controlled conditions. Full stop. |

## The Alleyways Nobody Has Mapped

These are the directions that don't appear in mainstream teleportation research — not because they've been ruled out, but because nobody has done the work. Some may be dead ends. We won't know until we run the math.

**1. Reframing the information requirement**
Every mainstream approach assumes you need to copy the *quantum state* of every particle (~10²⁸ bits). But what you actually need for functional equivalence is probably the connectome + molecular composition (~10¹⁵ bits of *classical* data). The quantum barriers vanish entirely at that level. Nobody has built a rigorous information-theoretic model of the minimum copy required for functional teleportation. This is the most honest near-term path and the least explored.

**2. Center-of-mass tunneling of macroscopic bound states**
Superconductors and BECs already exhibit macroscopic quantum tunneling. Levitated nanoparticle experiments (Delord et al. 2021, Pontin et al. 2023) have placed ~10⁷-atom objects into quantum superpositions of center-of-mass motion. A composite bound state tunnels as a unit — the relevant wavefunction is the center-of-mass, not 10⁷ individual particles. The scaling math for this process hasn't been done rigorously as a function of object mass, internal temperature, and barrier geometry.

**3. Quantum Cheshire Cat / post-selection**
Denkmayr et al. (2014, *Nature Communications*) experimentally demonstrated a neutron's spin appearing in a different arm than the neutron itself. A particle property was physically separated from the particle. This is not an interpretation artifact — it's measured. Nobody has asked whether this effect scales, whether it can be applied to properties other than spin, or whether it constitutes a physically meaningful form of property transport. Mostly dismissed. May not be.

**4. Gravitational decoherence threshold (Penrose-Diósi)**
The Penrose-Diósi objective collapse model predicts wavefunction collapse driven by gravitational self-energy, with a timescale τ ≈ ℏ/E_G where E_G is the gravitational self-energy difference between superposition branches. This sets a hard, calculable mass limit for quantum superposition — and therefore for quantum teleportation. Whether the model is right or wrong matters enormously for this project. Experiments (AION, MAGIS, levitated particle interferometry) are testing this now, but the teleportation-specific predictions haven't been extracted.

**5. Quantum Darwinism reconstruction**
Zurek's quantum Darwinism framework establishes that the environment continuously records classical "pointer state" snapshots of every object via redundant environmental imprinting (photons, air molecules, thermal radiation). That information exists, distributed, in principle recoverable. A proper information-theoretic analysis of what fraction is recoverable, at what fidelity, and whether it's sufficient for functional reconstruction has never been done. The framework exists; the teleportation application doesn't.

---

## Key Numbers

| Quantity | Value | Source |
|----------|-------|--------|
| Human body atom count | ~7 × 10²⁷ | — |
| Quantum state info content | ~10²⁸–10³² bits | Scaling estimate |
| Rest-mass energy of 70 kg human | ~6.3 × 10¹⁸ J | E = mc² |
| Wormhole exotic matter (1 m throat) | ~−2 × 10²⁷ kg | Visser 1989–1995 |
| Alcubierre exotic matter (original) | ~−10⁶⁴ kg | Alcubierre 1994 |
| Casimir effect density (1 μm plates) | ~−1.3 × 10⁻³ J/m³ | 38 orders too small for wormholes |
| Decoherence time (macro body, 300 K) | ~10⁻²³ s | Thermal decoherence estimate |
| QT record distance | 1,400 km | Pan et al., Nature 2017 |
| QT fidelity (Northwestern 2024) | ~90% | Over live 400 Gbps internet traffic |

---

## Research Files

### Government & Intelligence Documents
- [`research/government_docs.md`](research/government_docs.md) — CIA STARGATE program, DIA DIRD #18 (Davis 2010), AFRL Teleportation Physics Study (Davis 2004)

### Science Reviews
- [`research/quantum_teleportation_state_of_science.md`](research/quantum_teleportation_state_of_science.md) — experimental milestones 1997–2025, fundamental limits, scaling analysis
- [`research/theoretical_frameworks.md`](research/theoretical_frameworks.md) — wormholes, ER=EPR, warp drive, GR constraints, energy budget table

### Papers
| File | Paper |
|------|-------|
| [`bennett_1993_quantum_teleportation.md`](research/papers/bennett_1993_quantum_teleportation.md) | Bennett et al. (1993) — original QT protocol, full equations |
| [`pan_etal_2017_ground_to_satellite.md`](research/papers/pan_etal_2017_ground_to_satellite.md) | Pan et al. (2017) — 1,400 km Micius satellite record |
| [`alcubierre_1994_warp_drive.md`](research/papers/alcubierre_1994_warp_drive.md) | Alcubierre (1994) — warp drive metric, exotic matter estimates |
| [`maldacena_susskind_2013_ER_EPR.md`](research/papers/maldacena_susskind_2013_ER_EPR.md) | Maldacena & Susskind (2013) — ER = EPR conjecture |
| [`visser_kar_dadhich_2003_small_exotic_matter.md`](research/papers/visser_kar_dadhich_2003_small_exotic_matter.md) | Visser, Kar & Dadhich (2003) — arbitrarily small exotic matter result |
| [`ford_roman_1999_quantum_interest.md`](research/papers/ford_roman_1999_quantum_interest.md) | Ford & Roman (1999) — quantum interest conjecture, negative energy limits |

### In Progress
- [`math/`](math/) — energy budget calculations, decoherence bounds, wormhole geometry
- [`architecture/`](architecture/) — conceptual teleporter design docs

---

## What Physics Actually Forbids (and What It Doesn't)

**Hard limits from established physics:**
- No-cloning theorem: cannot copy an unknown quantum state
- No-communication theorem: quantum entanglement cannot transmit information FTL
- Ford-Roman quantum inequalities: negative energy density is bounded — you cannot sustain exotic matter at macroscopic scales
- Heisenberg: a complete quantum scan of a body requires destroying or disturbing it

**What GR does NOT forbid (mathematically):**
- Traversable wormholes (Morris & Thorne 1988)
- Alcubierre warp drive metric (1994)
- Closed timelike curves

The gap between "mathematically permitted solution to Einstein's equations" and "physically constructible object" is where all the action is.

---

*Working assumptions: Standard Model + GR as baseline. All extensions (string theory, extra dimensions) labeled speculative. All calculations shown with units and sources.*
