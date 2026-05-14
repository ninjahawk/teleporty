"""
d_eff analysis for mouse cortex (MICrONS mm3, portion 65).
~50,943 neurons, 7.5 million synapses, mouse V1.

Adds third data point to the scaling law: C. elegans -> Drosophila -> Mouse
"""

import os, sys, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import sparse
from sklearn.utils.extmath import randomized_svd
import h5py

sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")

os.makedirs("simulation/results", exist_ok=True)

print("Loading MICrONS mm3 connectome...")
path = "simulation/data/microns_mm3_connectome.h5"
with h5py.File(path, "r") as f:
    edge_idx = f["connectivity/condensed/edge_indices/block0_values"][:]
    weights  = f["connectivity/condensed/edges/block0_values"][:].flatten().astype(float)

# Map to contiguous indices
all_ids = np.unique(edge_idx)
N = len(all_ids)
id2i = {nid: i for i, nid in enumerate(all_ids)}
pre_i  = np.array([id2i[x] for x in edge_idx[:, 0]])
post_i = np.array([id2i[x] for x in edge_idx[:, 1]])

w_max = weights.max()
w_norm = weights / w_max
print(f"N={N}, edges={len(edge_idx)}, max_w={w_max:.0f}, mean_w={weights.mean():.2f}")

W = sparse.csr_matrix((w_norm, (pre_i, post_i)), shape=(N, N))
total_var = W.power(2).sum()
print(f"Sparse matrix: {W.shape}, nnz={W.nnz}, density={W.nnz/N**2:.2e}")

# --- Randomized SVD k=2000 ---
print("\nComputing SVD k=2000...")
t0 = time.time()
U, S, Vt = randomized_svd(W, n_components=2000, random_state=42, n_iter=3)
print(f"  Done in {time.time()-t0:.1f}s")
eig = S**2
var_captured = eig.sum() / total_var
d_eff_2000 = eig.sum()**2 / (eig**2).sum()
print(f"  Top 2000 variance: {100*var_captured:.1f}%")
print(f"  PR d_eff (top 2000): {d_eff_2000:.1f}")

# Tail power law
k_fit = 500
log_i = np.log(np.arange(1501, 2001))
log_e = np.log(eig[1500:2000] + 1e-30)
slope = np.polyfit(log_i, log_e, 1)
beta_tail = -slope[0]
C_tail = np.exp(slope[1])
print(f"  Tail power law: lambda ~ {C_tail:.2e} * i^(-{beta_tail:.3f})")

# Estimate full d_eff with power law tail
i_ext = np.arange(2001, N+1)
lam_tail = C_tail * i_ext**(-beta_tail)
eig_full = np.concatenate([eig, lam_tail])
d_eff_full = eig_full.sum()**2 / (eig_full**2).sum()
var_tail = lam_tail.sum() / total_var
print(f"  Tail variance (2001 to N): {100*var_tail:.1f}%")
print(f"  Estimated full d_eff: {d_eff_full:.1f}")

# Save eigenvalues
np.save("simulation/results/mouse_eig_2000.npy", eig)

# --- Scaling law: three points ---
print("\n--- Three-organism scaling law ---")
data_points = [
    ("C. elegans", 302,    28.0),
    ("Drosophila", 138639, 700.0),
    ("Mouse V1",   N,      d_eff_full),
]

for name, n, d in data_points:
    print(f"  {name}: N={n:,}, d_eff={d:.1f}")

# Fit power law to all three points
Ns = np.array([p[1] for p in data_points], dtype=float)
Ds = np.array([p[2] for p in data_points], dtype=float)
log_N = np.log(Ns)
log_D = np.log(Ds)
coeffs = np.polyfit(log_N, log_D, 1)
alpha_fit = coeffs[0]
C_scale = np.exp(coeffs[1])
print(f"\nFitted scaling: d_eff = {C_scale:.3f} * N^{alpha_fit:.4f}")

# Residuals
for name, n, d in data_points:
    d_pred = C_scale * n**alpha_fit
    print(f"  {name}: measured={d:.1f}, predicted={d_pred:.1f}, ratio={d/d_pred:.2f}")

# Human estimate
N_human = 86e9
d_eff_human = C_scale * N_human**alpha_fit
R_human = d_eff_human * 1.74
print(f"\nHuman (N={N_human:.0e}):")
print(f"  d_eff ~ {d_eff_human:.3e}")
print(f"  R(D=30%) ~ {R_human:.3e} bits  ({R_human/8e3:.0f} KB)")

# --- Plot ---
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Eigenspectrum comparison
fly_eig = np.load("simulation/results/fly_eig_3000.npy")
elegans_data = np.load("simulation/results/deff_results.npz")
elegans_eig = elegans_data["eigenvalues"]

for ax_eig, eig_data, label, color in [
    (axes[0], elegans_eig/elegans_eig[0], "C. elegans (N=302)", "steelblue"),
    (axes[0], fly_eig/fly_eig[0],          "Drosophila (N=138k)", "forestgreen"),
    (axes[0], eig/eig[0],                  "Mouse V1 (N=51k)", "darkorange"),
]:
    axes[0].semilogy(np.arange(1, len(eig_data)+1), eig_data, "-", color=color, lw=1.5, label=label)
axes[0].set_xlabel("Principal component rank")
axes[0].set_ylabel("Normalized eigenvalue")
axes[0].set_title("Eigenspectrum comparison\n(three organisms)")
axes[0].legend(fontsize=8)
axes[0].grid(True, alpha=0.3, which="both")
axes[0].set_xlim(1, 500)

