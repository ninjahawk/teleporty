"""
d_eff analysis for Drosophila (FlyWire 783, Dorkenwald et al. 2023).

138,000 neurons, 16.8 million edges.

For a network this size, we can't build the full 138k x 138k weight matrix —
that's 138000^2 * 8 bytes = 152 GB. Instead we use:

Method 1 — Randomized SVD on the sparse weight matrix
  Treat the NxN sparse matrix as a linear operator, use randomized SVD
  (Halko et al. 2011) to estimate the top-k singular values.
  d_eff = (sum sigma_i^2)^2 / sum(sigma_i^4)  [participation ratio]

Method 2 — Out-degree distribution analysis
  For each neuron, its out-degree profile is a sparse vector.
  PCA on a random sample of neuron profiles estimates d_eff.

Method 3 — Stochastic power iteration
  Estimate the eigenspectrum decay rate without computing all eigenvalues.
  Fit a power law to the top-k eigenvalues, extrapolate.

Compares to C. elegans result to fit alpha in d_eff ~ N^alpha.
"""

import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import sparse
from sklearn.utils.extmath import randomized_svd
import pandas as pd

sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")

os.makedirs("simulation/results", exist_ok=True)

print("Loading FlyWire edge list...")
df = pd.read_feather("simulation/data/flywire_connections_783.feather")
print(f"  {len(df):,} edges, {df['pre_pt_root_id'].nunique():,} pre-neurons, "
      f"{df['post_pt_root_id'].nunique():,} post-neurons")

# --- Build sparse weight matrix ---
print("\nBuilding sparse weight matrix...")

# Aggregate by (pre, post) — sum syn_count across neuropils
df_agg = df.groupby(['pre_pt_root_id', 'post_pt_root_id'])['syn_count'].sum().reset_index()
print(f"  Unique directed pairs: {len(df_agg):,}")

# Map neuron IDs to integer indices
all_ids = sorted(set(df_agg['pre_pt_root_id']) | set(df_agg['post_pt_root_id']))
N = len(all_ids)
id_to_idx = {nid: i for i, nid in enumerate(all_ids)}
print(f"  Total unique neurons: {N:,}")

pre_idx  = df_agg['pre_pt_root_id'].map(id_to_idx).values
post_idx = df_agg['post_pt_root_id'].map(id_to_idx).values
weights  = df_agg['syn_count'].values.astype(float)

# Normalize weights (same as C. elegans: divide by max)
w_max = weights.max()
w_norm = weights / w_max
print(f"  Max syn_count: {w_max:.0f}, mean (nonzero): {weights.mean():.2f}")

# Build sparse matrix
W_sparse = sparse.csr_matrix((w_norm, (pre_idx, post_idx)), shape=(N, N))
print(f"  Sparse matrix shape: {W_sparse.shape}, nnz: {W_sparse.nnz:,}")
print(f"  Density: {W_sparse.nnz / N**2:.2e}")

# -------------------------------------------------------------------
# Method 1: Randomized SVD
# -------------------------------------------------------------------
print("\nMethod 1: Randomized SVD (top 300 components)...")

# Center the matrix (subtract column means) — approximated via sparse ops
col_means = np.asarray(W_sparse.mean(axis=0)).flatten()
# For sparse matrix, we can't subtract means directly without densifying
# Use uncentered SVD as approximation (common for large sparse matrices)
# This gives us the dominant directions of variation

k = 300  # number of singular values to compute
U, S, Vt = randomized_svd(W_sparse, n_components=k, random_state=42, n_iter=4)
eigenvalues = S**2  # proportional to variance

# Participation ratio
d_eff_pr = eigenvalues.sum()**2 / (eigenvalues**2).sum()

# Variance explained — we only have top k, extrapolate total variance
# Total variance = sum of all singular values squared = ||W||_F^2
total_variance = W_sparse.power(2).sum()
var_in_top_k = eigenvalues.sum()
print(f"  Variance in top {k} components: {100*var_in_top_k/total_variance:.1f}% of total")

# Cumulative variance explained by top-k
cumvar_k = np.cumsum(eigenvalues) / total_variance
d_eff_90  = int(np.argmax(cumvar_k >= 0.90)) + 1 if (cumvar_k >= 0.90).any() else f">{k}"
d_eff_99  = int(np.argmax(cumvar_k >= 0.99)) + 1 if (cumvar_k >= 0.99).any() else f">{k}"

