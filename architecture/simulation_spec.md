# Testable Simulation Specification

**Status:** Active — Phase 7  
**Goal:** A simulation that produces concrete, falsifiable predictions about functional teleportation feasibility — predictions that can be tested against real data or near-term experiments.

This is not a toy model. The predictions must be specific enough to be wrong.

---

## What "Testable" Means Here

A testable prediction has the form:
> "If we corrupt the C. elegans connectome by distorting synaptic weights by σ%, then behavior metric B will change by X% ± Y%."

This can be verified by:
1. Running the simulation with and without distortion
2. Comparing to actual C. elegans behavior recordings
3. Checking whether the prediction of functional equivalence holds at the predicted distortion threshold

If the simulation predicts that 30% weight distortion is functionally transparent, and actual C. elegans with lesioned synapses behaves differently, the prediction is falsified. This is useful — it either validates the rate-distortion assumptions or forces us to revise them.

---

## Simulation 1: C. elegans Connectome Distortion Test

### Why C. elegans

- Complete connectome published (White et al. 1986, updated Cook et al. 2019): 302 neurons, 6,393 chemical synapses, 890 gap junctions
- Wiring diagram is deterministic enough to be modeled neuron-by-neuron
- Behavior is well-characterized: locomotion (forward/backward), chemotaxis, thermotaxis, tap-withdrawal reflex, egg-laying
- Neural dynamics models exist: Izhikevich or leaky-integrate-and-fire at single-neuron resolution
- Published data: OpenWorm project (openworm.org) has a full simulation; WormAtlas has anatomy + behavior correlations

### Simulation Architecture

```
Input:    C. elegans connectome (adjacency matrix W, 302×302 chemical + gap junction)
Model:    Leaky integrate-and-fire (LIF) network
          τ dV/dt = -V + Σⱼ wᵢⱼ × f(Vⱼ) + I_ext(t)
Output:   Neural activity traces r(t), behavioral predictions (locomotion direction, speed)
```

**Parameters:**
- Membrane time constant τ = 10 ms (standard for C. elegans interneurons)
- Synaptic weight matrix W from published connectome (Cook et al. 2019)
- Sensory input I_ext(t) = simulated chemotaxis gradient or tap stimulus
- Output: muscle activation → locomotion via published neuromuscular connectivity

### The Distortion Experiment

**Procedure:**
1. Run baseline simulation with original W → record behavior B_0(t)
2. Add Gaussian noise: W_noisy = W + ε, where ε ~ N(0, σ²_W × D) for distortion fraction D
3. Run simulation with W_noisy → record behavior B_D(t)
4. Compute behavioral divergence: d(B_0, B_D) = KL divergence between behavior distributions
5. Repeat for D = {1%, 5%, 10%, 20%, 30%, 50%, 100%}
6. Plot: functional distortion d vs. weight distortion D

**Prediction from rate-distortion analysis:**
The 30% distortion threshold (D = 0.30) should be near or below the behavioral discrimination threshold — i.e., d(B_0, B_30%) should be small compared to natural C. elegans behavior variability across individuals.

**Falsifiable prediction:** If d(B_0, B_30%) > natural inter-individual behavioral variation, the 30% distortion assumption is too optimistic and the rate-distortion bound must be recalculated with a tighter D.

### d_eff Extraction from C. elegans

**Procedure:**
1. Take the 302×302 weight matrix W (flattened: ~45,000 non-zero entries after symmetry)
2. For each published connectome reconstruction of C. elegans (multiple worms measured separately — at least 2 from White 1986, plus Cook 2019 and others)
3. Compute the inter-individual weight variation matrix: ΔW_ij = W_worm2,ij - W_worm1,ij
4. Apply PCA to the set of connectome matrices
5. Plot cumulative variance explained vs. number of principal components → this gives d_eff for C. elegans

**Expected result:** The C. elegans connectome dimensionality d_eff(C. elegans) gives an anchor point for estimating d_eff(human) via scaling laws.

**Scaling law hypothesis:** If d_eff scales as N^α where N = neuron count, then:
```
d_eff(human) / d_eff(C. elegans) ≈ (86 × 10⁹ / 302)^α
```

For α = 0.5 (square root scaling, conservative): d_eff(human) ≈ d_eff(C. elegans) × 17,000  
For α = 1.0 (linear scaling): d_eff(human) ≈ d_eff(C. elegans) × 2.8 × 10⁸

If d_eff(C. elegans) = 50 (purely as an example — to be measured):
- α = 0.5: d_eff(human) ≈ 850,000
- α = 1.0: d_eff(human) ≈ 1.4 × 10¹⁰

This is a testable calibration for the critical unknown (d_eff of the human connectome).

---

## Simulation 2: Rate-Distortion Curve Verification

### What We're Testing

The Shannon R-D bound assumes the connectome has a specific statistical structure (Gaussian weights, known correlation structure). We're testing whether this assumption is correct.

