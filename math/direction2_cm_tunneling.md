# Direction 2: Center-of-Mass Tunneling — Analysis and Verdict

**Status:** Closed — ruled out by decoherence  
**Result:** CM tunneling of objects larger than ~10⁻¹⁸ kg is not a viable path to teleportation. Decoherence times are shorter than any realistic tunneling time by many orders of magnitude.

---

## What Made This Worth Checking

Quantum tunneling is real. Macroscopic quantum tunneling is real — the Josephson effect (supercurrent tunneling through insulating barriers) is the textbook example. Cooper pairs in a superconductor tunnel as a coherent macroscopic entity, not as individual electrons.

The question was: for a composite bound object with N atoms, does tunneling proceed at the rate of the whole object (using the CM wavefunction) or the product of individual atom rates? If the former, could this be engineered into something useful?

---

## Part 1: Tunneling Rate for a Single Particle

For a particle of mass m tunneling through a rectangular barrier of height V₀ and width d, with energy E < V₀:

```
T ≈ 16 × (E/V₀)(1 - E/V₀) × exp(-2κd)

where κ = √(2m(V₀ - E)) / ℏ
```

The exponential factor dominates. Define the WKB exponent:
```
θ = 2d√(2m(V₀ - E)) / ℏ
```

**Single electron** (m = 9.11×10⁻³¹ kg), barrier V₀ - E = 1 eV, d = 1 nm:
```
κ = √(2 × 9.11×10⁻³¹ × 1.6×10⁻¹⁹) / 1.05×10⁻³⁴ = 5.1×10⁹ m⁻¹
θ = 2 × 10⁻⁹ × 5.1×10⁹ = 10.2
T ≈ exp(-10.2) ≈ 3.7 × 10⁻⁵  (~0.004%)
```

This is the regime of field emission and scanning tunneling microscopy.

**Single proton** (m = 1.67×10⁻²⁷ kg), same barrier:
```
κ = √(2 × 1.67×10⁻²⁷ × 1.6×10⁻¹⁹) / 1.05×10⁻³⁴ = 2.2×10¹¹ m⁻¹
θ = 2 × 10⁻⁹ × 2.2×10¹¹ = 440
T ≈ exp(-440) ≈ 10⁻¹⁹¹
```

Already essentially zero for a proton through a 1 nm barrier.

---

## Part 2: The Composite Object Question

For a composite object of N identical particles each of mass m_p, total mass M = N × m_p, does it tunnel as one object (using M) or as N independent particles?

**Case A: Independent tunneling**
```
T_total ≈ T_single^N = exp(-N × θ_single)
```

This is catastrophically small. For 10² atoms (tiny nanoparticle), T ≈ exp(-44000) ≈ 0.

**Case B: Coherent CM tunneling**
If the object is in a coherent quantum state of its center-of-mass, the relevant mass for CM tunneling is M, not m_p. The CM wavefunction is:

```
Ψ_CM(R) where R = (Σ mᵢrᵢ) / M
```

For a perfectly rigid body at zero temperature with all internal d.o.f. frozen, the CM tunnels as a unit with mass M:
```
κ_CM = √(2M(V₀ - E)) / ℏ
θ_CM = 2d√(2M(V₀ - E)) / ℏ
```

For M = 10⁻¹⁸ kg (100 nm sphere), same 1 eV barrier, 1 nm width:
```
κ_CM = √(2 × 10⁻¹⁸ × 1.6×10⁻¹⁹) / 1.05×10⁻³⁴
     = √(3.2×10⁻³⁷) / 1.05×10⁻³⁴
     = 1.79×10⁻¹⁸·⁵ / 1.05×10⁻³⁴
     = 5.4×10¹⁶ m⁻¹
θ_CM = 2 × 10⁻⁹ × 5.4×10¹⁶ = 1.1 × 10⁸
T_CM ≈ exp(-1.1×10⁸)  →  essentially zero
```

Even for coherent CM tunneling, the exponent grows with √M. For any macroscopic mass through any realistic barrier, the tunneling probability is not zero — it's immeasurably smaller than zero.

**The BEC / Josephson exception:**
In a Josephson junction, it is not the mass that tunnels — it is the *phase* of the macroscopic wavefunction. The relevant coordinate is the phase difference Δφ between two superconductors, not the positions of electrons. The effective "potential barrier" in the Josephson problem is the Josephson energy E_J, and the tunneling is of a phase variable (not a spatial coordinate carrying mass).

This is fundamentally different from spatial teleportation. You cannot extend the Josephson mechanism to spatial transport of matter.

