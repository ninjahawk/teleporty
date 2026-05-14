# Quantum Teleportation — State of the Science

## What It Actually Is
Quantum teleportation transfers the *quantum state* of a particle — not the particle itself, not matter, not energy — to another particle at a remote location. The remote particle then "becomes" the original state. The original is destroyed in the process (required by the no-cloning theorem).

**Foundational paper:** Bennett, C.H., Brassard, G., Crépeau, C., Jozsa, R., Peres, A., & Wootters, W.K. (1993). "Teleporting an Unknown Quantum State via Dual Classical and Einstein–Podolsky–Rosen Channels." *Physical Review Letters*, 70(13), 1895–1899. DOI: 10.1103/PhysRevLett.70.1895

**Protocol requires three resources:**
1. Pre-shared entangled pair (the EPR channel)
2. Bell-state measurement by sender
3. Classical communication channel — sender transmits 2 classical bits to receiver, who applies unitary correction

**The classical channel means teleportation cannot exceed the speed of light.**

---

## Experimental Milestones

| Year | Achievement | System | Group |
|------|-------------|--------|-------|
| 1997 | First experimental demo | Photon polarization states | Bouwmeester, Pan, Zeilinger et al. — *Nature* 390, 575 |
| 1998 | Independent confirmation | Photons | Boschi et al. (Rome) |
| 2004 | First atomic-scale teleportation | Beryllium ions | NIST (Wineland) + U. Innsbruck (Blatt), independently |
| 2004 | 600 m over optical fiber | Photons | Zeilinger group, across Danube River, Vienna |
| 2008 | Atoms in separate enclosures, 1 m | Ytterbium ions | U. Maryland |
| 2012 | Free-space record: 143 km | Photons | Zeilinger group, Canary Islands |
| 2015 | Multiple degrees of freedom simultaneously | Photons + Rb ensemble | Jian-Wei Pan, USTC |
| 2017 | **Ground-to-satellite: 1,400 km** (current distance record) | Photons (Micius satellite) | Pan, USTC — *Nature* 549, 70 |
| 2020 | 44 km over deployed fiber, >90% fidelity | Photons | INQNET (Fermilab/Caltech) |
| 2024 | Over live 400 Gbps internet traffic, 30.2 km | Photons (O-band, 1310 nm) | Northwestern (Kanter) — *Optica* |
| 2025 | 94% fidelity via nanophotonic chip (InGaP) | Photons | U. Illinois Urbana-Champaign |

**Current distance record: 1,400 km** (Micius satellite, 2017)

---

## Fundamental Limits

### 1. No-Cloning Theorem (Wootters & Zurek 1982; Dieks 1982)
Cannot create a perfect independent copy of an unknown quantum state. This is why teleportation destroys the original — state is moved, not duplicated. Direct consequence of linearity of quantum mechanics.

### 2. No-Teleportation Theorem
Cannot convert an arbitrary quantum state into classical information and reconstruct it perfectly. Measurement collapses the state. Fundamental barrier to "scan and transmit" matter teleportation.

### 3. Classical Channel Requirement
Bell measurement result must be communicated classically before the receiver can apply correction. No FTL information transfer. Minimum transmission time = c-limited distance/speed.

### 4. Decoherence
Quantum states interacting with environment lose coherence on timescales that decrease with system complexity:
- Single atoms: microseconds to milliseconds (controlled)
- Biological macromolecules at room temperature: femtoseconds (~10⁻¹⁵ s)
- Human-scale objects at room temperature: ~10⁻²³ s or less

Maintaining quantum coherence across ~10²⁸ particles in a human body is not an engineering challenge — it is a fundamental physical incompatibility with thermal environment.

### 5. Fidelity Threshold
Classical communication alone achieves max average fidelity of 2/3 for quantum state transfer. Demonstrations above 2/3 fidelity confirm genuine quantum teleportation.

---

## Scaling to Macroscopic Objects

**Information content of a human body:**
- ~7 × 10²⁷ atoms
- Full quantum state characterization: ~10²⁸–10³² bits
- At 30 GHz bandwidth: transmission time ≈ 4.85 × 10¹⁵ years (~350,000× age of universe)

**Heisenberg barrier:** Simultaneous precise measurement of conjugate variables (position/momentum) is forbidden. A complete quantum scan either destroys the original or accepts irreducible uncertainty.

**Current "macroscopic" frontier:**
- 2016: Teleportation from light beams to vibrational states of macroscopic diamond, 90.6% fidelity (*Nature Communications* 7, 11736)
- 2024: Macroscopic quantum teleportation preprint (arXiv:2411.02968)
- Still at milligram-to-gram scale, not human scale

**Conclusion:** No physical law prohibits macroscopic quantum teleportation in principle. But exponential information scaling + decoherence + Heisenberg measurement problem make it astronomically far-off, not merely a near-term engineering challenge.