# Cumulative variance
fly_cumvar = np.load("simulation/results/fly_cumvar_3000.npy")
elegans_cumvar = elegans_data["cumvar"]
mouse_cumvar = np.cumsum(eig) / total_var

axes[1].plot(np.arange(1, len(elegans_cumvar)+1), elegans_cumvar*100, "b-",  lw=2, label=f"C. elegans (d_eff=28)")
axes[1].plot(np.arange(1, len(fly_cumvar)+1),     fly_cumvar*100,     "g-",  lw=2, label=f"Drosophila (d_eff~700)")
axes[1].plot(np.arange(1, len(mouse_cumvar)+1),   mouse_cumvar*100,   "o-",  lw=2, label=f"Mouse V1 (d_eff~{d_eff_full:.0f})", markersize=0)
axes[1].axhline(75, color="gray", ls=":", lw=1)
axes[1].axhline(90, color="gray", ls="--", lw=1)
axes[1].set_xlabel("Number of principal components")
axes[1].set_ylabel("Cumulative variance (%)")
axes[1].set_title("Variance explained — three organisms")
axes[1].legend(fontsize=7)
axes[1].grid(True, alpha=0.3)
axes[1].set_xlim(0, 2000)

# Scaling law
N_range = np.logspace(2, 11, 300)
d_range = C_scale * N_range**alpha_fit
axes[2].loglog(N_range, d_range, "k-", lw=2, label=f"Fit: d_eff={C_scale:.2f}*N^{alpha_fit:.3f}")
# Individual alpha references
for a, col, ls in [(0.33, "gray", ":"), (0.5, "blue", "--"), (0.67, "red", "--")]:
    C_a = Ds[0] / Ns[0]**a
    axes[2].loglog(N_range, C_a*N_range**a, ls=ls, color=col, lw=1, alpha=0.6, label=f"alpha={a}")
# Data points
colors_pts = ["steelblue", "forestgreen", "darkorange"]
for (name, n, d), col in zip(data_points, colors_pts):
    axes[2].scatter([n], [d], s=100, c=col, zorder=5)
    axes[2].annotate(name, (n, d), textcoords="offset points", xytext=(5, 5), fontsize=8)
# Human
axes[2].scatter([N_human], [d_eff_human], s=150, c="purple", marker="*", zorder=5,
                 label=f"Human: {d_eff_human:.1e}")
axes[2].axvline(N_human, color="purple", ls=":", lw=1.5)
axes[2].axhspan(1e10, 1e12, alpha=0.08, color="red", label="Original assumption")
axes[2].set_xlabel("Neuron count N")
axes[2].set_ylabel("d_eff")
axes[2].set_title(f"Three-organism scaling law\nalpha={alpha_fit:.3f}")
axes[2].legend(fontsize=7)
axes[2].grid(True, alpha=0.3, which="both")

plt.suptitle("d_eff Scaling: C. elegans -> Drosophila -> Mouse V1 -> Human",
             fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig("simulation/results/three_organism_scaling.png", dpi=150)
plt.close()
print("\nSaved: simulation/results/three_organism_scaling.png")

# Save
np.savez("simulation/results/mouse_deff_results.npz",
         N=N, d_eff_2000=d_eff_2000, d_eff_full=d_eff_full,
         alpha_fit=alpha_fit, C_scale=C_scale,
         d_eff_human=d_eff_human, R_human=R_human,
         Ns=Ns, Ds=Ds, beta_tail=beta_tail)

summary = f"""Mouse V1 (MICrONS mm3) d_eff Analysis
=======================================
Dataset: MICrONS mm3 portion 65 (Ding et al., Nature 2023 / Zenodo 16744240)
Neurons: {N:,}  |  Synaptic edges: {len(edge_idx):,}
Max synapse count: {w_max:.0f}  |  Mean: {weights.mean():.2f}

SVD top 2000:
  Variance captured:   {100*var_captured:.1f}%
  PR d_eff (top 2000): {d_eff_2000:.1f}

Power law tail (ranks 1500-2000): lambda ~ {C_tail:.2e} * i^(-{beta_tail:.3f})
  Tail variance (2001 to N): {100*var_tail:.1f}%
  Estimated full d_eff:      {d_eff_full:.1f}

THREE-ORGANISM SCALING LAW
  C. elegans  N=302     d_eff=28
  Drosophila  N=138,639 d_eff=700
  Mouse V1    N={N:,}  d_eff={d_eff_full:.0f}

  Fit: d_eff = {C_scale:.3f} * N^{alpha_fit:.4f}  (R^2 of log-log fit)

HUMAN ESTIMATE
  d_eff(human, N=86e9) = {d_eff_human:.3e}
  R(D=30%) = {R_human:.3e} bits = {R_human/8e3:.0f} KB

CONSISTENCY WITH TWO-ORGANISM FIT
  Previous alpha (C.elegans + Drosophila only): ~0.50
  Three-organism alpha: {alpha_fit:.4f}
  {'Consistent: alpha stable across three organisms.' if abs(alpha_fit - 0.50) < 0.10 else f'Shifted: alpha changed from 0.50 to {alpha_fit:.3f} with mouse added.'}

WHAT THIS MEANS
  d_eff(human) ~ {d_eff_human:.1e}
  Minimum bits for functional brain reconstruction: ~{R_human:.1e} bits ({R_human/8e3:.0f} KB)
  Scanner measurements needed: ~{d_eff_human * np.log2(1e14/d_eff_human):.1e}
    (compressed sensing: M = d_eff * log2(N_synapses/d_eff))
"""

print(summary)
with open("simulation/results/mouse_deff_summary.txt", "w", encoding="utf-8") as f:
    f.write(summary)
