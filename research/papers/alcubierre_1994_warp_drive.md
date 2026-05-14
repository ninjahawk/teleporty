# The Warp Drive: Hyper-Fast Travel Within General Relativity

**Author:** Miguel Alcubierre  
**Year:** 1994  
**Published:** Classical and Quantum Gravity, 11, L73–L77 (1994)  
**arXiv:** gr-qc/0009013 (arXiv upload 2000; original submitted to CQG 1994)  
**DOI:** 10.1088/0264-9381/11/5/001

---

## Abstract
Proposes a spacetime metric allowing a spaceship to travel at arbitrarily high effective velocities by contracting spacetime ahead of it and expanding spacetime behind it — without the ship itself moving through space at faster-than-light speeds locally. No wormhole required. Does require exotic matter (negative energy density).

---

## The Alcubierre Metric

The line element (in units where c = 1):

```
ds² = -dt² + [dx - f(rs, σ) v_s(t) dt]² + dy² + dz²
```

Where:
- `v_s(t) = dx_s(t)/dt` — coordinate velocity of the center of the warp bubble
- `x_s(t)` — trajectory of the center of the bubble along the x-axis
- `rs = √[(x - x_s(t))² + y² + z²]` — radial distance from the bubble center
- `f(rs, σ)` — the warp factor (shape function)

### Warp Factor Function

```
f(rs, σ) = [tanh(σ(rs + R)) - tanh(σ(rs - R))] / [2 tanh(σR)]
```

Where:
- `R` — bubble radius (size of the "flat" region of spacetime inside the bubble)
- `σ` — shape parameter controlling thickness of the transition region (wall of the bubble)
  - Large σ → thin wall (bubble wall sharply defined)
  - Small σ → thick wall (gradual transition)

**Properties of f:**
- f → 1 as rs → 0 (inside the bubble, spacetime is flat)
- f → 0 as rs → ∞ (far outside, normal Minkowski spacetime)
- The transition region (the "bubble wall") is where exotic matter is concentrated

### Geodesic of the Ship
A passenger at the center of the bubble follows a geodesic — they are in free fall and experience no acceleration. Their proper time equals coordinate time within the bubble. To an outside observer, the ship appears to move at v_s, which can exceed c.

---

## Energy Conditions and Exotic Matter

The stress-energy tensor component T₀₀ (energy density as measured by Eulerian observers) is:

```
T₀₀ = -(c⁴ / 8πG) × (v_s² / 4) × ρ²(t) × (df/drs)²
```

**Key result:** T₀₀ is always **negative**. The warp drive requires exotic matter — material with negative energy density — distributed throughout the bubble wall region.

### Exotic Matter Mass Estimate (Original Alcubierre)

For a bubble of radius R = 100 m and σ = 8/R:

```
E_exotic ≈ -10^64 kg × c²
```

This is roughly **10 orders of magnitude larger than the mass-energy of the observable universe** (~10^53 kg). Clearly not achievable with any known technology or material.

### Van Den Broeck Modification (1999) — arXiv:gr-qc/9905084

Chris Van Den Broeck showed that by making the interior volume of the warp bubble macroscopic while making the exterior surface area microscopic (like a "balloon in a bottle"), the total exotic matter requirement can be reduced to:

```
E_exotic ≈ -a few solar masses
```

Still enormous, but ~60 orders of magnitude less than Alcubierre's original estimate.

### Harold White Modification (2011–2012, NASA)

Harold White proposed oscillating the bubble's warp field intensity and using a toroidal (donut-shaped) rather than spherical bubble geometry. White claimed this could reduce exotic matter requirements to:

```
E_exotic ≈ -mass of Jupiter (~2 × 10^27 kg)
```

**Note:** White's analysis has been criticized by multiple physicists. The reduction relies on questionable assumptions about averaging the energy density over time. No peer consensus that this is valid.

---

## Physical Problems (Beyond Exotic Matter)

1. **Causal disconnection:** The interior of the bubble is causally disconnected from the bubble wall. A pilot inside cannot send signals to the wall to steer or shut down the drive. The warp bubble cannot be created or controlled from inside.

2. **Hawking radiation:** Pfenning & Ford (1997) showed that quantum effects at the bubble wall create radiation that could destroy the drive (and the ship).

3. **Quantum inequalities:** Ford-Roman quantum inequalities severely limit how much negative energy can exist, for how long, and in what region. The exotic matter configuration required almost certainly violates quantum inequalities.

4. **Closed timelike curves:** If a warp drive can be constructed, Everett & Roman (2012) showed it could be used to construct time machines, creating causality violations. The Chronology Protection Conjecture (Hawking 1992) suggests physics prevents this.

5. **Horizon formation:** At superluminal bubble speeds, a horizon forms between the ship and the front of the bubble, preventing any interaction with the forward region.

---

## Key Equations Summary

| Quantity | Expression |
|----------|-----------|
| Metric line element | `ds² = -dt² + (dx - f·v_s dt)² + dy² + dz²` |
| Warp function | `f(rs,σ) = [tanh(σ(rs+R)) - tanh(σ(rs-R))] / [2 tanh(σR)]` |
| Energy density | `T₀₀ = -(c⁴/8πG)(v_s²/4)ρ²(df/drs)²` |
| Original exotic mass | `~−10^64 kg` |
| Van Den Broeck reduction | `~−few solar masses` |
| White (2012) estimate | `~−Jupiter mass (~2×10^27 kg)` |

---

## Assessment

**The physics:** The metric is a valid solution to Einstein's field equations. GR itself does not forbid this. The mathematics is sound.

**The engineering:** Requires exotic matter at scales that violate quantum inequalities (Ford-Roman), are causally inaccessible from inside the bubble, and involve energy densities larger than the observable universe (original form). No known physical process produces exotic matter at any relevant scale.

**Status:** Theoretically permitted, practically impossible with any conceivable technology. A legitimate physics thought experiment, not an engineering proposal.

---

## Key References
- Alcubierre (1994), CQG 11 L73 — original paper
- Pfenning & Ford (1997), CQG 14, 1743 — quantum inequalities applied to warp drive
- Van Den Broeck (1999), CQG 16, 3973 — reduced energy requirements
- White (2012), AIP Conf. Proc. 1486, 259 — oscillating bubble modification (controversial)
- Everett & Roman (2012) — warp drives and CTCs
