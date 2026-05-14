# Direction 4: Penrose-Diósi Gravitational Decoherence — Full Calculation

**Status:** Complete  
**Result:** Quantum approaches are capped at ~10⁻¹⁵ kg by thermal decoherence alone. Penrose-Diósi, if real, tightens the cap to ~10⁻¹⁸ kg. Human-scale quantum teleportation is ruled out by both.

---

## The Model

Roger Penrose (1996) and Lajos Diósi (1989) independently proposed that wavefunction collapse is caused by the gravitational energy difference between superposition branches. A system in a spatial superposition of states A and B has two different spacetime geometries — and GR cannot handle a superposition of geometries, so the system collapses.

**Collapse timescale:**
```
τ_PD = ℏ / E_G
```

**Gravitational self-energy of the density difference:**
```
E_G = G ∫∫ [ρ_A(r) - ρ_B(r)] [ρ_A(r') - ρ_B(r')] / |r - r'| d³r d³r'
```

Where ρ_A(r), ρ_B(r) are the mass density distributions of the two branches.

---

## Part 1: Exact Calculation for a Uniform Sphere

For a rigid uniform sphere of mass m and radius R, displaced by distance d between branches:

The integral decomposes as:
```
E_G = G [W_AA + W_BB - 2W_AB]
```

Where:
- W_AA = W_BB = gravitational self-interaction of each branch's density = 3Gm²/(5R)
- W_AB = mutual gravitational energy between the two branches

**Gravitational self-energy of a uniform sphere:**
```
W_self = 3Gm² / (5R)
```

**Mutual energy for non-overlapping spheres (d > 2R):**
```
W_AB = Gm²/d × [1 + 2(R/d)² + ...] → Gm²/d as d → ∞
```

**Fully separated case (d >> R):**
```
E_G → 2 × 3Gm²/(5R) - 2 × 0 = 6Gm²/(5R)

τ_PD = 5ℏR / (6Gm²)
```

For fixed density ρ, substituting m = (4/3)πR³ρ:
```
E_G = (32π²G ρ² R⁵) / 15

τ_PD = 15ℏ / (32π²G ρ² R⁵)
```

---

## Part 2: Numerical Results (Silica Spheres, ρ = 2200 kg/m³)

Computing the constant:
```
K = 32π²G ρ² / 15
  = 32 × 9.870 × 6.674×10⁻¹¹ × (2200)² / 15
  = 32 × 9.870 × 6.674×10⁻¹¹ × 4.84×10⁶ / 15
  = 6.80×10⁻³ J·m⁻⁵

E_G = 6.80×10⁻³ × R⁵    (R in meters)
τ_PD = 1.55×10⁻³² / R⁵  (seconds)
```

| Radius R | Mass m | E_G (J) | τ_PD | Comparable object |
|----------|--------|---------|------|-------------------|
| 1 nm | 9.2 × 10⁻²⁴ kg | 6.8 × 10⁻⁴⁸ | **490,000 years** | Protein |
| 10 nm | 9.2 × 10⁻²¹ kg | 6.8 × 10⁻⁴³ | **4.9 years** | Large protein complex |
| 100 nm | 9.2 × 10⁻¹⁸ kg | 6.8 × 10⁻³⁸ | **26 minutes** | Large virus (adenovirus) |
| 430 nm | 7.5 × 10⁻¹⁶ kg | 1.05 × 10⁻³⁴ | **1 second** | ← Penrose-Diósi 1-second limit |
| 1 μm | 9.2 × 10⁻¹⁵ kg | 6.8 × 10⁻³³ | **15 ms** | Bacterium |
| 3 μm | 7.5 × 10⁻¹³ kg | 1.65 × 10⁻³¹ | **0.6 ms** | Red blood cell |
| 10 μm | 9.2 × 10⁻¹² kg | 6.8 × 10⁻²⁸ | **155 ns** | Small cell |
| 100 μm | 9.2 × 10⁻⁹ kg | 6.8 × 10⁻²³ | **1.5 ps** | Sand grain |
| 1 mm | 9.2 × 10⁻⁶ kg | 6.8 × 10⁻¹⁸ | **15 as** | Grain of salt |
| 1 cm | 9.2 × 10⁻³ kg | 6.8 × 10⁻¹³ | **0.15 ys** | Raisin |

**For a 70 kg human** (ρ_body ≈ 1060 kg/m³, effective radius R ≈ 0.25 m, fully separated superposition):
```
E_G = 6G × m² / (5R) = 6 × 6.67×10⁻¹¹ × 70² / (5 × 0.25)
    = 6 × 6.67×10⁻¹¹ × 4900 / 1.25
    ≈ 1.57 × 10⁻⁶ J

τ_PD = ℏ / E_G = 1.05×10⁻³⁴ / 1.57×10⁻⁶ ≈ 6.7 × 10⁻²⁹ s
```

