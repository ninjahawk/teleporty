# The Quantum Interest Conjecture (Ford-Roman Quantum Inequalities)

**Authors:** L.H. Ford (Tufts University), Thomas A. Roman (Central Connecticut State University)  
**Year:** 1999  
**Published:** Physical Review D, 60, 104018 (1999)  
**arXiv:** gr-qc/9901074

---

## Context: What Are Quantum Inequalities?

Ford (1978) first showed that negative energy densities are permitted in quantum field theory (e.g., Casimir effect, squeezed vacuum states) but that they are constrained — you cannot have arbitrarily large negative energy for arbitrarily long times.

Ford & Roman developed "quantum inequalities" (QIs) through the 1990s — these are uncertainty-principle-like bounds on negative energy. They take the form:

```
∫ ρ(τ) g(τ) dτ ≥ -C / t₀⁴
```

Where:
- `ρ(τ)` = energy density measured along a timelike worldline
- `g(τ)` = a sampling function peaked on timescale `t₀`
- `C` = positive constant (of order 1 in natural units)
- `t₀` = sampling time

**Interpretation:** The time-averaged energy density (weighted by a positive function of duration t₀) cannot be more negative than ~−1/t₀⁴ (in Planck units). The shorter the duration of negative energy, the less negative it can be — and there must be compensating positive energy before/after.

---

## The Quantum Interest Conjecture (1999 paper)

Building on earlier QI work, Ford & Roman propose: a pulse of negative energy must be followed by a compensating pulse of positive energy, and the positive pulse must *exceed* the negative pulse by an amount that increases with their temporal separation.

```
E_+ ≥ E_- × (1 + α × T²/τ²)
```

Where:
- `E_+` = energy in the positive pulse
- `E_-` = magnitude of energy in the negative pulse  
- `T` = temporal separation between pulses
- `τ` = characteristic duration of the pulses
- `α` = positive constant

**Analogy to finance:** Like a bank loan — you can borrow negative energy, but you must pay it back with interest. The longer you wait to repay, the higher the interest. The "bank" is the quantum vacuum.

---

## Implications for Exotic Matter / Wormholes / Warp Drives

For a macroscopic traversable wormhole, you need:
1. A large amount of negative energy (−Jupiter mass scale for a 1 m throat)
2. Sustained over a macroscopic region (the throat)
3. Without compensating positive energy destroying the geometry

The quantum interest conjecture says you cannot sustain a large negative energy density in a macroscopic region for a macroscopic time without paying an even larger positive energy penalty. This effectively rules out:
- Stable macroscopic wormhole throats
- Warp drive exotic matter configurations
- Any engineering use of negative energy at human scales

### Numerical Example

For a Casimir device with plate separation `a = 1 μm` (10⁻⁶ m):

```
Energy density ≈ -ℏc π² / (720 a⁴) ≈ -1.3 × 10⁻³ J/m³
```

This is the maximum negative energy density achievable by Casimir plates at that separation. For reference, the negative energy density needed at a wormhole throat of radius R = 1 m is roughly:

```
ρ_exotic ≈ -c⁴ / (8πGR²) ≈ -4.8 × 10³⁵ J/m³
```

The gap is **~38 orders of magnitude**. Casimir plates cannot plausibly provide the required exotic matter density, even in principle (the QIs become violated long before that density could be sustained).

---

## Earlier Ford-Roman Papers (QI Development)

1. **Ford (1978)** — First quantum inequalities result; negative energy must be compensated
2. **Ford & Roman (1995)** — "Averaged energy conditions and quantum inequalities", PRD 51, 4277
3. **Ford & Roman (1996)** — "Quantum field theory constrains traversable wormhole geometries", PRD 53, 5496 — directly showed wormhole exotic matter configurations violate QIs
4. **Ford & Roman (1997)** — "Restrictions on negative energy density in flat spacetime", PRD 55, 2082
5. **Ford & Roman (1999)** — "The Quantum Interest Conjecture" (this paper)

---

## Assessment

**Status:** Established theoretical physics. Ford-Roman quantum inequalities are universally accepted by the quantum field theory community and are derived from first principles (the positivity of energy in quantum field theory).

**What they prove:** You cannot engineer macroscopic amounts of negative energy using any quantum process consistent with known physics.

**What they do NOT prove:** They are derived in flat spacetime (Minkowski). Their extension to curved spacetime (where wormholes live) is more complex and remains an active research area. However, the expectation is that they hold in any physically reasonable curved spacetime background.

**Bottom line for teleportation:** Quantum inequalities are the most fundamental barrier to wormhole-based teleportation. Even if you solve every other problem, the vacuum itself enforces a debt-with-interest rule on negative energy that makes macroscopic exotic matter configurations physically untenable.
