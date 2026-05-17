# Fabricator Simulation: Human-Scale Teleportation

**Status:** [THIS PROJECT] — quantitative engineering model  
**Date:** 2026-05-17  
**Goal:** Determine what a human-scale teleportation fabricator must look like: resolution,
throughput, parallelization, and vascular viability constraints. Identify where the physics
limits are and where the engineering gaps are.

Baseline: apple pipeline (see `apple_pipeline.md`) established the fabricator as the
binding constraint, with 10× resolution gap (100 μm → 10 μm) and 100× throughput gap
(10⁶ cells/min → 10⁸ cells/s). This document extends the model to human scale.

---

## 1. Resolution Requirement

### Functional unit analysis

The resolution a fabricator needs is set by the smallest structure whose position affects
function. This differs between tissue types.

**Neural tissue:**

The functional unit is the synapse. A synapse determines:
- Which neuron connects to which (graph topology) — captured in the connectome spec (42 KB)
- The weight of that connection — also in the spec
- The *position* of the synapse on the dendritic tree — affects dendritic integration

Dendritic compartment models (Rall 1967; Mainen & Sejnowski 1996) show that synapse
position within ~1 μm on a dendrite produces measurable differences in somatic voltage.
So the fabricator needs to place synaptic contacts with ~1 μm accuracy.

Synapse footprint: active zone ~300 nm, overall post-synaptic density ~1 μm.
Nyquist: resolving a 1 μm structure requires ≤ 0.5 μm voxels. Round up to:

```
Δx_neural = 1 μm
```

**[ESTABLISHED]** Dendritic computation models, synapse dimensions from electron microscopy.  
**[THIS PROJECT]** 1 μm precision is sufficient; sub-μm variation in synapse position does
not materially alter circuit behavior at the network level given D=30% distortion tolerance.

**Somatic (non-neural) tissue:**

The functional unit is the cell. Functional equivalence requires:
- Correct cell type at each position (determines enzyme expression, metabolic role)
- Correct cell-cell contacts (determines gap junction and tight junction formation)
- Correct extracellular matrix organization (mechanical properties, signaling)

Cell-cell junctions form spontaneously when cells of the correct type are in contact.
The fabricator does not need to place individual junction proteins — it places cells, and
junction formation is self-organizing.

Cell diameters: 10–30 μm across tissue types. Nyquist on a 10 μm cell:

```
Δx_somatic = 5 μm
```

This matches the apple pipeline (10 μm; slightly coarser is fine for non-neural tissue
because apples have no fine-grained spatial computation).

**[ESTABLISHED]** Gap junction and tight junction self-assembly are established cell biology.  
**[THIS PROJECT]** 5 μm resolution is sufficient for somatic functional equivalence.

### Resolution summary

| Tissue | Δx required | Limiting structure |
|--------|------------|-------------------|
| Neural (brain, spinal cord) | 1 μm | Synapse position on dendrite |
| Muscle | 5 μm | Sarcomere organization (self-assembles from myosin/actin) |
| Liver, kidney, gut | 5 μm | Cell type and position |
| Vascular (large vessels) | 10 μm | Lumen geometry |
| Vascular (capillaries) | 2 μm | Capillary lumen ~8 μm; must be patent |
| Skin | 5 μm | Layered epithelium |

The binding resolution constraint across the whole body is **neural tissue: Δx = 1 μm**.

---

## 2. Voxel Count

**Brain:**

Volume: V_brain = 1.2 L = 1.2 × 10⁻³ m³  
Resolution: Δx = 1 μm = 10⁻⁶ m

```
N_voxels_brain = V_brain / Δx³
               = 1.2 × 10⁻³ / (10⁻⁶)³
               = 1.2 × 10⁻³ / 10⁻¹⁸
               = 1.2 × 10¹⁵ voxels
```

Active voxels (excluding extracellular space, ~20% of brain volume):

```
N_active_brain = 0.80 × 1.2 × 10¹⁵ = 9.6 × 10¹⁴ ≈ 10¹⁵ voxels
```

**Body (non-neural):**

Volume: V_body = 70 L − 1.2 L ≈ 68.8 L = 6.88 × 10⁻² m³  
Resolution: Δx = 5 μm = 5 × 10⁻⁶ m

```
N_voxels_body = 6.88 × 10⁻² / (5 × 10⁻⁶)³
              = 6.88 × 10⁻² / 1.25 × 10⁻¹⁶
              = 5.5 × 10¹⁴ voxels
```