print(f"  Participation ratio d_eff: {d_eff_pr:.1f}")
print(f"  Dims for 90% variance (of top-{k}): {d_eff_90}")
print(f"  Dims for 99% variance (of top-{k}): {d_eff_99}")

# -------------------------------------------------------------------
# Method 2: PCA on random sample of neuron out-profiles
# -------------------------------------------------------------------
print("\nMethod 2: PCA on sampled neuron out-degree profiles...")

# Sample N_sample neurons; for each, take their output weight vector
# (their row in W, as a dense vector — feasible for a sample)
N_sample = 5000
rng = np.random.default_rng(42)
sampled_idx = rng.choice(N, N_sample, replace=False)

# Build dense sample matrix: (N_sample, N)
# Each row = one neuron's outgoing weight profile
X_sample = W_sparse[sampled_idx, :].toarray()  # (N_sample, N) — this is 5000 x 138k = 5.5 GB... too big

print(f"  N_sample x N = {N_sample} x {N} = {N_sample*N*8/1e9:.1f} GB — too large for dense")
print("  Using sparse-compatible approach instead: sample columns too")

# Better: sample both rows and columns — gives submatrix PCA
# Take top N_col most-connected neurons as the feature space
out_degrees = np.asarray(W_sparse.sum(axis=1)).flatten()
top_col_idx = np.argsort(out_degrees)[-2000:]  # top 2000 by out-strength as features

X_sub = W_sparse[sampled_idx, :][:, top_col_idx].toarray()  # (5000, 2000)
print(f"  Submatrix shape: {X_sub.shape}")

X_sub_c = X_sub - X_sub.mean(axis=0)
_, S_sub, _ = randomized_svd(X_sub_c, n_components=min(200, min(X_sub.shape)-1), random_state=42)
eig_sub = S_sub**2
d_eff_sub = eig_sub.sum()**2 / (eig_sub**2).sum()
cumvar_sub = np.cumsum(eig_sub) / eig_sub.sum()
d_sub_90 = int(np.argmax(cumvar_sub >= 0.90)) + 1

print(f"  Submatrix participation ratio d_eff: {d_eff_sub:.1f}")
print(f"  Submatrix dims for 90% variance: {d_sub_90}")

# -------------------------------------------------------------------
# Method 3: Eigenvalue power-law fit -> extrapolate
# -------------------------------------------------------------------
print("\nMethod 3: Power-law fit to eigenspectrum...")

# Fit a power law: lambda_i ~ C * i^(-beta)
# log(lambda_i) = log(C) - beta * log(i)
k_fit = 200  # use top 200 for fit (avoid noise floor at high indices)
i_vals = np.arange(1, k_fit + 1)
log_i = np.log(i_vals)
log_lam = np.log(eigenvalues[:k_fit] + 1e-30)

# Linear regression in log-log space
coeffs = np.polyfit(log_i, log_lam, 1)
beta = -coeffs[0]
log_C = coeffs[1]
C = np.exp(log_C)

print(f"  Power law: lambda_i ~ {C:.4f} * i^(-{beta:.3f})")
print(f"  (beta > 1 means total variance converges, beta <= 1 means it diverges)")

# Estimate total variance by integrating power law from 1 to N
# integral_1^N C*i^(-beta) di ~ C * N^(1-beta) / (1-beta) for beta != 1
if beta > 1:
    total_var_powerlaw = C * (1 - N**(1-beta)) / (beta - 1)
    # d_eff from participation ratio: sum(lam^2) / (sum lam)^2
    # For power law: sum(lam_i) ~ C * N^(1-beta)/(beta-1), sum(lam_i^2) ~ C^2 * N^(1-2*beta)/(2*beta-1)
    sum_lam  = C * (1 - N**(1-beta)) / (beta-1) if beta != 1 else C * np.log(N)
    sum_lam2 = C**2 * (1 - N**(1-2*beta)) / (2*beta-1) if beta > 0.5 else np.inf
    if np.isfinite(sum_lam2) and sum_lam2 > 0:
        d_eff_powerlaw = sum_lam**2 / sum_lam2
        print(f"  Extrapolated d_eff (power law): {d_eff_powerlaw:.1f}")
    else:
        d_eff_powerlaw = None
        print(f"  Extrapolated d_eff: diverges (beta={beta:.3f} <= 0.5 in sum_lam2)")