**Procedure:**
1. Take C. elegans weight matrix W
2. Fit a Gaussian model to the weight distribution
3. Compute the theoretical R-D curve: R(D) = d_eff × (1/2) log₂(σ²/D)
4. Independently: compress W using standard codecs (JPEG-equivalent for matrices: DCT + quantization; or neural network-based compression) at various bit rates
5. Measure the behavioral distortion at each compression level
6. Compare empirical R-D curve (from simulation) to theoretical Shannon bound

**Expected outcome:** The empirical curve should approach (but not exceed) the Shannon bound. If empirical compression achieves lower distortion than the bound predicts at a given bit rate, there's something wrong with the model. If it achieves higher distortion, the bound is correct but achievable — it's a lower bound, after all.

**Why this matters:** This validates or refutes the assumption that the Gaussian R-D formula applies to the connectome. If the connectome has heavier-tailed weight distributions or different correlation structures, the bound changes.

---

## Simulation 3: Two-Tier Scan Fidelity Test

### Testing the Generative Model Approach

**Procedure:**
1. **Ground truth:** C. elegans full structural connectome W (known)
2. **Functional "recording":** Simulate the LIF model under diverse stimuli, record activity traces r(t)
3. **Generative model:** Train a neural network G to predict W from r(t): Ŵ = G(r(t))
4. **Reconstruction fidelity:** Measure ||W - Ŵ||² / ||W||² (fractional error)
5. **Behavioral test:** Run the reconstructed connectome Ŵ in the simulator, compare behavior to original W
6. **Vary training data:** Test how much functional recording is needed (how many neurons, how long, how many stimuli) before Ŵ converges to within the rate-distortion bound

**The key question this answers:** Can a generative model that only sees activity patterns (not structure) predict the structural connectome well enough for functional reconstruction?

**Falsifiable prediction:** There exists a finite amount of functional recording R* such that for all recordings of duration > R*, G(r(t)) achieves d_eff-dimensional accuracy within the rate-distortion bound. If no such R* exists (the generative model never converges), the two-tier approach fails.

---

## Implementation Plan

### Phase 7A: C. elegans Baseline Simulation

**Inputs:**
- Cook et al. 2019 connectome data (available: https://www.wormbase.org/, doi:10.1038/s41586-019-1352-7)
- WormAtlas neuromuscular connectivity (wormbase.org)

**Tools:** Python + NumPy + SciPy. The LIF model is ~50 lines of code.

**Output:** Verified simulation matching known C. elegans behaviors (tap-withdrawal, chemotaxis)

**Estimated effort:** 1–2 weeks

### Phase 7B: Distortion Experiments

**Inputs:** Phase 7A simulator + distorted weight matrices

**Output:** d(B_0, B_D) vs D curve — the empirical behavioral R-D function

**Estimated effort:** 2–4 weeks (mostly running experiments and analyzing)

### Phase 7C: d_eff Extraction

**Inputs:** Multiple C. elegans connectome datasets (White 1986, Cook 2019, + any others available)

**Output:** d_eff(C. elegans) + confidence interval

**Estimated effort:** 1 week (data is available, PCA is standard)

### Phase 7D: Generative Model

**Inputs:** Phase 7A simulation runs, connectome ground truth

**Tools:** PyTorch or JAX. Standard supervised learning.

**Output:** G(r(t)) → Ŵ with measured reconstruction fidelity

**Estimated effort:** 4–8 weeks

---

## What the Simulation Does and Does Not Prove

### What it proves (if predictions hold):

1. Functional equivalence at 30% weight distortion is achievable in C. elegans — concrete evidence that the rate-distortion assumption is not wildly off
2. d_eff for C. elegans is measurable — gives a calibration point for the human estimate
3. A generative model can recover structural weights from activity — validates the two-tier scan approach
4. The information-theoretic approach to teleportation is internally consistent

### What it does not prove:

1. That human brains work the same way as C. elegans (302 neurons vs. 86 billion — the scaling is unverified)
2. That the reconstruction technology can be built
3. That reconstructed identity is "the same person" (philosophical question, outside the scope)

### The next falsification target (post-simulation):

After C. elegans validation, the natural next step is Drosophila — 140,000 neurons, completed connectome (Flywire project 2023). This is 450× larger and more complex, and validates the scaling hypothesis.

---

## Predictions Summary

| Prediction | Can be tested with | Falsifies if |
|-----------|-------------------|-------------|
| d(B_0, B_30%) < natural C. elegans variation | C. elegans LIF simulation | Behavior changes significantly at 30% distortion |
| d_eff(C. elegans) << N_synapses | PCA on multiple connectomes | Connectome variance spans full N_synapses dimensions |
| G(r(t)) → Ŵ within R-D bound | Generative model training | Model fails to predict weights from activity |
| R-D curve approaches Shannon bound | Compression + behavior test | Empirical curve far above theoretical bound |
| d_eff scales as N^α | C. elegans + Drosophila comparison | Scaling law inconsistent between organisms |

All five predictions are falsifiable with existing or near-existing technology and data. None require building the full reconstruction system.
