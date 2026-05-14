# Direction 3: Quantum Cheshire Cat / Post-Selection — Analysis and Verdict

**Status:** Closed — post-selection constraint makes it non-exploitable for controllable transport  
**Result:** The effect is real but fundamentally passive. You cannot use it to send anything anywhere on demand.

---

## The Experiment

**Reference:** Denkmayr, T. et al. (2014). "Observation of a quantum Cheshire Cat in a matter-wave interferometer experiment." *Nature Communications*, 5, 4492. DOI: 10.1038/ncomms5492

A polarized neutron passes through a Mach-Zehnder interferometer with two arms. Using weak measurements and post-selection:

- The neutron's position (path through the interferometer) indicated it went through the **right arm**
- The neutron's spin was found in the **left arm**

A property of the particle was located where the particle itself was not. The experimenters called this a "quantum Cheshire cat" — the cat is gone but its grin remains.

This is experimentally real. The weak measurement results are statistically significant. This is not a matter of interpretation.

---

## Part 1: The Mathematical Framework (Two-State Vector Formalism)

The effect is best described in the Aharonov-Bergmann-Lebowitz (ABL) formalism (also called the two-state vector formalism, TSVF).

In standard quantum mechanics, a system's state is described by a forward-evolving state |ψ⟩ prepared by measurement. In the TSVF, a *post-selected* system is described by both:
- |ψ(t)⟩ — forward-evolving from preparation (pre-selection)
- ⟨φ(t)| — backward-evolving from post-selection

The **weak value** of observable A is:
```
⟨A⟩_w = ⟨φ|A|ψ⟩ / ⟨φ|ψ⟩
```

This is defined only in the post-selected ensemble (the subset of trials where the post-selection measurement gave the desired outcome).

### Setup for the Neutron Experiment

**Pre-selected state** (neutron enters with spin-up along z, in equal superposition of paths):
```
|ψ_i⟩ = |↑_z⟩ ⊗ (|L⟩ + |R⟩) / √2
```
where |L⟩, |R⟩ = left arm, right arm.

**Post-selected state** (specific combination selected by exit port + spin analyzer):
```
|ψ_f⟩ = (|↑_z⟩|R⟩ - |↓_z⟩|L⟩) / √2
```

(The actual post-selection in the experiment is chosen to maximize the Cheshire cat effect.)

**Weak value of path projection for right arm, Π_R = |R⟩⟨R|:**
```
⟨Π_R⟩_w = ⟨ψ_f|Π_R|ψ_i⟩ / ⟨ψ_f|ψ_i⟩

Numerator: ⟨ψ_f|Π_R|ψ_i⟩ = (1/2)(⟨↑_z|⟨R| - ⟨↓_z|⟨L|)(|R⟩⟨R|)(|↑_z⟩|L⟩ + |↑_z⟩|R⟩)/√2

Simplifying... ⟨Π_R⟩_w = 1
```

Neutron is "found" with probability 1 in the right arm (its path).

**Weak value of spin in the left arm, S_z^L = σ_z ⊗ |L⟩⟨L|:**
```
⟨S_z^L⟩_w = ⟨ψ_f|σ_z ⊗ |L⟩⟨L||ψ_i⟩ / ⟨ψ_f|ψ_i⟩ = ℏ/2  (non-zero)
```

The neutron's spin is "found" in the left arm with non-zero weak value — where the neutron's path is not.

### What Weak Values Are (and Aren't)

**What they are:**
- Statistical averages over a post-selected sub-ensemble
- The experimentally measurable shift in a weakly coupled pointer variable
- A property of the joint pre+post selected quantum state

**What they aren't:**
- Eigenvalues (weak values can be outside the spectrum of the operator, e.g., ⟨σ_z⟩_w = 100 is possible)
- Classical properties of the system at the time of measurement
- A statement that the spin "is" at that location in any classical sense

---

## Part 2: Can This Be Used for Transport?

The question for this project: is there any way to exploit this effect to controllably move a property from one location to another?

### The Post-Selection Trap