**A human body in quantum superposition collapses in ~10⁻²⁹ s under the Penrose-Diósi model.** Nuclear vibration timescales are ~10⁻²³ s. A human superposition collapses one million times faster than an atomic nucleus can vibrate once.

---

## Part 3: Thermal Decoherence (For Comparison)

Penrose-Diósi is not the only source of decoherence. Thermal photons and residual gas also collapse quantum superpositions. The comparison between the two defines which is the binding constraint.

### Gas Molecule Scattering

Decoherence rate from gas collisions:
```
Γ_gas = n_gas × σ_scatter × v_thermal
```

Where:
- n_gas = P / (k_B T) — gas number density
- σ_scatter ≈ π R² — geometric cross section (for R >> λ_dB of gas molecule)
- v_thermal = √(8k_B T / π m_air) — mean thermal speed of N₂ at 300 K ≈ 475 m/s

At various vacuum levels, 300 K, for R = 100 nm:

| Vacuum level | P (Pa) | n_gas (m⁻³) | τ_gas (s) | τ_PD (s) | Dominant |
|-------------|--------|-------------|-----------|-----------|---------|
| Sea level | 10⁵ | 2.4 × 10²⁵ | 3 × 10⁻¹⁵ s | 1548 s | Thermal (by 18 orders) |
| Standard lab | 10⁻⁵ | 2.4 × 10¹⁵ | 3 × 10⁻⁵ s | 1548 s | Thermal (by 8 orders) |
| Good UHV | 10⁻⁸ | 2.4 × 10¹² | 3 s | 1548 s | Thermal |
| Best UHV | 10⁻¹⁰ | 2.4 × 10¹⁰ | 300 s | 1548 s | **Comparable** |
| 10⁻¹² Pa | 10⁻¹² | 2.4 × 10⁸ | 30,000 s | 1548 s | **Penrose-Diósi wins** |

At ~10⁻¹¹ Pa vacuum (achievable in lab, difficult), the two timescales cross for a 100 nm sphere. This is the operating point for experiments that can test the Penrose-Diósi model.

### Thermal Photon Scattering

For a nanoparticle with R << λ_thermal (where λ_thermal ≈ 10 μm at 300 K):

Photon scattering is in the Rayleigh regime:
```
σ_photon ∝ R⁶ / λ⁴  (much smaller than geometric cross section for R << λ)
```

For R = 100 nm, λ = 10 μm:
σ_photon ≈ (100nm/10μm)⁴ × πR² = (0.01)⁴ × π × (10⁻⁷)² ≈ 10⁻²² m²

Rate ≈ (c × energy density of thermal radiation) / (energy per photon) × σ_photon
     ≈ (radiation energy density at 300K is σ_SB T⁴/c ≈ 6×10⁻⁶ J/m³)
     ≈ negligible for sub-μm particles

Photon thermal decoherence is subdominant to gas scattering for nanoparticles below ~1 μm. For human-scale objects (where R >> λ_thermal), photon decoherence becomes important.

### Human-Scale Thermal Decoherence

For a human at 300 K in vacuum:

Thermal radiation emitted by the human body at 37°C:
- Power: P = ε σ_SB T⁴ A ≈ 0.98 × 5.67×10⁻⁸ × 310⁴ × 1.73 ≈ 544 W
- Energy per photon (peak of thermal spectrum at 310 K, λ ≈ 9.4 μm): 
  E_photon = hc/λ = 6.63×10⁻³⁴ × 3×10⁸ / 9.4×10⁻⁶ = 2.1×10⁻²⁰ J
- Photon emission rate: 544 / 2.1×10⁻²⁰ ≈ 2.6×10²² photons/second

**Each emitted photon carries "which branch" information and causes decoherence.**
```
τ_thermal_photon (human) ≈ 1 / (2.6 × 10²²) ≈ 3.8 × 10⁻²³ s
```

This is the thermal decoherence time for a human body at room temperature from photon emission alone, in perfect vacuum. It's a hard limit that cannot be overcome by improving vacuum — the human body itself emits thermal radiation.

To suppress this: cool the body to 0 K. Not compatible with life. Not compatible with a meaningful "person" at the destination.

---

## Part 4: Comparison Table — All Mechanisms