else:
    d_eff_powerlaw = None
    print(f"  beta={beta:.3f} <= 1: power law doesn't converge, d_eff ~ N")

# -------------------------------------------------------------------
# Scale comparison: C. elegans vs Drosophila -> fit alpha
# -------------------------------------------------------------------
print("\n--- Scaling Analysis ---")
N_elegans = 302
d_eff_elegans = 13.3  # from activity manifold PR, from run_deff.py

N_fly = N
d_eff_fly = d_eff_pr  # participation ratio from randomized SVD

alpha_fit = np.log(d_eff_fly / d_eff_elegans) / np.log(N_fly / N_elegans)
print(f"C. elegans: N={N_elegans}, d_eff={d_eff_elegans:.1f}")
print(f"Drosophila: N={N_fly:,}, d_eff={d_eff_fly:.1f}")
print(f"Fitted alpha: {alpha_fit:.4f}")
print(f"  d_eff ~ N^{alpha_fit:.3f}")

N_human = 86e9
d_eff_human = d_eff_elegans * (N_human / N_elegans) ** alpha_fit
print(f"\nHuman estimate (N={N_human:.0e}):")
print(f"  d_eff(human) = {d_eff_human:.3e}")

# R-D at D=30% with fitted d_eff
sigma2_elegans = 0.011226  # from C. elegans run
D_30 = 0.001010
R_human = d_eff_human * 0.5 * np.log2(sigma2_elegans / D_30)
print(f"  R(D=30%): {R_human:.3e} bits = {R_human/8e9:.2f} GB")

# -------------------------------------------------------------------
# Plot
# -------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Eigenspectrum
axes[0].semilogy(np.arange(1, k+1), eigenvalues / eigenvalues[0], "b-", lw=1.5, label="FlyWire (Drosophila)")
# Power law fit
i_range = np.arange(1, k+1)
axes[0].semilogy(i_range, C * i_range**(-beta) / eigenvalues[0], "r--", lw=1.5,
                  label=f"Power law fit (beta={beta:.2f})")
axes[0].set_xlabel("Principal component index")
axes[0].set_ylabel("Normalized eigenvalue")
axes[0].set_title(f"FlyWire eigenspectrum\n(N={N:,}, d_eff PR={d_eff_pr:.0f})")
axes[0].legend(fontsize=8)
axes[0].grid(True, alpha=0.3, which="both")

# Cumulative variance (top k)
axes[1].plot(np.arange(1, k+1), cumvar_k * 100, "b-", lw=2, label="FlyWire")
axes[1].axhline(90, color="orange", ls="--", lw=1.5, label="90%")
axes[1].axhline(99, color="red",    ls="--", lw=1.5, label="99%")
axes[1].set_xlabel("Number of principal components")
axes[1].set_ylabel("Cumulative variance (%)")
axes[1].set_title(f"Variance explained (top {k})\nFlyWire Drosophila connectome")
axes[1].legend(fontsize=8)
axes[1].grid(True, alpha=0.3)

# Scaling plot
N_points = np.array([N_elegans, N_fly])
d_points  = np.array([d_eff_elegans, d_eff_fly])
N_range = np.logspace(2, 11, 200)

axes[2].loglog(N_points, d_points, "ko", ms=10, zorder=5, label="Measured")
axes[2].loglog(N_range, d_eff_elegans * (N_range/N_elegans)**alpha_fit, "b-",
                lw=2, label=f"Fit: alpha={alpha_fit:.3f}")
for a, col in [(0.5,"green"), (0.75,"orange"), (1.0,"red")]:
    axes[2].loglog(N_range, d_eff_elegans * (N_range/N_elegans)**a, "--",
                    color=col, lw=1, alpha=0.6, label=f"alpha={a}")
axes[2].axvline(N_human, color="purple", ls=":", lw=1.5)
axes[2].text(N_human*1.5, 1, "Human", fontsize=8, color="purple")
axes[2].scatter([N_human], [d_eff_human], s=100, c="purple", marker="*", zorder=5,
                 label=f"Human est: {d_eff_human:.1e}")