---

## Part 3: The Decoherence Death Blow

Even if CM tunneling were somehow viable, decoherence kills it first. From Direction 4 calculations:

For a 100 nm silica sphere at 10⁻¹⁰ Pa vacuum, 300 K:
- τ_thermal ≈ 5 minutes (gas collisions)
- τ_PD ≈ 26 minutes (if Penrose-Diósi real)

For tunneling to be useful, the tunneling time must be shorter than the coherence time.

**Tunneling time estimate:**
The Büttiker-Landauer traversal time (time to tunnel through a barrier) is:
```
τ_tunnel ≈ d / v_eff  where v_eff = ℏκ/m is the "imaginary velocity" under the barrier
```

For a 100 nm sphere through a 1 nm, 1 eV barrier:
```
κ = 5.4×10¹⁶ m⁻¹ (from above)
v_eff = ℏκ/M = 1.05×10⁻³⁴ × 5.4×10¹⁶ / 10⁻¹⁸ = 5.7×10³ m/s (fast)
τ_tunnel ≈ 10⁻⁹ / 5.7×10³ = 1.8×10⁻¹³ s
```

So the traversal time is femtoseconds — fast. But the transmission probability is exp(-10⁸). You would need to attempt the tunneling 10^(10⁸) times before it succeeds once. At a repetition rate of 10¹³ Hz (atomic vibrational frequency), success time:

```
t_success = 10^(10⁸) × 10⁻¹³ s = 10^(10⁸ - 13) s
```

The age of the universe is ~4×10¹⁷ s ≈ 10¹⁷·⁶ s. We need 10^(10⁸) seconds. This is not physics — this is a number so large it has no physical meaning.

For context: the number of atoms in the observable universe is ~10⁸⁰. We need to attempt tunneling 10^(10,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000) times. The exponent alone requires more digits than atoms in the universe.

---

## Part 4: What About Smaller Objects?

**At what mass does CM tunneling become interesting?**

Set θ_CM = 10 (T ≈ 5×10⁻⁵, measurable tunneling):

```
2d√(2M(V₀-E))/ℏ = 10
M = (10ℏ)² / (8d²(V₀-E))
  = (10 × 1.05×10⁻³⁴)² / (8 × (10⁻⁹)² × 1.6×10⁻¹⁹)
  = 1.10×10⁻⁶⁶ / (1.28×10⁻³⁶)
  = 8.6×10⁻³¹ kg
```

This is the mass of one electron (~9.11×10⁻³¹ kg). That's not an accident — single electrons tunnel through 1 nm barriers with θ ≈ 10. This approach cannot be scaled to useful macroscopic objects.

---

## Part 5: Levitated Nanoparticles — What They Can and Cannot Do

The levitated nanoparticle experiments (Delord 2021, Pontin 2023, Aspelmeyer group) that motivated this direction have demonstrated:
- Cooling a ~10⁷-atom nanoparticle to its CM motional ground state ✓
- Quantum superposition of CM position states (preliminary 2022 results) ✓
- Sub-SQL (below standard quantum limit) position sensitivity ✓

What they have NOT demonstrated:
- Tunneling of the CM through a spatial barrier ✗
- Any spatial displacement via quantum effects beyond the oscillator ground state ✗

What these experiments DO offer (relevant to Direction 4):
- Direct test of Penrose-Diósi at the ~10⁻¹⁸ kg scale
- Demonstration that quantum coherence can be maintained for macroscopic objects on experimental timescales
- Foundation for testing quantum gravity phenomenology

These experiments are valuable for this project — but as tests of Direction 4, not as a path to Direction 2 teleportation.

---

## Verdict

**Direction 2 is closed.**

The reasoning:
1. CM tunneling probability for macroscopic objects scales as exp(-√M × constant), which reaches values beyond physical meaning for M > ~10⁻²⁸ kg.
2. Even if the probability were non-negligible, decoherence timescales (10⁻²³ s at room temperature for human-scale, minutes for 100 nm spheres) are far shorter than the time needed to attempt tunneling the required number of times.
3. The Josephson-effect analogy fails — that effect tunnels a phase variable, not spatial coordinates carrying mass.
4. There is no known mechanism by which quantum coherence in a BEC or superconductor extends to spatial transport at macroscopic scales.

**What to carry forward:** The levitated nanoparticle experiments remain important as tests of Direction 4 (Penrose-Diósi). The cooling and coherence techniques developed for this direction could in principle extend quantum teleportation of quantum states to larger objects — but only up to the decoherence ceiling, which is far below human scale.