| Mass | Object | τ_PD | τ_thermal (10⁻¹⁰ Pa) | τ_photon (300K) | Binding limit |
|------|--------|------|----------------------|-----------------|---------------|
| 10⁻¹⁸ kg | 100 nm sphere | 26 min | 5 min | negligible | Both comparable |
| 10⁻¹⁵ kg | 1 μm sphere | 15 ms | 0.3 s | ~ms | Thermal gas |
| 10⁻¹² kg | 10 μm sphere | 155 ns | 1.4 ms | ~ms | PD (if real) |
| 10⁻⁶ kg | 130 μm sphere | 1.5 ps | — | — | PD / photons |
| 70 kg | Human | 6.7 × 10⁻²⁹ s | — | 3.8 × 10⁻²³ s | Photons first |

---

## Part 5: The Teleportation Mass Ceiling

Combining both decoherence mechanisms, the practical ceiling for quantum teleportation (requiring τ > 1 second to run the protocol):

**From thermal decoherence alone (no PD required):**

Setting Γ_gas = n_gas × π R² × v_thermal < 1 s⁻¹, at best vacuum (10⁻¹² Pa):
```
n_gas = 2.4 × 10⁸ m⁻³
v_thermal = 475 m/s

R²_max = 1 / (n_gas × π × v_thermal) = 1 / (2.4×10⁸ × π × 475) = 2.8×10⁻¹² m²
R_max ≈ 53 μm
m_max (silica) ≈ (4/3)π(53×10⁻⁶)³ × 2200 ≈ 1.4 × 10⁻⁸ kg
```

So even without Penrose-Diósi, at the best achievable vacuum and room temperature, quantum teleportation is limited to objects smaller than ~50 μm (10⁻⁸ kg).

**At 0 K (eliminates thermal gas and photon decoherence), Penrose-Diósi alone:**

τ_PD > 1 s requires R < 430 nm (from Part 2), m < 7.5 × 10⁻¹⁶ kg.

This is the irreducible quantum limit if Penrose-Diósi is real.

**Summary of ceilings:**

| Condition | Max object for quantum teleportation |
|-----------|--------------------------------------|
| Room temp, sea level air | ~1 nm (single molecule) |
| Room temp, 10⁻¹⁰ Pa vacuum | ~50 nm sphere (10⁻¹⁸ kg) |
| 0 K, perfect vacuum, PD real | ~430 nm sphere (7.5 × 10⁻¹⁶ kg) |
| 0 K, perfect vacuum, PD false | ~50 μm sphere (10⁻⁸ kg)* |
| Human body (70 kg) | **Impossible by any quantum approach** |

*Limited by zero-point field (quantum vacuum fluctuations), which still cause decoherence at 0 K.

---

## Part 6: What the Experiments Will Show

Current experiments testing Penrose-Diósi:

**AION (100m atom interferometer, Oxford)** — uses strontium atoms, testing superposition coherence over long baselines. Should probe PD timescales for ~10⁻²⁵ kg atoms over seconds.

**MAGIS-100 (Fermilab)** — 100m baseline, strontium atoms. Full operation ~2026–2028. Will probe PD at ~10⁻²⁵ kg.

**Levitated nanoparticle interferometry (Vienna, Zurich groups)** — ~10⁻¹⁸ kg particles (100 nm), coherence times approaching the regime where PD and thermal compete. This is the closest to a direct test.

**What a positive PD signal looks like:** Coherence decay faster than predicted by environmental decoherence alone, with the excess matching the E_G/ℏ prediction.

**What a negative PD signal means for this project:** Standard QM is correct. No gravitational collapse. The ceiling from Part 5 row 4 applies. Still no path to human-scale quantum teleportation (the 0 K, perfect vacuum limit of ~50 μm is still seven orders of magnitude below a human). Direction 1 remains the only viable path regardless of the PD outcome.

---

## Conclusion

**Penrose-Diósi or not, quantum teleportation of human-scale objects is physically ruled out by:**
1. Thermal radiation from the body itself (~10⁻²³ s at 300K)
2. Gas molecule collisions at any achievable vacuum (~10⁻¹⁵ s at 10⁻¹⁰ Pa for human scale)

These are not engineering problems. They are thermodynamic consequences of being a warm, physical object in a physical environment.

**The Penrose-Diósi result is still important because:**
- It sets the ceiling for quantum teleportation of small objects (viruses, bacteria, nanoparticles)
- If real, it rules out quantum approaches above ~430 nm even at 0 K in perfect vacuum
- The experiments currently running are the most important near-term tests for this project

**For the main goal (human-scale teleportation):** This calculation definitively confirms that Direction 1 (classical information reframing) is the only physically viable path. All quantum approaches fail before reaching scales relevant to the human body.
