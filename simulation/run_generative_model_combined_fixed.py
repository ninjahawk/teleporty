"""
Generative model test — combined regression with direct A_j computation.

Problem with previous pulsed experiments:
  A_j = A_K - A_invalid_j becomes numerically unstable when almost all steps
  are invalid for neuron j (sparse pulsed data). Subtracting two nearly-equal
  large matrices amplifies floating-point error, causing frob to explode at K>=8.

Fix: compute A_j directly from valid rows (no subtraction).
  For each j: X_valid = X_K[v_K[:,j]]; A_j = X_valid.T @ X_valid + lambda*I
  This is slower (can't precompute A_K once) but numerically exact.

Also: adaptive lambda = max(lambda_min, alpha * mean_diag(A_j)) to handle
neurons with very few valid observations.

Expected: combined regression now stable across all K. Both tap and chem
should be recoverable simultaneously with K>=2 targeted conditions.
"""

import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")

from simulation.load_connectome import load_connectome, load_gap_junctions
from simulation.rate_model import RateParams, simulate_rate, make_tap_input, make_chem_input

os.makedirs("simulation/results", exist_ok=True)

print("Loading connectome...")
W_raw, neurons, W_norm = load_connectome()
G_raw, g_neurons = load_gap_junctions()
N = len(neurons)

g_idx = {n: i for i, n in enumerate(g_neurons)}
g_set = set(g_neurons)
G_aligned = np.zeros((N, N))
for i, ni in enumerate(neurons):
    for j, nj in enumerate(neurons):
        if ni in g_set and nj in g_set:
            G_aligned[i, j] = G_raw[g_idx[ni], g_idx[nj]]
G_norm = G_aligned / (G_aligned.max() or 1.0)

params = RateParams(tau=10.0, gain=2.5, w_chem=0.25, w_gap=0.1, dt=0.5)
W = W_norm * params.w_chem
G = G_norm * params.w_gap
G_rowsum = G.sum(axis=1)

tap_neurons  = {"ALML", "ALMR", "AVM", "PLML", "PLMR", "PVM"}
chem_neurons = {"AWCL", "AWCR", "ASEL", "ASER"}
tap_idx  = [i for i, n in enumerate(neurons) if n in tap_neurons]
chem_idx = [i for i, n in enumerate(neurons) if n in chem_neurons]

rng = np.random.default_rng(7)
T_ms    = 600.0
T_steps = int(T_ms / params.dt)
SUB     = 20
EPS     = 0.001
PULSE   = int(30.0 / params.dt)
TAP_AMP = 1.5
CHEM_AMP = 1.5

def make_targeted_pulsed(rng, N, T_steps, target_idx, n_pulses, amplitude):
    I = np.zeros((T_steps, N))
    for _ in range(n_pulses):
        onset = rng.integers(0, max(1, T_steps - PULSE))
        for idx in target_idx:
            I[onset:onset+PULSE, idx] = amplitude * rng.uniform(0.7, 1.3)
    return I

def make_random_pulsed(rng, N, T_steps, n_pulses=3):
    I = np.zeros((T_steps, N))
    for _ in range(n_pulses):
        onset = rng.integers(0, max(1, T_steps - PULSE))
        n_d = rng.integers(5, 40)
        idx = rng.choice(N, size=n_d, replace=False)
        I[onset:onset+PULSE, idx] = rng.uniform(1.0, 3.0, size=n_d)
    return I

K_MAX    = 50
K_values = [1, 2, 3, 5, 8, 10, 15, 20, 30, 50]

print(f"\nGenerating {K_MAX} conditions...")
stimuli_full = []
for k in range(K_MAX):
    mod = k % 3
    if mod == 0:
        stimuli_full.append(make_targeted_pulsed(rng, N, T_steps, tap_idx, 4, TAP_AMP))
    elif mod == 1:
        stimuli_full.append(make_targeted_pulsed(rng, N, T_steps, chem_idx, 4, CHEM_AMP))
    else:
        stimuli_full.append(make_random_pulsed(rng, N, T_steps))