Active voxels (~65% fill from cell packing + ECM):

```
N_active_body = 0.65 × 5.5 × 10¹⁴ = 3.6 × 10¹⁴ voxels
```

**Total:**

```
N_voxels_total = 9.6 × 10¹⁴ + 3.6 × 10¹⁴ = 1.32 × 10¹⁵ ≈ 1.3 × 10¹⁵ voxels
```

The brain dominates voxel count by ~2.7× despite being 1.7% of body volume, because
its 5× finer resolution requires (5)³ = 125× more voxels per unit volume.

### Comparison to apple

| Object | Volume | Resolution | Voxels |
|--------|--------|-----------|--------|
| Apple | 400 mL | 10 μm | 4 × 10¹¹ |
| Human brain | 1.2 L | 1 μm | 1.2 × 10¹⁵ |
| Human body (non-brain) | 68.8 L | 5 μm | 5.5 × 10¹⁴ |
| Human total | 70 L | mixed | 1.7 × 10¹⁵ |

Human total is **4250× more voxels** than the apple.

---

## 3. Cell Count

Independent of voxel counting, the fabricator must place individual cells (the physical
deposition unit). Voxels describe what goes where; cells are what gets deposited.

```
Human body total cells: N_cells = 3.7 × 10¹³
  Brain (neurons + glia): 1.7 × 10¹¹
  Somatic remainder:      3.68 × 10¹³
```

**[ESTABLISHED]** Bianconi et al. 2013 (Ann. Human Biol.) cell count estimate.

For comparison, the apple: ~3 × 10⁸ cells.

Human body has **~10⁵× more cells** than an apple.

---

## 4. Vascular Viability Constraint

This is the unique hard constraint for humans that the apple sidesteps entirely.
A printed organ dies without oxygen supply. The question: how fast must the fabricator
work before ischemic cell death compromises the reconstruction?

### Krogh cylinder derivation

The maximum tissue thickness that can be oxygenated by diffusion from a nearby capillary
is the Krogh radius R_K. This was derived by August Krogh (1919) for cylindrical geometry.

Parameters for brain tissue:
- O₂ diffusivity in tissue: D = 2 × 10⁻⁹ m²/s
- O₂ consumption rate: q = 3.5 mL O₂/(100g·min) at 37°C

Converting q to SI:
```
q = 3.5 × 10⁻² mL / (g·min) = 5.83 × 10⁻⁴ mL / (mL·s)
  = 5.83 × 10⁻⁴ × (1 mol / 22,400 mL) × 10⁶ mL/m³
  = 5.83 × 10⁻⁴ × 44.6 mol/(m³·s)
  = 0.026 mol/(m³·s)
```

