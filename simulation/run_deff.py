"""
Phase 7C: Effective dimensionality (d_eff) extraction from the C. elegans connectome.

Two complementary methods:

Method 1 — Participation ratio of the weight matrix spectrum:
  d_eff = (sum lambda_i)^2 / sum(lambda_i^2)
  where lambda_i are eigenvalues of W @ W.T (the covariance structure).
  This estimates how many dimensions carry the variance.

Method 2 — Variance explained curve:
  Find k such that top-k PCA components explain 90% (and 99%) of total variance.

Method 3 — Activity manifold dimensionality:
  Run N_stim diverse stimuli, collect activity vectors, apply PCA to the
  (N_stim, N) activity matrix. d_eff_activity = participation ratio of activity eigenspectrum.
  This measures the intrinsic dimensionality of the neural response manifold.

Outputs:
  simulation/results/deff_results.npz
  simulation/results/deff_spectrum.png
  simulation/results/deff_summary.txt
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
from simulation.rate_model import RateParams, simulate_rate

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

# -------------------------------------------------------------------
# Method 1+2: PCA of the weight matrix (flattened connection vectors)
# Each neuron is a point in R^N space (its row of W)
# -------------------------------------------------------------------
print("\nMethod 1+2: PCA of weight matrix rows...")

# Treat each row of W_norm as a data point (presynaptic neuron's output profile)
X = W_norm.copy()  # (N, N)
X_centered = X - X.mean(axis=0)

# SVD
U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
eigenvalues = S**2  # proportional to variance explained

# Participation ratio (Method 1)
d_eff_pr = eigenvalues.sum()**2 / (eigenvalues**2).sum()

# Variance explained curve (Method 2)
cumvar = np.cumsum(eigenvalues) / eigenvalues.sum()
d_eff_90 = int(np.argmax(cumvar >= 0.90)) + 1
d_eff_99 = int(np.argmax(cumvar >= 0.99)) + 1
d_eff_999 = int(np.argmax(cumvar >= 0.999)) + 1

print(f"  N neurons: {N}")
print(f"  N nonzero connections: {(W_norm>0).sum()}")
print(f"  Participation ratio d_eff: {d_eff_pr:.1f}")
print(f"  Dims for 90% variance: {d_eff_90}")
print(f"  Dims for 99% variance: {d_eff_99}")
print(f"  Dims for 99.9% variance: {d_eff_999}")

# -------------------------------------------------------------------
# Method 3: Activity manifold dimensionality
# Diverse stimuli -> collect activity patterns -> PCA
# -------------------------------------------------------------------
print("\nMethod 3: Activity manifold PCA...")

params = RateParams(tau=10.0, gain=2.5, w_chem=0.25, w_gap=0.1, dt=0.5)
T_ms = 400.0
rng = np.random.default_rng(42)

# Generate diverse stimuli: random subsets of neurons stimulated
N_stim = 200
T_steps = int(T_ms / params.dt)
win_s = int(100/params.dt)

activity_matrix = []  # (N_stim, N)

for k in range(N_stim):
    # Random stimulus: 1-10 neurons stimulated at random amplitude
    n_driven = rng.integers(1, 11)
    driven_idx = rng.choice(N, n_driven, replace=False)
    amplitude = rng.uniform(1.0, 4.0)

    I_ext = np.zeros((T_steps, N))
    stim_end = int(200/params.dt)
    I_ext[:stim_end, driven_idx] = amplitude

    result = simulate_rate(W_norm, G_norm, I_ext, T_ms, params)
    # Activity at response peak (100-300ms window)
    win_e = int(300/params.dt)
    r_mean = result["r"][win_s:win_e].mean(axis=0)
    activity_matrix.append(r_mean)

    if (k+1) % 50 == 0:
        print(f"  Stimulus {k+1}/{N_stim}")

A = np.array(activity_matrix)  # (N_stim, N)
print(f"  Activity matrix shape: {A.shape}")
print(f"  Mean activity: {A.mean():.4f}, std: {A.std():.4f}")

A_centered = A - A.mean(axis=0)
_, S_act, _ = np.linalg.svd(A_centered, full_matrices=False)
eig_act = S_act**2

d_eff_act_pr = eig_act.sum()**2 / (eig_act**2).sum()
cumvar_act = np.cumsum(eig_act) / eig_act.sum()
d_eff_act_90  = int(np.argmax(cumvar_act >= 0.90)) + 1
d_eff_act_99  = int(np.argmax(cumvar_act >= 0.99)) + 1

print(f"  Activity PR d_eff: {d_eff_act_pr:.1f}")
print(f"  Activity dims 90%: {d_eff_act_90}")
print(f"  Activity dims 99%: {d_eff_act_99}")

# -------------------------------------------------------------------
# Scaling estimate for human
# -------------------------------------------------------------------
# C. elegans: 302 neurons, d_eff from activity manifold
# Human: ~86e9 neurons
# Scaling law: d_eff(human) = d_eff(elegans) * (N_human / N_elegans)^alpha

N_elegans = 302
N_human = 86e9

for alpha in [0.5, 0.75, 1.0]:
    scale = (N_human / N_elegans) ** alpha
    d_eff_human_est = d_eff_act_pr * scale
    print(f"  Scaling alpha={alpha}: d_eff(human) ~ {d_eff_human_est:.2e}")

# -------------------------------------------------------------------
# Save and plot
# -------------------------------------------------------------------
np.savez("simulation/results/deff_results.npz",
         eigenvalues=eigenvalues, cumvar=cumvar,
         eig_act=eig_act, cumvar_act=cumvar_act,
         d_eff_pr=d_eff_pr, d_eff_90=d_eff_90, d_eff_99=d_eff_99,
         d_eff_act_pr=d_eff_act_pr, d_eff_act_90=d_eff_act_90, d_eff_act_99=d_eff_act_99,
         N=N, N_elegans=N_elegans, N_human=N_human)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Plot 1: Weight matrix eigenspectrum
axes[0].semilogy(eigenvalues / eigenvalues.sum(), "b-", lw=1.5)
axes[0].set_xlabel("Principal component index")
axes[0].set_ylabel("Fraction of variance")
axes[0].set_title(f"Weight matrix eigenspectrum\n(N={N}, PR d_eff={d_eff_pr:.1f})")
axes[0].axvline(d_eff_90,  color="orange", ls="--", lw=1.5, label=f"90% ({d_eff_90})")
axes[0].axvline(d_eff_99,  color="red",    ls="--", lw=1.5, label=f"99% ({d_eff_99})")
axes[0].legend(fontsize=8)
axes[0].grid(True, alpha=0.3)

# Plot 2: Cumulative variance
axes[1].plot(cumvar, "b-", lw=2, label="Weight matrix")
axes[1].plot(cumvar_act[:len(cumvar)], "g-", lw=2, label="Activity manifold")
axes[1].axhline(0.90, color="orange", ls="--", lw=1.5, label="90%")
axes[1].axhline(0.99, color="red",    ls="--", lw=1.5, label="99%")
axes[1].set_xlabel("Number of principal components")
axes[1].set_ylabel("Cumulative variance explained")
axes[1].set_title("Dimensionality of C. elegans connectome")
axes[1].legend(fontsize=8)
axes[1].grid(True, alpha=0.3)
axes[1].set_xlim(0, N)

# Plot 3: Activity manifold eigenspectrum
axes[2].semilogy(eig_act / eig_act.sum(), "g-", lw=1.5)
axes[2].set_xlabel("Principal component index")
axes[2].set_ylabel("Fraction of variance")
axes[2].set_title(f"Activity manifold eigenspectrum\n(N_stim={N_stim}, PR d_eff={d_eff_act_pr:.1f})")
axes[2].axvline(d_eff_act_90, color="orange", ls="--", lw=1.5, label=f"90% ({d_eff_act_90})")
axes[2].axvline(d_eff_act_99, color="red",    ls="--", lw=1.5, label=f"99% ({d_eff_act_99})")
axes[2].legend(fontsize=8)
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("simulation/results/deff_spectrum.png", dpi=150)
plt.close()
print("\nSaved: simulation/results/deff_spectrum.png")

summary = f"""C. elegans d_eff Analysis — Phase 7C
======================================
Network: {N} neurons, {(W_norm>0).sum()} chemical synapses

