"""
Phase 7B: Distortion experiment.

For each distortion level D (fraction of std), corrupt the weight matrix W
and measure the behavioral divergence: how different is the resulting
population activity from the original?

Behavioral metric: cosine similarity between activity vectors.
  sim(r_orig, r_dist) = dot(r_orig, r_dist) / (|r_orig| * |r_dist|)

Divergence: 1 - sim (ranges from 0=identical to 2=opposite)

Run for two stimuli (tap and chem), across D = 0..1.0.

Outputs:
  simulation/results/distortion_results.npz
  simulation/results/distortion_curve.png
  simulation/results/distortion_summary.txt
"""

import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd, re

sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")

from simulation.load_connectome import load_connectome
from simulation.rate_model import RateParams, simulate_rate, make_tap_input, make_chem_input

os.makedirs("simulation/results", exist_ok=True)

print("Loading connectome...")
W_raw, neurons, W_norm = load_connectome()
N = len(neurons)

# Build G_norm
path = "simulation/data/SI5_connectome_adjacency.xlsx"
df_g = pd.read_excel(path, sheet_name="hermaphrodite gap jn symmetric", header=None)
isn = lambda x: bool(re.match(r'^[A-Z][A-Z0-9]{1,6}$', str(x).strip())) if isinstance(x,str) else False
cn=df_g.iloc[2,3:].values; rn=df_g.iloc[3:,2].values
ci=[i+3 for i,n in enumerate(cn) if isn(str(n).strip())]
ri=[i+3 for i,n in enumerate(rn) if isn(str(n).strip())]
cn2=[str(cn[i-3]).strip() for i in ci]; rn2=[str(rn[i-3]).strip() for i in ri]
dg=df_g.iloc[ri,:].iloc[:,ci].fillna(0).astype(float); dg.index=rn2; dg.columns=cn2
gc=sorted(set(rn2)&set(cn2)); G_full=dg.loc[gc,gc].values.astype(float)
gs=set(gc); G_aligned=np.zeros((N,N))
for i,ni in enumerate(neurons):
    for j,nj in enumerate(neurons):
        if ni in gs and nj in gs: G_aligned[i,j]=G_full[gc.index(ni),gc.index(nj)]
G_norm = G_aligned / (G_aligned.max() or 1.0)

# Parameters tuned for moderate activity propagation
params = RateParams(tau=10.0, gain=2.5, w_chem=0.25, w_gap=0.1, dt=0.5)
T_ms = 600.0

print(f"Network: {N} neurons,  {(W_norm>0).sum()} chemical,  {(G_norm>0).sum()} gap junctions")
print(f"Params: gain={params.gain}, w_chem={params.w_chem}, w_gap={params.w_gap}, T={T_ms}ms")

# --- Run baseline simulations ---
I_tap  = make_tap_input(N, neurons, T_ms, params.dt, onset_ms=50.0, duration_ms=30.0, amplitude=4.0)
I_chem = make_chem_input(N, neurons, T_ms, params.dt, amplitude=3.0)

print("Running baseline tap...")
res0_tap  = simulate_rate(W_norm, G_norm, I_tap,  T_ms, params)
print("Running baseline chem...")
res0_chem = simulate_rate(W_norm, G_norm, I_chem, T_ms, params)

# Response window: 100-500ms
win_s = int(100/params.dt); win_e = int(500/params.dt)
r0_tap  = res0_tap["r"][win_s:win_e].flatten()
r0_chem = res0_chem["r"][win_s:win_e].flatten()

print(f"Baseline tap   active: {(res0_tap['r_mean']>0.02).sum()}/{N}")
print(f"Baseline chem  active: {(res0_chem['r_mean']>0.02).sum()}/{N}")

# --- Distortion sweep ---
# Distortion levels: fraction of per-synapse std of W_norm
W_std = W_norm[W_norm > 0].std()
W_mean = W_norm[W_norm > 0].mean()
print(f"\nW_norm stats (nonzero): mean={W_mean:.4f}, std={W_std:.4f}")

distortion_levels = np.array([0.0, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.75, 1.0])
n_trials = 20  # average over noise realizations

def cosine_sim(a, b):
    na = np.linalg.norm(a); nb = np.linalg.norm(b)
    if na < 1e-10 or nb < 1e-10: return 0.0
    return np.dot(a, b) / (na * nb)

divergence_tap  = []
divergence_chem = []
divergence_tap_std  = []
divergence_chem_std = []

rng = np.random.default_rng(1337)

for D in distortion_levels:
    sim_tap_trials = []
    sim_chem_trials = []

    for trial in range(n_trials if D > 0 else 1):
        if D == 0:
            W_d = W_norm.copy()
        else:
            # Add Gaussian noise proportional to D * local weight magnitude
            # (noise on each synapse proportional to its own weight -- biological noise model)
            noise = rng.standard_normal(W_norm.shape) * D * W_norm
            W_d = np.clip(W_norm + noise, 0, None)  # keep non-negative
            # Zero out connections that were zero in original (don't add false synapses)
            W_d[W_norm == 0] = 0.0

        res_tap  = simulate_rate(W_d, G_norm, I_tap,  T_ms, params)
        res_chem = simulate_rate(W_d, G_norm, I_chem, T_ms, params)

        r_tap  = res_tap["r"][win_s:win_e].flatten()
        r_chem = res_chem["r"][win_s:win_e].flatten()

        sim_tap_trials.append(cosine_sim(r0_tap, r_tap))
        sim_chem_trials.append(cosine_sim(r0_chem, r_chem))

    divergence_tap.append(1.0 - np.mean(sim_tap_trials))
    divergence_chem.append(1.0 - np.mean(sim_chem_trials))
    divergence_tap_std.append(np.std(sim_tap_trials))
    divergence_chem_std.append(np.std(sim_chem_trials))

    print(f"D={D:.2f}: tap div={divergence_tap[-1]:.4f} +/- {divergence_tap_std[-1]:.4f}  "
          f"chem div={divergence_chem[-1]:.4f} +/- {divergence_chem_std[-1]:.4f}")