O₂ concentration at capillary wall (pO₂ ≈ 50 mmHg, Henry's law in tissue):
```
K_H (O₂ in water, 37°C) = 1.3 × 10⁻³ mol/(L·atm)
pO₂ = 50/760 atm = 0.0658 atm
C_a = 1.3 × 10⁻³ × 0.0658 = 8.6 × 10⁻⁵ mol/L = 8.6 × 10⁻² mol/m³
```

Krogh radius (simplified, ignoring log correction):
```
R_K = sqrt(4 D C_a / q)
    = sqrt(4 × 2 × 10⁻⁹ × 8.6 × 10⁻² / 0.026)
    = sqrt(4 × 2 × 10⁻⁹ × 3.31)
    = sqrt(2.65 × 10⁻⁸)
    = 1.6 × 10⁻⁴ m
    = 160 μm
```

**R_K ≈ 160 μm.** Cells beyond 160 μm from the nearest capillary face anoxia.

**[ESTABLISHED]** Krogh 1919; confirmed by measured intercapillary distances in brain
gray matter (~25–50 μm, consistent with R_K ≈ 25–50 μm at local mean pO₂; the 160 μm
corresponds to maximum radius at capillary-wall pO₂, not mean tissue pO₂).  
**[ESTABLISHED]** q and D values from cerebral metabolic rate literature (Fox & Raichle 1986).

### Hypothermic fabrication

At 37°C, brain ischemia tolerance is ~4 minutes (irreversible damage). This would demand
fabrication at ~7 × 10⁸ cells/s for the brain alone (calculated below) — feasible, but
requires the brain to be the last organ printed and immediately perfused.

A cleaner approach: hypothermic fabrication at 4–10°C.

Metabolic rate scales with temperature by Q₁₀ ≈ 2–3 (van't Hoff rule):
```
Rate(4°C) / Rate(37°C) = Q₁₀^((4−37)/10) = Q₁₀^(−3.3)

Q₁₀ = 2: factor = 2^(−3.3) = 0.10   (10× slower metabolism)
Q₁₀ = 3: factor = 3^(−3.3) = 0.037  (27× slower metabolism)
```

At 4°C, brain tissue consumes O₂ at ~10–27× lower rate → ischemia tolerance extends to
40–120 minutes. Deep hypothermic circulatory arrest (DHCA) in cardiac surgery uses this:
standard DHCA at 4–18°C permits 45–60 min of circulatory arrest without neurological damage.

**[ESTABLISHED]** DHCA literature: Bellinger et al. 1995, Shin'oka et al. 2000.

**Assumption [THIS PROJECT]:** fabricate at T_fab = 4°C with oxygenated perfluorocarbon
preservation solution. This extends neural viability window to 60 minutes.

This also modifies R_K at reduced temperature:
```
q(4°C) ≈ 0.026 / 15 = 1.7 × 10⁻³ mol/(m³·s)  (using geometric mean Q₁₀)
R_K(4°C) = sqrt(4 × 2 × 10⁻⁹ × 8.6 × 10⁻² / 1.7 × 10⁻³)
           = sqrt(4.1 × 10⁻⁷)
           = 6.4 × 10⁻⁴ m = 640 μm
```

At 4°C, oxygen diffuses effectively across ~640 μm, relaxing the per-layer constraint.
Each printed layer can be up to ~640 μm thick before the next layer cuts off O₂ supply.

**This is the key enabling assumption:** hypothermic fabrication at 4°C eliminates the
per-layer vascular emergency. The only constraint becomes: complete fabrication within
60 minutes and then restore warm circulation.

---

## 5. Throughput Target

With a 60-minute fabrication window at 4°C:

```
Target time: T = 3600 s
Total cells:  N = 3.7 × 10¹³

Required throughput: Ṅ = N / T = 3.7 × 10¹³ / 3600 = 1.0 × 10¹⁰ cells/s
```

**The fabricator must deposit 10 billion cells per second.**

Comparison to apple:
```
Apple throughput (from apple_pipeline.md): 10⁸ cells/s
Human throughput required:                 10¹⁰ cells/s
Ratio:                                     100×
```

This 100× gap is on top of the already-established 100× throughput gap between current
bioprinters and the apple target. So the full gap from current state of the art to
human-scale fabrication is **10,000×** in throughput.

### Breakdown by tissue

| Tissue | Cell count | Fraction | Time at 10¹⁰ cells/s |
|--------|-----------|----------|----------------------|
| Somatic (non-brain) | 3.68 × 10¹³ | 99.5% | 3582 s (59.7 min) |
| Brain | 1.7 × 10¹¹ | 0.5% | 17 s |

The brain is a tiny fraction of the cell count; the body dominates fabrication time.
However, the brain voxel count dominates due to fine resolution (see Section 2).

**Voxel throughput:**

```
Total voxels: 1.3 × 10¹⁵
Target time:  3600 s
Required rate: 1.3 × 10¹⁵ / 3600 = 3.6 × 10¹¹ voxels/s
```

At the finer resolution, the voxel throughput is the harder constraint.
Each voxel may contain a sub-cellular feature (organelle, ECM fiber) that must be
correctly placed even when not occupied by a whole cell.

---

## 6. Parallelization: How Many Print Heads?

The fabricator achieves required throughput through massive parallelization.
A single inkjet-style bioprinting nozzle deposits ~1 cell per droplet at ~1 kHz:

```
Single nozzle throughput: ṅ_1 = 10³ cells/s
```

**[ESTABLISHED]** Current inkjet bioprinting rates: Murphy & Atala 2014 (Nature Biotechnology).

Number of nozzles needed:
```
N_nozzles = Ṅ / ṅ_1 = 10¹⁰ / 10³ = 10⁷ nozzles = 10 million nozzles
```

**Physical area of print head:**

Current inkjet nozzle density: ~10³ nozzles/cm² (100 μm pitch between nozzles):
```
A_head = N_nozzles / ρ_nozzles = 10⁷ / 10³ = 10⁴ cm² = 1 m²
```

A **1 m × 1 m print head array** with 10 million nozzles achieves the 60-minute target.

If nozzle density advances to 10⁴/cm² (30 μm pitch, achievable with MEMS fabrication):
```
A_head = 10⁷ / 10⁴ = 10³ cm² = 0.1 m² (33 cm × 33 cm)
```

A sub-meter print head array is achievable with near-term MEMS technology.

**Print head geometry:**

The fabricator is a chamber ~1 m × 1 m × 2 m (human-scale). The print head array
traverses vertically (z-axis), depositing one horizontal layer at a time.

Layer thickness: Δz = 5 μm (somatic) or 1 μm (neural).
Total layers: H_human / Δz = 1.8 m / 5 μm = 3.6 × 10⁵ layers (body)
              H_brain / Δz = 0.12 m / 1 μm = 1.2 × 10⁵ layers (brain, neural resolution)

At 3600 s total, time per layer:
```
t_layer (body): 3600 / 3.6 × 10⁵ = 0.01 s/layer (somatic, Δz = 5 μm)
t_layer (brain): [brain section of 17s] / 1.2 × 10⁵ = 1.4 × 10⁻⁴ s/layer (Δz = 1 μm)
```

Wait — these are simultaneous, not sequential. The full 1 m² print head prints the brain
region at 1 μm and the somatic region at 5 μm. For practical implementation, the print
head array can be zoned (high-density zone for neural tissue, lower-density zone for
somatic tissue), or the full array operates at 1 μm everywhere (overkill for somatic,
but eliminates the zoning engineering problem).

Full-array at 1 μm (uniform high resolution):
- Somatic cells at 1 μm: mostly empty voxels, low throughput demand
- Brain at 1 μm: full utilization
- No zoning complexity

This is the simpler design and has no physics disadvantage.

---

## 7. Physics Limits

For each constraint, confirm whether the gap is engineering or fundamental.

### Resolution: physics floor

Bioprinting resolution is limited by:
1. Droplet mechanics: surface tension, nozzle diameter
   - Minimum stable droplet: ~1 μm at surface tension γ ≈ 0.03 N/m, ΔP ~ 2γ/r ~ 6×10⁴ Pa → achievable with MEMS nozzles
   - Physics floor: ~100 nm (atomic force microscope writes with 10 nm precision)
2. Cell positioning post-deposition: Brownian motion of a cell-sized object
   - k_B T / (drag force) → drift ~1 nm/s for μm-scale objects in hydrogel → not limiting

**Required: 1 μm. Physics floor: ~100 nm. Gap to physics floor: 10×.**  
**Gap to current best: 100× (current best: ~10 μm inkjet, 100 μm extrusion).**  
**[CONCLUSION: engineering gap, not fundamental.]**

### Throughput: physics floor

Each cell is ~10 μm. To deposit at velocity v through a nozzle:
```
Time per cell: t_cell = d_cell / v = 10 μm / v
Throughput per nozzle: ṅ = v / d_cell
```

At v = 1 m/s (slow laminar flow, easily achievable): ṅ = 10⁵ cells/s per nozzle.

At that single-nozzle rate with 10⁷ nozzles: 10¹² cells/s — **100× more than needed**.

The physics floor on throughput is not a ceiling at all; it's a floor far above the
target. Throughput is purely an engineering/cost problem (number of nozzles, system
integration, cross-contamination avoidance).

**[CONCLUSION: no physics limit on throughput at the required scale.]**

### Vascular viability: physics floor

The O₂ diffusion timescale through a hypothermically fabricated layer sets the
minimum perfusion restoration time required.

After completing fabrication, the O₂ diffusion time from the body surface to the
deepest interior tissue:
```
d_max = 0.1 m (rough center-to-surface distance for trunk)
t_diff = d_max² / D_O2 = (0.1)² / 2 × 10⁻⁹ = 5 × 10⁶ s ≈ 58 days
```

Diffusion alone cannot oxygenate deep tissue on a survivable timescale. This is why
vasculature must be patent — diffusion is not the transport mechanism for bulk tissue.
The fabricated vasculature must conduct bulk flow (convection), not diffusion.

The fabricator must therefore print **a connected vascular tree** that is perfusable
immediately upon completion. This is not a throughput constraint but a structural one:
the vascular topology must be correct, not just the parenchymal cell positions.

Additional vascular constraint: the fabricated capillary lumen (~8 μm diameter) must
be open (not collapsed or blocked by debris). This is a fabrication quality constraint
that is separate from throughput.

**[THIS PROJECT]** Vascular patent fabrication (printing hollow tubes at 8 μm diameter
with correct cell lining) is an engineering challenge but not a physics impossibility.
Proof of concept: electrospun tubes at 100 μm are commercially available; 8 μm is ~10×
finer. No physics barrier prevents it.

---

## 8. Energy: Human Scale

**Thermodynamic minimum:**

Entropy cost to assemble 1.3 × 10¹⁵ voxels (brain, Δx = 1 μm):
```
V_accessible = V_brain = 1.2 × 10⁻³ m³
V_target = Δx³ = (10⁻⁶)³ = 10⁻¹⁸ m³

ΔS_voxel = k_B × ln(V_accessible / V_target)
          = 1.38 × 10⁻²³ × ln(1.2 × 10¹⁵)
          = 1.38 × 10⁻²³ × 34.7
          = 4.8 × 10⁻²² J/K

T × ΔS_voxel at T = 277 K (4°C): = 1.3 × 10⁻¹⁹ J per voxel

E_min_brain = 9.6 × 10¹⁴ × 1.3 × 10⁻¹⁹ = 1.2 × 10⁻⁴ J ≈ 0.1 mJ
```

For body voxels (Δx = 5 μm):
```
ΔS_voxel = k_B × ln(6.88 × 10⁻² / 1.25 × 10⁻¹⁶)
          = 1.38 × 10⁻²³ × ln(5.5 × 10¹⁴)
          = 1.38 × 10⁻²³ × 34.0 = 4.7 × 10⁻²² J/K
T × ΔS_voxel = 1.3 × 10⁻¹⁹ J

E_min_body = 3.6 × 10¹⁴ × 1.3 × 10⁻¹⁹ = 4.7 × 10⁻⁵ J

E_min_total = 0.1 mJ + 0.05 mJ ≈ 0.15 mJ
```

The thermodynamic minimum energy for human-scale fabrication is **~0.15 mJ**. Negligible.

**Practical energy:**

Scaling from apple (~1 kWh for 400g):
```
Human body mass: 70 kg = 175 × apple mass

E_practical ≈ 175 × 1 kWh = 175 kWh
```

At $0.10/kWh: **$17.50 per teleportation event**.

Energy cost is not a barrier at any scale.

---

## 9. Technology Gap Summary

| Requirement | Apple pipeline | Human body | Current SOTA | Physics limit |
|-------------|---------------|-----------|--------------|---------------|
| Resolution (neural) | 10 μm | **1 μm** | 10 μm (inkjet) | ~100 nm |
| Resolution (somatic) | 10 μm | 5 μm | 10 μm (inkjet) | ~100 nm |
| Cell throughput | 10⁸ cells/s | **10¹⁰ cells/s** | ~10⁴ cells/s | >10¹² cells/s |
| Voxel throughput | 10⁸ voxels/s | **3.6 × 10¹¹ voxels/s** | ~10⁶ voxels/s | >10¹² voxels/s |
| Print heads | ~10⁵ nozzles | **10⁷ nozzles** | single head (~10³ nozzles) | unlimited |
| Print head area | 0.1 m² | **1 m² (at current density)** | ~10 cm² | — |
| Vascular construction | not needed | **required, 8 μm lumen** | 100 μm min lumen | 100 nm |
| Cell viability | 70% (current) | **>99% required** | ~70% | 100% |
| Multi-material types | 8 | ~200 cell types | 3–5 | — |

**Engineering gaps (human scale vs. current SOTA):**

| Metric | Gap | Gap type |
|--------|-----|----------|
| Resolution: neural | 10× (10 μm → 1 μm) | Engineering |
| Throughput | 10,000× (10⁴ → 10⁸ cells/s per head, ×10⁷ heads) | Engineering + scale |
| Vascular lumen | 10× (100 μm → 8 μm) | Engineering |
| Cell types supported | 40× (5 → 200) | Engineering |
| Fabrication viability | 1.4× (70% → 99%) | Engineering |

None of these is a fundamental physics barrier.

---

## 10. Fabricator Architecture

Based on the constraints above, a functionally complete human teleportation fabricator
requires the following design:

**Chamber:** ~2 m × 1 m × 2 m (human-scale workspace), maintained at 4°C.  
**Print head:** 1 m × 1 m array, 10⁷ nozzles at 10³ nozzles/cm² (100 μm pitch).  
Each nozzle: inkjet-style, 1 μm droplet precision, 1 kHz actuation.  
**Material supply:** ~200 cell-type reservoirs, pre-loaded with correct cell populations at 4°C.  
**Vascular system:** pre-loaded vascular scaffold deposited in each layer (dedicated nozzles).  
**Imaging feedback:** layer-by-layer optical verification against spec file (confocal or OCT).  
**Perfusion system:** connects to external oxygenated pump at fabrication end; warm
irrigation restores temperature from 4°C → 37°C over ~10 min.

**Fabrication sequence:**
1. Load spec file (~42 KB neural + ~10 GB somatic + ~10 GB immune/microbiome)
2. Begin layer-by-layer deposition at 4°C, starting from feet upward
3. Simultaneously deposit vascular scaffold in each layer (connected to external perfusion port)
4. Complete full-body deposition in 60 min
5. Connect external oxygenated circuit to vascular access port
6. Gradual rewarming over 10–20 min
7. Verify circulation, neural activity, and somatic function

---

## 11. Technology Readiness Level

Using NASA TRL scale (1–9):

| Component | TRL today | Required TRL | Barrier |
|-----------|-----------|-------------|---------|
| Single-nozzle bioprinting at 10 μm | 6 (demonstrated in labs) | 9 | scale-up |
| Single-nozzle at 1 μm | 3 (proof of concept) | 9 | engineering |
| Multi-nozzle array (10⁵ nozzles) | 4–5 | 9 | integration |
| Multi-nozzle array (10⁷ nozzles) | 2–3 | 9 | integration + cost |
| 200 cell-type support | 2 | 9 | bioengineering |
| Patent capillary printing (8 μm) | 2 | 9 | engineering |
| Layer-by-layer vascular connection | 1–2 | 9 | design + engineering |
| Full integrated system | 1 | 9 | all of the above |

The fabricator is at TRL 1–3 overall. The apple fabricator is at TRL 3–4.

---

## 12. Open Questions

1. **Capillary patent rate:** what fraction of printed 8 μm lumens are patent vs. collapsed?
   This determines whether hypothermic fabrication actually works or whether cells still die
   before perfusion is restored. Needs simulation of capillary lumen collapse dynamics.

2. **Immune cell loading:** lymphocytes have unique receptor repertoires (the immune
   "memory"). Printed lymphocytes must match the original repertoire. This adds ~1 GB
   to the spec but requires sourcing ~10⁹ matched lymphocytes — either from the original
   or from cloned/synthesized cells. This is a biology problem, not a fabricator problem.

3. **Gut microbiome:** ~10¹³ bacteria, ~1000 species. Currently ignored in the model.
   Adding microbiome reconstruction adds another 10–100 GB to the spec and requires a
   separate microbiome fabricator. Not a first-pass constraint.

4. **Print head contamination:** with 200 cell types in a shared environment, cross-
   contamination between nozzle reservoirs would corrupt cell-type assignment. Requires
   either physical separation of nozzle zones or rapid purging between cell types.

5. **Cell viability during 60-min cold storage:** cells in the pre-loaded reservoirs must
   survive at 4°C while waiting to be deposited. Standard cryopreservation handles hours
   to days; 60 min is straightforward. Not a barrier.

---

## Summary

The human teleportation fabricator requires:

- **Resolution:** 1 μm (neural), 5 μm (somatic)
- **Throughput:** 10¹⁰ cells/s = 10 billion cells per second
- **Architecture:** 1 m² print head array, 10 million nozzles, 60-minute fabrication at 4°C
- **Unique constraint:** patent vasculature must be restored within 60 min (hypothermic window)
- **Energy cost:** ~175 kWh ≈ $17.50 per teleportation event

No physics barriers. All gaps are engineering gaps:
- 10,000× throughput improvement (parallelization + nozzle density)
- 10× resolution improvement (nozzle miniaturization)
- Vascular printing at 8 μm lumen (MEMS fabrication)

The apple fabricator (TRL 3–4) is a tractable near-term target.
The human fabricator (TRL 1–3) requires a generational engineering program —
comparable in scale to semiconductor fab development, not comparable to basic research.

**Fabricator is confirmed as the binding constraint for the full teleportation program.**
Scanner (42 KB spec) and transmission (seconds) remain non-bottlenecks.