print("Simulating...")
r_t_list, r_tp1_list, I_list = [], [], []
for k in range(K_MAX):
    if (k+1) % 10 == 0:
        print(f"  {k+1}/{K_MAX}")
    r = simulate_rate(W_norm, G_norm, stimuli_full[k], T_ms, params)["r"]
    t_idx = np.arange(0, T_steps - 1, SUB)
    r_t_list.append(r[t_idx].astype(np.float64))
    r_tp1_list.append(r[t_idx + 1].astype(np.float64))
    I_list.append(stimuli_full[k][t_idx].astype(np.float64))

T_pc    = r_t_list[0].shape[0]
T_total = T_pc * K_MAX

X_all  = np.concatenate(r_t_list,   axis=0)
Xp_all = np.concatenate(r_tp1_list, axis=0)
Ie_all = np.concatenate(I_list,     axis=0)

ratio    = params.tau / params.dt
tanh_arg = (Xp_all - X_all) * ratio + X_all
valid    = (Xp_all > EPS) & (tanh_arg > -0.9999) & (tanh_arg < 0.9999)
Igap_all = X_all @ G.T - X_all * G_rowsum[np.newaxis, :]
z_all    = np.arctanh(np.clip(tanh_arg, -0.9999, 0.9999)) / params.gain - Igap_all - Ie_all

check = np.abs((z_all - X_all @ W)[valid]).mean()
print(f"Consistency check: {check:.3e}")
frac_valid = valid.mean(axis=0)
print(f"Validity: mean={frac_valid.mean():.3f}, min={frac_valid.min():.3f}")
print(f"Activity: mean={X_all.mean():.4f}")

# -------------------------------------------------------------------
# Behavioral baseline
# -------------------------------------------------------------------
T_test      = 600.0
I_tap_test  = make_tap_input(N, neurons, T_test, params.dt,
                              onset_ms=50.0, duration_ms=30.0, amplitude=4.0)
I_chem_test = make_chem_input(N, neurons, T_test, params.dt, amplitude=3.0)
ws, we = int(100/params.dt), int(500/params.dt)

print("\nBaseline behavioral simulations...")
r_tap0  = simulate_rate(W_norm, G_norm, I_tap_test,  T_test, params)["r"][ws:we].flatten()
r_chem0 = simulate_rate(W_norm, G_norm, I_chem_test, T_test, params)["r"][ws:we].flatten()