axes[2].set_xlabel("Neuron count N")
axes[2].set_ylabel("d_eff")
axes[2].set_title(f"d_eff scaling law\nalpha={alpha_fit:.3f}")
axes[2].legend(fontsize=7)
axes[2].grid(True, alpha=0.3, which="both")
axes[2].annotate("C. elegans", (N_elegans, d_eff_elegans), fontsize=8,
                   xytext=(N_elegans*3, d_eff_elegans*3))
axes[2].annotate("Drosophila", (N_fly, d_eff_fly), fontsize=8,
                   xytext=(N_fly*0.1, d_eff_fly*3))

plt.suptitle("Drosophila d_eff Analysis — FlyWire 783 Connectome", fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig("simulation/results/drosophila_deff.png", dpi=150)
plt.close()
print("\nSaved: simulation/results/drosophila_deff.png")

# Save results
np.savez("simulation/results/drosophila_deff_results.npz",
         N=N, d_eff_pr=d_eff_pr, d_eff_sub=d_eff_sub,
         eigenvalues=eigenvalues, cumvar_k=cumvar_k,
         alpha_fit=alpha_fit, d_eff_human=d_eff_human,
         N_elegans=N_elegans, d_eff_elegans=d_eff_elegans,
         beta=beta, C=C)

summary = f"""Drosophila (FlyWire 783) d_eff Analysis
========================================
Dataset: Dorkenwald et al. 2023, proofread_connections_783.feather
Neurons: {N:,}
Directed edges (unique pairs): {len(df_agg):,}
Max syn_count: {w_max:.0f}

METHOD 1: Randomized SVD (top {k} components)
  Participation ratio d_eff:         {d_eff_pr:.1f}
  Dims for 90% variance (top-{k}):  {d_eff_90}
  Dims for 99% variance (top-{k}):  {d_eff_99}
  Variance in top {k} components:   {100*var_in_top_k/total_variance:.1f}%

METHOD 2: Submatrix PCA ({N_sample} x 2000 submatrix)
  Participation ratio d_eff:  {d_eff_sub:.1f}
  Dims for 90% variance:      {d_sub_90}

METHOD 3: Power-law eigenspectrum fit
  lambda_i ~ {C:.4f} * i^(-{beta:.3f})
  beta = {beta:.3f} {'(> 1: variance converges)' if beta > 1 else '(<= 1: slow convergence)'}
  Extrapolated d_eff: {f'{d_eff_powerlaw:.1f}' if d_eff_powerlaw else 'N/A'}

SCALING ANALYSIS
  C. elegans: N={N_elegans},   d_eff_activity={d_eff_elegans:.1f}
  Drosophila: N={N_fly:,}, d_eff_SVD={d_eff_pr:.1f}
  Fitted scaling exponent alpha: {alpha_fit:.4f}
  d_eff scales approximately as N^{alpha_fit:.3f}

HUMAN ESTIMATE
  N_human = 86e9 neurons
  d_eff(human) ~ {d_eff_human:.3e}
  R(D=30%) ~ {R_human:.3e} bits  ({R_human/8e9:.2f} GB)

INTERPRETATION
  The scaling exponent alpha={alpha_fit:.3f} means:
  {'- Sub-linear scaling: each new neuron adds less than proportional complexity' if alpha_fit < 1 else '- Linear scaling: complexity grows with neuron count'}
  - d_eff(human) ~ {d_eff_human:.1e}, {'within' if 1e10 <= d_eff_human <= 1e12 else 'BELOW' if d_eff_human < 1e10 else 'ABOVE'} the assumed R-D range of 10^10-10^12

  {'This REVISES DOWNWARD the minimum bits estimate.' if d_eff_human < 1e10 else 'This is consistent with the assumed range.'}
  Revised R-D minimum at D=30%: {R_human:.2e} bits = {R_human/8e9:.2f} GB

CAVEAT
  The C. elegans d_eff was measured from activity manifold (behavioral simulation).
  The Drosophila d_eff was measured from the weight matrix SVD (no dynamics).
  These are different quantities — ideally both would use the same method.
  The SVD method tends to give HIGHER d_eff than the activity manifold method.
  If the activity manifold d_eff for Drosophila is lower (as for C. elegans,
  where activity d_eff=13 vs weight PCA d_eff=28), alpha would be even lower.
"""

print(summary)
with open("simulation/results/drosophila_deff_summary.txt", "w", encoding="utf-8") as f:
    f.write(summary)