Every application of the Cheshire cat effect requires post-selection. You must:
1. Run the experiment many times
2. After each run, measure the post-selection observable
3. Keep only the runs where post-selection succeeded
4. In those runs, the weak value shows the dislocated property

**The fundamental problem:** You cannot choose in advance which runs will satisfy the post-selection. The post-selected ensemble is a *retroactively filtered subset* of a random process. You have no ability to force a specific run to land in that subset.

This is equivalent to saying: "I can send you a message by flipping a coin, and I'll keep only the flips that come up heads, and in that subset the message was heads." The message is in the post-selected data, but you had no control over which flips were heads.

**No-communication theorem compliance:** The TSVF is a reinterpretation of standard quantum mechanics. All probabilities and expectation values computed with the TSVF match standard QM. The no-communication theorem holds. No faster-than-light or backward-in-time information transfer is possible.

### The Information Content of Weak Measurements

Even in the post-selected ensemble, weak measurements carry limited information per trial.

A weak measurement of observable A uses a pointer variable (e.g., the deflection of a photon in the weak coupling regime). The pointer shift is:
```
Δp ≈ g × Re(⟨A⟩_w)
```

But the pointer has initial uncertainty σ_p >> g|⟨A⟩_w|. The measurement is "weak" precisely because the coupling g is small enough that the system isn't strongly disturbed. This means the signal-to-noise ratio per trial is << 1.

To extract the weak value with precision ε requires:
```
N_trials ≈ (σ_p / g)² / ε² = (signal-to-noise)⁻² / ε²
```

For the Denkmayr experiment: N ≈ 10⁴ neutron counts per data point. The information per trial is ~1/10,000 of a bit.

There is no regime where you get useful information faster via weak measurements than via strong measurements. The post-selected ensemble advantage is exactly cancelled by the information loss from the large pointer uncertainty.

### Scaling to Larger Properties

Could this be extended beyond spin? In principle, any quantum property has a weak value:
- Linear momentum ✓ — weak values of momentum can exceed classically expected values
- Angular momentum ✓ — can exceed ℏ/2
- Mass ✓ — in principle
- Position ✓ — the "quantum trajectory" studies use this

But scaling these to macroscopic properties runs into the same post-selection problem, amplified by decoherence. A macroscopic superposition collapses before the weak measurement + post-selection protocol can be executed (see Direction 4).

---

## Part 3: The "Quantum Cheshire Cat as Teleportation" Claim

Some popular science articles have suggested the Cheshire cat experiment represents a form of teleportation (the spin teleported to the other arm). Let's be clear about what this would mean:

**What the experiment shows:** In post-selected trials, a weak perturbation applied to the spin in the left arm produces an outcome consistent with spin-up in the left arm, even though the neutron's path is in the right arm.

**What this is NOT:**
- The spin did not travel from the neutron to the left arm. The neutron was prepared in a superposition that included the left arm; the post-selection filtered for a subensemble where the left-arm amplitude contributed.
- No information was transmitted from right arm to left arm. The experimenter applied weak interactions to both arms independently and collected data afterward.
- No "copy" of the spin was created at the left arm. The weak value is a property of an ensemble, not a definite state at a single trial.

---

## Verdict

**Direction 3 is closed.**

The quantum Cheshire cat is a genuine quantum phenomenon that reveals the contextuality of quantum mechanics and the power of weak measurements. It is not a transport mechanism.

The reasons it cannot be used for teleportation:
1. **Post-selection is passive** — you cannot force outcomes into the post-selected subset
2. **Information per trial is negligible** — the weak coupling required gives ~1/N information per trial where N is the number of trials needed for statistical significance
3. **No-communication theorem** — TSVF is equivalent to standard QM; causality is preserved
4. **Decoherence** — for macroscopic properties, decoherence destroys the interference required before post-selection can be applied

**What to carry forward:** The TSVF formalism and weak measurement theory are legitimate tools. The idea that quantum systems can exhibit "disembodied properties" is real and interesting. But it does not provide a mechanism for transport. The phenomenon is a window into quantum contextuality, not a door to teleportation.