def cdiv(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 1.0 - np.dot(a, b)/(na*nb) if na > 1e-10 and nb > 1e-10 else 1.0


# -------------------------------------------------------------------
# Per-neuron ridge regression — DIRECT valid-row computation (no subtraction)
# For each j: A_j = X_valid_j.T @ X_valid_j  (exact, no cancellation)
# Adaptive lambda: alpha * mean(diag(A_j)), minimum lambda_min
# -------------------------------------------------------------------
LAMBDA_ALPHA = 0.01    # lambda = alpha * mean(diag(A_j))
LAMBDA_MIN   = 1e-4    # floor
MIN_VALID    = 5       # minimum valid samples to attempt regression

print(f"\nDirect per-neuron regression (adaptive lambda, alpha={LAMBDA_ALPHA})...")
results = {}

for K in K_values:
    T_K  = K * T_pc
    X_K  = X_all[:T_K]
    z_K  = z_all[:T_K]
    v_K  = valid[:T_K]

    W_hat = np.zeros((N, N))
    lambdas_used = []

    for j in range(N):
        v_j   = v_K[:, j]
        n_v   = v_j.sum()
        if n_v < MIN_VALID:
            continue
        Xv    = X_K[v_j]           # (n_v, N) — valid rows only, exact
        zv    = z_K[v_j, j]        # (n_v,)
        A_j   = Xv.T @ Xv          # (N, N) — no subtraction, numerically clean
        diag_mean = A_j.diagonal().mean()
        lam   = max(LAMBDA_MIN, LAMBDA_ALPHA * diag_mean)
        lambdas_used.append(lam)
        A_j  += lam * np.eye(N)
        b_j   = Xv.T @ zv
        W_hat[:, j] = np.linalg.solve(A_j, b_j)

    frob = np.linalg.norm(W_hat - W) / (np.linalg.norm(W) + 1e-10)
    nz   = W.flatten() > 1e-6
    pr   = pearsonr(W.flatten()[nz], W_hat.flatten()[nz])[0] if nz.sum() > 5 else 0.0

    Wh_norm = np.clip(W_hat / params.w_chem, 0, None)
    r_tap1  = simulate_rate(Wh_norm, G_norm, I_tap_test,  T_test, params)["r"][ws:we].flatten()
    r_chem1 = simulate_rate(Wh_norm, G_norm, I_chem_test, T_test, params)["r"][ws:we].flatten()
    div_tap  = cdiv(r_tap0,  r_tap1)
    div_chem = cdiv(r_chem0, r_chem1)

    lam_arr = np.array(lambdas_used)
    results[K] = dict(frob=frob, pearson=pr, div_tap=div_tap, div_chem=div_chem,
                      W_hat=W_hat, lam_mean=lam_arr.mean(), lam_max=lam_arr.max())
    print(f"K={K:3d}: frob={frob:.4f}, r={pr:.4f}, "
          f"div_tap={div_tap:.4f}, div_chem={div_chem:.4f}  "
          f"[lam mean={lam_arr.mean():.2e} max={lam_arr.max():.2e}]")

# -------------------------------------------------------------------
# Plot
# -------------------------------------------------------------------
K_arr  = np.array(K_values)
fr_arr = np.array([results[K]["frob"]     for K in K_values])
pr_arr = np.array([results[K]["pearson"]  for K in K_values])
dt_arr = np.array([results[K]["div_tap"]  for K in K_values])
dc_arr = np.array([results[K]["div_chem"] for K in K_values])

D_EFF = 28
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Generative Model — Combined Regression (Direct A_j, Adaptive Lambda)\n"
             "Targeted pulsed training: tap / chem / random", fontsize=11)

ax = axes[0,0]
ax.plot(K_arr, fr_arr, "o-", color="steelblue", lw=2)
ax.axvline(D_EFF, color="red", ls="--", lw=1.5, label=f"d_eff={D_EFF}")
ax.set_xlabel("K conditions"); ax.set_ylabel("||W_hat-W||/||W||")
ax.set_title("Structural Reconstruction Error"); ax.set_xscale("log")
ax.legend(); ax.grid(True, alpha=0.3)

ax = axes[0,1]
ax.plot(K_arr, pr_arr, "o-", color="darkorange", lw=2)
ax.axvline(D_EFF, color="red", ls="--", lw=1.5)
ax.axhline(0.9, color="gray", ls=":", lw=1.2, label="r=0.90")
ax.set_xlabel("K conditions"); ax.set_ylabel("Pearson r")
ax.set_title("Weight Correlation"); ax.set_xscale("log")
ax.set_ylim(-0.1, 1.1); ax.legend(); ax.grid(True, alpha=0.3)

ax = axes[1,0]
ax.plot(K_arr, dt_arr, "o-",  color="forestgreen", lw=2, label="Tap")
ax.plot(K_arr, dc_arr, "s--", color="purple",      lw=2, label="Chem")
ax.axvline(D_EFF, color="red",  ls="--", lw=1.5, label=f"d_eff={D_EFF}")
ax.axhline(0.05,  color="gray", ls=":",  lw=1.2, label="5% threshold")
ax.set_xlabel("K conditions"); ax.set_ylabel("Behavioral divergence")
ax.set_title("Behavioral Equivalence"); ax.set_xscale("log")
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