divergence_tap = np.array(divergence_tap)
divergence_chem = np.array(divergence_chem)
divergence_tap_std = np.array(divergence_tap_std)
divergence_chem_std = np.array(divergence_chem_std)

# --- Save results ---
np.savez("simulation/results/distortion_results.npz",
         distortion_levels=distortion_levels,
         divergence_tap=divergence_tap, divergence_chem=divergence_chem,
         divergence_tap_std=divergence_tap_std, divergence_chem_std=divergence_chem_std,
         r0_tap=r0_tap, r0_chem=r0_chem, neurons=neurons)

# --- Find threshold: D at which divergence > natural inter-trial variability ---
# "Natural variability" = divergence at D=0 (same connectome, deterministic) is 0
# We estimate natural variability as the divergence at very small D (D=0.05)
thresh_tap  = distortion_levels[np.where(divergence_tap  > 0.05)[0][0]] if (divergence_tap  > 0.05).any() else ">1.0"
thresh_chem = distortion_levels[np.where(divergence_chem > 0.05)[0][0]] if (divergence_chem > 0.05).any() else ">1.0"

# --- Plot ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

for ax, div, div_std, title, thresh in [
    (axes[0], divergence_tap,  divergence_tap_std,  "Tap Withdrawal", thresh_tap),
    (axes[1], divergence_chem, divergence_chem_std, "Chemotaxis",     thresh_chem),
]:
    ax.fill_between(distortion_levels, div - div_std, div + div_std, alpha=0.25, color="steelblue")
    ax.plot(distortion_levels, div, "o-", color="steelblue", lw=2, label="mean divergence")
    ax.axvline(0.30, color="red", ls="--", lw=1.5, label="30% threshold (rate-distortion prediction)")
    ax.axhline(0.05, color="gray", ls=":", lw=1.5, label="5% divergence threshold")
    ax.set_xlabel("Weight distortion level D (fraction of weight)")
    ax.set_ylabel("Behavioral divergence (1 - cosine similarity)")
    ax.set_title(f"{title} — Behavioral Divergence vs Distortion")
    ax.legend(fontsize=8)
    ax.set_xlim(0, 1.0); ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("simulation/results/distortion_curve.png", dpi=150)
plt.close()
print("\nSaved: simulation/results/distortion_curve.png")

# --- Summary ---
summary = f"""C. elegans Distortion Experiment — Phase 7B
============================================
Network: {N} neurons, {(W_norm>0).sum()} connections
Model params: gain={params.gain}, w_chem={params.w_chem}, w_gap={params.w_gap}
Trials per distortion level: {n_trials}
Noise model: W_distorted = W_original + N(0, D^2 * W^2) per synapse (multiplicative)

Behavioral metric: 1 - cosine_similarity(r_original[t], r_distorted[t])
                   over response window 100-500ms

RESULTS:
D      Tap div    +/-      Chem div   +/-
{''.join(f'{d:.2f}   {dt:.4f}     {dts:.4f}    {dc:.4f}     {dcs:.4f}' + chr(10) for d,dt,dts,dc,dcs in zip(distortion_levels,divergence_tap,divergence_tap_std,divergence_chem,divergence_chem_std))}

Divergence > 5% threshold:
  Tap withdrawal: D = {thresh_tap}
  Chemotaxis:     D = {thresh_chem}

Rate-distortion analysis prediction: D = 0.30 is functionally tolerable.
This means divergence at D=0.30 should be small (below natural variability threshold).

PREDICTION STATUS at D=0.30:
  Tap:  div = {divergence_tap[distortion_levels==0.30][0]:.4f}  -> {'CONFIRMED: small divergence' if divergence_tap[distortion_levels==0.30][0] < 0.10 else 'CHALLENGED: divergence exceeds 10%'}
  Chem: div = {divergence_chem[distortion_levels==0.30][0]:.4f} -> {'CONFIRMED: small divergence' if divergence_chem[distortion_levels==0.30][0] < 0.10 else 'CHALLENGED: divergence exceeds 10%'}

NOTE: C. elegans has only 300 neurons. The 30% threshold was derived from mammalian
in-vivo neural noise (Fano factor ~1). C. elegans neurons may be less noisy,
suggesting the actual functional threshold might be lower for C. elegans.
This is a testable refinement: compare predicted threshold to observed divergence
in actual C. elegans with synaptic weight perturbations.
"""

print(summary)
with open("simulation/results/distortion_summary.txt", "w", encoding="utf-8") as f:
    f.write(summary)
