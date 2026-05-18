# Direction 1 — Capillary Lumen Patency under Hypothermic Fabrication

## Question

The fabricator model (`math/direction1_fabricator.md`) assumes a 60-minute
fabrication window at 4 °C, justified by the established DHCA (deep
hypothermic circulatory arrest) tolerance in cardiac surgery. But DHCA in
surgery has blood-filled vessels at zero flow. The fabrication context is
**different**: the body is being built voxel-by-voxel, and capillaries are
empty until perfusion begins. Will an 8 μm capillary lumen stay open during
the gap between "vasculature deposited" and "perfusion started"?

If the lumen collapses, no fluid can be re-infused; the tissue dies of
ischemia. This question gates whether the fabricator approach survives
beyond the slab/single-organ scale.

## Forces acting on a capillary lumen

A capillary segment with radius R = 4 μm (diameter 8 μm) is a thin-walled
cylinder embedded in viscoelastic tissue. Forces normal to the wall:

1. **Internal pressure P_in** (from any fluid inside the lumen).
2. **External pressure P_ext** (from surrounding tissue, ECM stiffness,
   adjacent cell turgor).
3. **Wall tension T_wall** (endothelial cytoskeleton + basement membrane).
4. **Surface tension γ** at any air-fluid interface within the lumen.

Equilibrium for an open cylinder:
```
P_in − P_ext + (T_wall / R) − (γ_meniscus / R_meniscus) = 0
```

In the fabricator: the print head deposits cells in a saline carrier, so
**no air enters the lumen**. The γ term is zero (saline-saline interface
has γ ≈ 0). This is critical and not always true in tissue handling — the
DHCA-window assumption breaks immediately if air bubbles enter.

So in the fabricator the patency condition reduces to:
```
P_in + (T_wall / R) ≥ P_ext
```

## External tissue pressure

ECM stiffness at 4 °C (no active cytoskeleton): elastic modulus E ≈ 1 kPa
(measured by AFM on soft tissue, Janmey & Miller 2011).

For a void of radius R within an elastic medium, the inward closure pressure
from Mooney-Rivlin elasticity is approximately:
```
P_ext ≈ E · (Δ_local strain) ≈ E · (compression of surroundings)
```

If the surrounding tissue is at zero strain (just-printed, no compaction),
P_ext = 0. The lumen has no external compressive force.

If the tissue compacts under gravity during the build (worst case for an
upright print), the hydrostatic component is ρ g h. For h = 1 m of body
tissue: P_grav = 1060 kg/m³ × 9.81 m/s² × 1 m ≈ 10.4 kPa.

So the upper-bound P_ext ≈ 10 kPa.

## Internal saline pressure

The fabricator deposits cells in a carrier saline at hydrostatic pressure
from the printer reservoir. If the reservoir sits 1.5 m above the build
plate (modest plumbing): P_in = 1000 kg/m³ × 9.81 m/s² × 1.5 m = 14.7 kPa.

Wall tension at 4 °C: endothelial cells are quiescent (no actomyosin
contraction), so T_wall is dominated by the passive basement membrane
collagen IV mesh. T_wall ≈ E · h · R for a thin shell — taking h = 100 nm
basement membrane, E = 1 MPa: T_wall = 10⁶ × 10⁻⁷ × 4×10⁻⁶ ≈ 4×10⁻⁷ N/m.
T_wall/R ≈ 100 Pa. Negligible compared to P_in.

So the dominant balance is:
```
P_in ≈ 15 kPa  >  P_ext ≈ 10 kPa  (margin of 50%)
```

**Lumen stays open** under simple hydrostatic balance, with margin.

## Viscoelastic relaxation timescale

Even if P_in slightly exceeds P_ext, what's the timescale for tissue creep
to close the gap?

The Maxwell relaxation time of cytoplasm at 37 °C: τ_M ≈ 10 s
(Bausch et al. 1998, magnetic bead microrheology).

Temperature dependence: τ_M ∝ η (viscosity) ∝ exp(E_a / k_B T).
With E_a ≈ 30 kJ/mol for water-based cytoplasm (activation energy ~7 k_B T):
```
τ_M(4 °C) / τ_M(37 °C) = exp(E_a / R · (1/277 − 1/310))
                       = exp(30000 / 8.314 · (3.61e-3 − 3.23e-3))
                       = exp(1.37) ≈ 3.9
```

So at 4 °C: τ_M ≈ 40 s. Slow but not extremely slow.

ECM (collagen network) relaxation time is much longer: τ_collagen ≈
1000 − 10000 s (Pryse et al. 2003, tendon viscoelasticity). At 4 °C this
extends to ~3 × 10⁴ s ≈ 8 hours.

**The dominant tissue relaxation that could close the lumen is ECM creep,
with τ ≈ 8 hours at 4 °C, well beyond the 60-minute fabrication window.**

## Required perfusion start time

After fabrication completes (60 min), perfusion must start before
significant ECM creep closes the lumens. Margin:
  fabrication window: 60 min
  ECM creep timescale: ~480 min at 4 °C
  Safety factor: 8×

Cells in a 4 °C saline-perfused lumen survive at least 60 minutes (standard
DHCA window). So the total cold-ischemia tolerance is:
  60 min build + 60 min perfusion ramp-up + warming = ~3 hours.
  Within the 8-hour ECM-creep limit.

## Failure modes

1. **Air ingress**: any air bubble in the lumen produces γ/R ≈ 18 kPa
   inward pressure (saline γ ≈ 72 mN/m, R = 4 μm). This exceeds the
   hydrostatic margin and pinches the lumen closed. **Critical engineering
   requirement: bubble-free perfusion throughout the fabrication.**

2. **Local print misalignment**: a misprinted endothelial cell that protrudes
   into the lumen could nucleate collapse. Modeled by Murray's law deviations;
   simulation outside this scope.

3. **Reservoir pressure loss**: if the carrier saline reservoir drops below
   10 kPa head, ECM compression starts to close lumens. **Engineering
   requirement: pressure-regulated reservoir, minimum 1.5 m head.**

## Conclusion

Capillary patency during the 60-minute hypothermic fabrication is achievable
under three engineering requirements:

| Requirement | Spec |
|---|---|
| Bubble-free saline carrier | strict (no air interfaces in lumens) |
| Reservoir head pressure | ≥ 1.5 m (15 kPa) |
| Fabrication temperature | ≤ 4 °C throughout |

Under these, the patency physics has an 8× safety margin (60 min < 480 min
ECM creep timescale at 4 °C). The DHCA-window assumption transfers from
cardiac surgery to fabricator-built vasculature.

**The fabricator-side vascular constraint is not a physics barrier. It is
a fluidics engineering specification.**

## Open

A full 3D simulation of capillary collapse dynamics under realistic
print-head deposition rates would close the question rigorously. Force-
balance analysis here gives the order-of-magnitude answer. Detailed CFD
(e.g. with finite-element soft-tissue model around a perfused lumen) is
left for the engineering team that builds the actual fabricator.