ax = axes[1,1]
lam_means = [results[K]["lam_mean"] for K in K_values]
ax.plot(K_arr, lam_means, "o-", color="gray", lw=2)
ax.set_xlabel("K conditions"); ax.set_ylabel("Mean adaptive lambda")
ax.set_title("Regularization (adaptive)"); ax.set_xscale("log")
ax.set_yscale("log"); ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("simulation/results/generative_model_combined_fixed.png", dpi=150)
plt.close()
print("\nSaved: simulation/results/generative_model_combined_fixed.png")

# -------------------------------------------------------------------
# Summary
# -------------------------------------------------------------------
def find_K(arr, thresh, below=True):
    for K, v in zip(K_values, arr):
        if (below and v < thresh) or (not below and v > thresh):
            return K
    return None

thresh_tap  = find_K(dt_arr, 0.05)
thresh_chem = find_K(dc_arr, 0.05)
thresh_r    = find_K(pr_arr, 0.90, below=False)

lines = [
    "Generative Model Test — Combined Regression, Direct A_j, Adaptive Lambda",
    "=========================================================================",
    f"N={N}, d_eff={D_EFF}, T={T_ms}ms/cond, sub={SUB}, T_pc={T_pc}",
    f"Tap amp={TAP_AMP}, Chem amp={CHEM_AMP}, cycling tap/chem/random",
    f"Adaptive lambda = max({LAMBDA_MIN}, {LAMBDA_ALPHA} * mean_diag(A_j))",
    f"Direct A_j computation (valid rows only, no subtraction)",
    f"Consistency check: {check:.2e}",
    "",
    f"{'K':>5}  {'frob':>8}  {'pearson':>8}  {'div_tap':>9}  {'div_chem':>9}  {'lam_mean':>10}",
]
for K in K_values:
    r = results[K]
    lines.append(f"{K:5d}  {r['frob']:8.4f}  {r['pearson']:8.4f}  "
                 f"{r['div_tap']:9.4f}  {r['div_chem']:9.4f}  {r['lam_mean']:10.2e}")

tap_status = ("CONFIRMED" if thresh_tap  and thresh_tap  <= 5 else
              "PARTIAL"   if thresh_tap  else "FAILED")
chem_status = ("CONFIRMED" if thresh_chem and thresh_chem <= 5 else
               "PARTIAL"   if thresh_chem else "FAILED")

lines += [
    "",
    f"Threshold K for div_tap  < 5%:  {thresh_tap  if thresh_tap  else f'>{K_values[-1]}'}",
    f"Threshold K for div_chem < 5%:  {thresh_chem if thresh_chem else f'>{K_values[-1]}'}",
    f"Threshold K for pearson >= 0.9: {thresh_r    if thresh_r    else f'>{K_values[-1]}'}",
    "",
    f"Tap:  {tap_status}",
    f"Chem: {chem_status}",
    "",
    "Assumptions:",
    "  [KNOWN IN SIM] G known exactly.",
    "  [ESTABLISHED] Dynamical regression exact for rate model.",
    "  [THIS PROJECT] d_eff=28, D_tolerance=0.30.",
    "  [THIS EXPERIMENT] Direct A_j (valid rows) avoids subtraction instability.",
    "  [THIS EXPERIMENT] Adaptive lambda = alpha * mean_diag(A_j) scales with signal.",
]

summary = "\n".join(lines)
print(summary)
with open("simulation/results/generative_model_combined_fixed_summary.txt", "w",
          encoding="utf-8") as f:
    f.write(summary)

np.savez("simulation/results/generative_model_combined_fixed.npz",
         K_values=K_values, frob=fr_arr, pearson=pr_arr,
         div_tap=dt_arr, div_chem=dc_arr, d_eff=D_EFF,
         W_true=W, W_hat_best=results[K_values[-1]]["W_hat"])
print("Done.")
