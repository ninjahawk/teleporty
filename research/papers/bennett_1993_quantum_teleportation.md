# Teleporting an Unknown Quantum State via Dual Classical and EPR Channels

**Authors:** Charles H. Bennett, Gilles Brassard, Claude Crépeau, Richard Jozsa, Asher Peres, William K. Wootters  
**Year:** 1993  
**Published:** Physical Review Letters, 70(13), 1895–1899 (March 29, 1993)  
**DOI:** 10.1103/PhysRevLett.70.1895  
**Note:** Predates arXiv widespread use; no arXiv preprint. Available via APS.

---

## Abstract
Introduces a protocol to transfer an unknown quantum state from one location to another using a pre-shared entangled pair and two classical bits of communication, destroying the original state in the process. This is "quantum teleportation."

---

## The Protocol

### Resources Required
1. **An unknown qubit** |ψ⟩ = α|0⟩ + β|1⟩ at Alice's location (state to be teleported)
2. **A Bell pair** (EPR pair) shared between Alice and Bob, e.g., |Φ⁺⟩ = (1/√2)(|00⟩ + |11⟩)
3. **A classical communication channel** (phone, radio, etc.) — takes c-limited time

### Steps

**Step 1:** Alice holds qubit 1 (the unknown state |ψ⟩) and qubit 2 (her half of the Bell pair). Bob holds qubit 3 (his half of the Bell pair).

Total 3-qubit state:
```
|ψ⟩₁ ⊗ |Φ⁺⟩₂₃ = (α|0⟩₁ + β|1⟩₁) ⊗ (1/√2)(|00⟩₂₃ + |11⟩₂₃)
```

**Step 2:** Alice performs a Bell basis measurement on qubits 1 and 2. This projects them into one of four Bell states. The 4 possible outcomes and their probabilities are each 1/4.

**Step 3:** Depending on Alice's measurement outcome (2 classical bits: 00, 01, 10, or 11), Bob's qubit 3 is left in one of four states:
- `00` → Bob has α|0⟩ + β|1⟩ = |ψ⟩ (no correction needed)
- `01` → Bob has α|1⟩ + β|0⟩ (apply Pauli X)
- `10` → Bob has α|0⟩ − β|1⟩ (apply Pauli Z)
- `11` → Bob has α|1⟩ − β|0⟩ (apply Pauli X then Z)

**Step 4:** Alice sends her 2 classical bits to Bob.

**Step 5:** Bob applies the appropriate Pauli correction, obtaining |ψ⟩ exactly.

### Result
Bob's qubit is now in exactly the state |ψ⟩. Alice's qubit is destroyed (collapsed by the Bell measurement). The state is teleported, not copied. Neither Alice nor Bob ever learns α or β.

---

## Key Properties

| Property | Value |
|----------|-------|
| Classical bits needed | Exactly 2 |
| Entangled pairs consumed | 1 Bell pair per qubit teleported |
| Original state preserved? | **No** — destroyed by Bell measurement |
| FTL communication? | **No** — classical channel required; limited to c |
| Information leaked? | No — Alice learns nothing about α, β |
| Fidelity | Perfect (F = 1) for ideal implementation |
| Classical-only fidelity threshold | 2/3 — experiments above this confirm quantum protocol |

---

## What Is and Isn't Teleported

**What IS teleported:** The quantum state (the information encoded in α and β). After teleportation, Bob's particle behaves exactly as Alice's original would have.

**What is NOT teleported:**
- The physical particle itself — Bob's particle was there all along (his half of the Bell pair)
- Matter or energy
- Faster-than-light information (the 2 classical bits travel at ≤ c)

---

## Importance

This paper launched the field of quantum information science and quantum communication. It proved that:
1. Quantum states can be transmitted without physically moving the particle
2. Entanglement is a resource that can be "consumed" to transmit quantum information
3. The no-cloning theorem is respected (original is destroyed)
4. Quantum mechanics allows a new type of communication channel (the "quantum teleportation channel")

---

## Path to Matter Teleportation?

The Bennett protocol teleports *quantum states*, not matter. To teleport a physical object, you would need:
1. A complete quantum state description of every particle in the object (~10²⁸ qubits for a human)
2. One Bell pair per qubit (~10²⁸ Bell pairs)
3. Classical communication of ~2 × 10²⁸ bits
4. Reconstruction of the object at the destination from raw matter

See `research/quantum_teleportation_state_of_science.md` for full scaling analysis.