METHOD 1+2: PCA of weight matrix (row vectors)
  Each neuron treated as a point in output-weight space.
  Total dimensions available: {N}

  Participation ratio d_eff:    {d_eff_pr:.1f}
  Dims for 90% variance:        {d_eff_90}
  Dims for 99% variance:        {d_eff_99}
  Dims for 99.9% variance:      {d_eff_999}

METHOD 3: Activity manifold PCA
  {N_stim} diverse random stimuli, activity pattern recorded.
  Activity matrix: ({N_stim} x {N})

  Participation ratio d_eff:    {d_eff_act_pr:.1f}
  Dims for 90% activity var:    {d_eff_act_90}
  Dims for 99% activity var:    {d_eff_act_99}

INTERPRETATION:
  The activity manifold has ~{d_eff_act_pr:.0f} effective dimensions out of {N} possible.
  Dimensionality fraction: {d_eff_act_pr/N:.3f} ({100*d_eff_act_pr/N:.1f}%)

  This means the network's responses to diverse stimuli lie in a
  ~{d_eff_act_pr:.0f}-dimensional subspace. Most of the {N}-dimensional activity space
  is never accessed — the network has massive low-dimensional structure.

SCALING TO HUMAN:
  C. elegans: N={N_elegans}, d_eff_activity ~ {d_eff_act_pr:.1f}
  Human: N ~ {N_human:.0e} neurons

  Scaling law d_eff(human) = d_eff(C.elegans) * (N_human/N_elegans)^alpha:
  alpha=0.50: d_eff(human) ~ {d_eff_act_pr * (N_human/N_elegans)**0.50:.2e}
  alpha=0.75: d_eff(human) ~ {d_eff_act_pr * (N_human/N_elegans)**0.75:.2e}
  alpha=1.00: d_eff(human) ~ {d_eff_act_pr * (N_human/N_elegans)**1.00:.2e}

  The rate-distortion analysis used d_eff(human) = 10^10 to 10^12.
  This simulation gives: alpha=0.75 -> {d_eff_act_pr * (N_human/N_elegans)**0.75:.1e}
  which {'falls within' if 1e10 <= d_eff_act_pr*(N_human/N_elegans)**0.75 <= 1e12 else 'falls outside'} the assumed range.

CAVEAT: Scaling from 300 neurons (C. elegans) to 86 billion (human) is a large
extrapolation. The Drosophila connectome (140,000 neurons, FlyWire 2023) would
provide a critical intermediate data point. If d_eff(Drosophila) is measured,
we can fit the alpha exponent empirically rather than assuming it.
"""

print(summary)
with open("simulation/results/deff_summary.txt", "w", encoding="utf-8") as f:
    f.write(summary)
