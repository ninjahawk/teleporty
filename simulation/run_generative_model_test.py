"""
Generative model falsification test — Prediction 3 (dynamical regression, corrected).

Prior runs:
  v1 (steady-state): consistency error = 0.61 — network doesn't reach fixed point.
  v2 (dynamical, shared A): consistency = 1e-6 (exact) but divergence worsens with K.
     Root cause: zero-padding invalid z entries biases the shared A regression.
     A grows with K but B (valid only) doesn't match -> increasing distortion.

This version (v3): per-neuron A_j using subtraction:
  A_j = A_all - A_invalid_j  (remove invalid-step contribution for each j)
  w_j = solve(A_j + lambda I, b_j)  [correct, unbiased per-neuron regression]

Key equation (exact, no approximation):
  z_j(t) = atanh((r_j(t+1) - r_j(t)) * tau/dt + r_j(t)) / gain
            - I_gap_j(t) - I_ext_j(t)
          = sum_i W[i,j] r_i(t)  [valid when r_j(t+1) > eps]

Prediction: behavioral equivalence (div < 5%) for K ~ a few conditions,
because each condition yields ~tau_eff = T/tau independent activity samples.
If K × T/tau >= d_eff = 28, the activity manifold is spanned.
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

print(f"N={N}, chemical={(W>0).sum()}, gap={(G>0).sum()}")

# -------------------------------------------------------------------
# Stimuli and simulation
# -------------------------------------------------------------------
rng = np.random.default_rng(42)
T_ms     = 600.0
T_steps  = int(T_ms / params.dt)  # 1200
SUB      = 20        # subsample stride: every 20 dt = 10ms ≈ tau (decorrelation)
EPS      = 0.001     # validity threshold for r_j(t+1)

K_values = [1, 2, 3, 5, 8, 10, 15, 20, 30, 50]
K_max    = max(K_values)

print(f"\nGenerating {K_max} conditions (T={T_ms}ms, sub={SUB})...")
stimuli = []
for k in range(K_max):
    n_d = rng.integers(5, 60)
    idx = rng.choice(N, size=n_d, replace=False)
    amp = rng.uniform(0.5, 5.0, size=n_d)
    I_k = np.zeros(N)
    I_k[idx] = amp
    stimuli.append(I_k)

print("Simulating...")
r_t_list, r_tp1_list, I_list = [], [], []
for k in range(K_max):
    if (k+1) % 10 == 0:
        print(f"  {k+1}/{K_max}")
    I_k_full = np.tile(stimuli[k], (T_steps, 1))
    r = simulate_rate(W_norm, G_norm, I_k_full, T_ms, params)["r"]  # (T_steps, N)
    t_idx = np.arange(0, T_steps - 1, SUB)
    r_t_list.append(r[t_idx].astype(np.float64))
    r_tp1_list.append(r[t_idx + 1].astype(np.float64))
    I_list.append(np.tile(stimuli[k], (len(t_idx), 1)).astype(np.float64))

T_pc = r_t_list[0].shape[0]   # time steps per condition after subsampling
T_total = T_pc * K_max

X_all   = np.concatenate(r_t_list,   axis=0)   # (T_total, N) activity at t
Xp_all  = np.concatenate(r_tp1_list, axis=0)   # (T_total, N) activity at t+1
Ie_all  = np.concatenate(I_list,     axis=0)   # (T_total, N) external input

print(f"T_pc={T_pc}, T_total={T_total}")
print(f"Activity: mean={X_all.mean():.4f}, frac>{EPS}: {(X_all > EPS).mean():.3f}")

# Validity: lower clip not active at t+1
valid = Xp_all > EPS  # (T_total, N)

# tanh argument (exact when valid)
ratio    = params.tau / params.dt   # = 20
tanh_arg = (Xp_all - X_all) * ratio + X_all  # (T_total, N)
valid   &= (tanh_arg > -0.9999) & (tanh_arg < 0.9999)

frac_valid = valid.mean(axis=0)  # (N,)
print(f"Validity: mean={frac_valid.mean():.3f}, min={frac_valid.min():.3f}")

# Gap junction current: I_gap[t, j] = (G @ r[t])[j] - G_rowsum[j] * r[t, j]
# In simulate_rate: I_gap = G @ r - G.sum(axis=1) * r
# So I_gap[j] = (G @ r)[j] - G_rowsum[j] * r[j]  => (X_all @ G.T)[t, j] = sum_i X[t,i]*G[j,i]
I_gap_all = X_all @ G.T - X_all * G_rowsum[np.newaxis, :]  # (T_total, N)

# Regression targets z_j(t) (exact where valid)
z_all = np.arctanh(np.clip(tanh_arg, -0.9999, 0.9999)) / params.gain \
        - I_gap_all - Ie_all   # (T_total, N)

# Consistency check on valid entries
z_expected = X_all @ W   # (T_total, N): true sum_i W[i,j] r_i
check = np.abs((z_all - z_expected)[valid]).mean()
print(f"Consistency check (valid): mean|z - X@W| = {check:.3e}  [expect ~0]")

# -------------------------------------------------------------------
# Behavioral baseline (ground truth)
# -------------------------------------------------------------------
T_test = 600.0
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
# Per-neuron ridge regression for each K
#
# Correct formulation:
#   For neuron j: solve min_wj sum_{t: valid_j} ||r(t)·wj - z_j(t)||^2 + lambda||wj||^2
#   => (A_j + lambda I) wj = b_j
#   where A_j = X_K[valid_K[:,j]].T @ X_K[valid_K[:,j]]
#         b_j = X_K[valid_K[:,j]].T @ z_j_K[valid_K[:,j]]
#
# Efficient: A_j = A_all_K - A_invalid_j_K
# A_invalid_j_K has only ~(1-f_j)*T_K rows (small for active neurons).
# -------------------------------------------------------------------
lambda_r = 1e-4
print(f"\nPer-neuron ridge regression (lambda={lambda_r})...")
results = {}

for K in K_values:
    T_K = K * T_pc
    X_K  = X_all[:T_K]      # (T_K, N)
    z_K  = z_all[:T_K]      # (T_K, N)  — raw z (correct for valid, garbage for invalid)
    v_K  = valid[:T_K]      # (T_K, N) boolean

    # Global A and B for this K
    A_K = X_K.T @ X_K                          # (N, N) — all steps
    B_K = X_K.T @ (z_K * v_K.astype(float))   # (N, N) — valid steps only (z * mask)

    # Per-neuron regression
    W_hat = np.zeros((N, N))
    for j in range(N):
        inv_j   = ~v_K[:, j]                   # boolean: invalid steps for j
        X_inv_j = X_K[inv_j]                   # (T_inv, N) — invalid rows
        A_inv_j = X_inv_j.T @ X_inv_j          # subtract to get A_j (valid only)
        A_j     = A_K - A_inv_j + lambda_r * np.eye(N)  # (N, N)
        b_j     = B_K[:, j]                    # (N,) = sum_{valid} r(t) * z_j(t)
        W_hat[:, j] = np.linalg.solve(A_j, b_j)

    # For neurons never valid in this K, zero their column
    frac_valid_K = v_K.mean(axis=0)  # (N,)
    W_hat[:, frac_valid_K < 0.05] = 0.0

    # --- Structural metrics ---
    frob = np.linalg.norm(W_hat - W) / (np.linalg.norm(W) + 1e-10)
    nz   = W.flatten() > 1e-6
    pr   = pearsonr(W.flatten()[nz], W_hat.flatten()[nz])[0] if nz.sum() > 5 else 0.0

    # --- Behavioral metrics ---
    Wh_norm = np.clip(W_hat / params.w_chem, 0, None)
    r_tap1  = simulate_rate(Wh_norm, G_norm, I_tap_test,  T_test, params)["r"][ws:we].flatten()
    r_chem1 = simulate_rate(Wh_norm, G_norm, I_chem_test, T_test, params)["r"][ws:we].flatten()
    div_tap  = cdiv(r_tap0,  r_tap1)
    div_chem = cdiv(r_chem0, r_chem1)

    results[K] = dict(frob=frob, pearson=pr, div_tap=div_tap, div_chem=div_chem,
                      W_hat=W_hat)
    print(f"K={K:3d}: frob={frob:.4f}, r={pr:.4f}, "
          f"div_tap={div_tap:.4f}, div_chem={div_chem:.4f}")

# -------------------------------------------------------------------
# Diagnostic: tap neuron coverage in training data
# -------------------------------------------------------------------
tap_neurons  = {"ALML", "ALMR", "AVM", "PLML", "PLMR", "PVM"}
chem_neurons = {"AWCL", "AWCR", "ASEL", "ASER"}
tap_idx  = [i for i, n in enumerate(neurons) if n in tap_neurons]
chem_idx = [i for i, n in enumerate(neurons) if n in chem_neurons]
print(f"\nTap neuron mean activity in training data: {X_all[:, tap_idx].mean():.4f}")
print(f"Chem neuron mean activity in training data: {X_all[:, chem_idx].mean():.4f}")
print(f"Global mean activity in training data: {X_all.mean():.4f}")

# -------------------------------------------------------------------
# Targeted experiment: add tap + chem stimuli explicitly to training
# Test hypothesis: tap divergence fails because tap neurons are
# underrepresented in random training stimuli.
# -------------------------------------------------------------------
print("\n--- Targeted experiment: K_random + 1 tap + 1 chem training conditions ---")

# Build tap training stimulus: constant drive to tap neurons
I_tap_train = np.zeros(N)
for idx in tap_idx:
    I_tap_train[idx] = 4.0
I_chem_train = np.zeros(N)
for idx in chem_idx:
    I_chem_train[idx] = 3.0

def run_condition(I_k_const):
    I_k_full = np.tile(I_k_const, (T_steps, 1))
    r = simulate_rate(W_norm, G_norm, I_k_full, T_ms, params)["r"]
    t_idx = np.arange(0, T_steps - 1, SUB)
    return r[t_idx].astype(np.float64), r[t_idx + 1].astype(np.float64)

r_tap_t,  r_tap_tp1  = run_condition(I_tap_train)
r_chem_t, r_chem_tp1 = run_condition(I_chem_train)
I_tap_tile  = np.tile(I_tap_train,  (r_tap_t.shape[0],  1))
I_chem_tile = np.tile(I_chem_train, (r_chem_t.shape[0], 1))

def compute_z_block(r_t, r_tp1, I_ext_block):
    ratio    = params.tau / params.dt
    tanh_arg = (r_tp1 - r_t) * ratio + r_t
    valid_b  = (r_tp1 > EPS) & (tanh_arg > -0.9999) & (tanh_arg < 0.9999)
    Igap_b   = r_t @ G.T - r_t * G_rowsum[np.newaxis, :]
    z_b      = np.arctanh(np.clip(tanh_arg, -0.9999, 0.9999)) / params.gain - Igap_b - I_ext_block
    return r_t, r_tp1, z_b, valid_b

xt_tap,  xtp1_tap,  z_tap,  v_tap  = compute_z_block(r_tap_t,  r_tap_tp1,  I_tap_tile)
xt_chem, xtp1_chem, z_chem, v_chem = compute_z_block(r_chem_t, r_chem_tp1, I_chem_tile)

print(f"Tap training: tap neuron mean activity = {xt_tap[:, tap_idx].mean():.4f}")
print(f"Chem training: chem neuron mean activity = {xt_chem[:, chem_idx].mean():.4f}")

targeted_results = {}
for K_rand in [0, 1, 2, 3, 5, 10, 20]:
    # Combine: K_rand random conditions + 1 tap + 1 chem
    if K_rand > 0:
        T_K = K_rand * T_pc
        X_base   = X_all[:T_K]
        z_base   = z_all[:T_K]
        v_base   = valid[:T_K]
        Ie_base  = Ie_all[:T_K]
        X_comb   = np.concatenate([X_base,  xt_tap,  xt_chem], axis=0)
        z_comb   = np.concatenate([z_base,  z_tap * v_tap.astype(float),
                                   z_chem * v_chem.astype(float)], axis=0)
        v_comb   = np.concatenate([v_base,  v_tap,   v_chem],  axis=0)
    else:
        X_comb = np.concatenate([xt_tap, xt_chem], axis=0)
        z_comb = np.concatenate([z_tap * v_tap.astype(float), z_chem * v_chem.astype(float)], axis=0)
        v_comb = np.concatenate([v_tap, v_chem], axis=0)

    A_comb = X_comb.T @ X_comb

    W_hat_t = np.zeros((N, N))
    for j in range(N):
        inv_j   = ~v_comb[:, j]
        A_inv_j = X_comb[inv_j].T @ X_comb[inv_j]
        A_j     = A_comb - A_inv_j + lambda_r * np.eye(N)
        b_j     = X_comb.T @ (z_comb[:, j] * v_comb[:, j].astype(float))
        W_hat_t[:, j] = np.linalg.solve(A_j, b_j)

    fv_t = v_comb.mean(axis=0)
    W_hat_t[:, fv_t < 0.05] = 0.0
    Wh_norm_t = np.clip(W_hat_t / params.w_chem, 0, None)

    r_tap1_t  = simulate_rate(Wh_norm_t, G_norm, I_tap_test,  T_test, params)["r"][ws:we].flatten()
    r_chem1_t = simulate_rate(Wh_norm_t, G_norm, I_chem_test, T_test, params)["r"][ws:we].flatten()
    dt_t  = cdiv(r_tap0,  r_tap1_t)
    dc_t  = cdiv(r_chem0, r_chem1_t)

    targeted_results[K_rand] = dict(div_tap=dt_t, div_chem=dc_t)
    print(f"  K_rand={K_rand:3d}+tap+chem: div_tap={dt_t:.4f}, div_chem={dc_t:.4f}")

# -------------------------------------------------------------------
# Plot
# -------------------------------------------------------------------
K_arr  = np.array(K_values)
fr_arr = np.array([results[K]["frob"]     for K in K_values])
pr_arr = np.array([results[K]["pearson"]  for K in K_values])
dt_arr = np.array([results[K]["div_tap"]  for K in K_values])
dc_arr = np.array([results[K]["div_chem"] for K in K_values])

D_EFF = 28
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Generative Model Test v3 — Per-Neuron Dynamical Regression\n"
             "C. elegans: Activity -> Weight Reconstruction vs K conditions", fontsize=11)

ax = axes[0]
ax.plot(K_arr, fr_arr, "o-", color="steelblue", lw=2)
ax.axvline(D_EFF, color="red", ls="--", lw=1.5, label=f"d_eff={D_EFF}")
ax.set_xlabel("Conditions K"); ax.set_ylabel("||W_hat-W||/||W||")
ax.set_title("Structural Reconstruction Error")
ax.set_xscale("log"); ax.legend(); ax.grid(True, alpha=0.3)

ax = axes[1]
ax.plot(K_arr, pr_arr, "o-", color="darkorange", lw=2)
ax.axvline(D_EFF, color="red", ls="--", lw=1.5, label=f"d_eff={D_EFF}")
ax.axhline(0.9, color="gray", ls=":", lw=1.2, label="r=0.90")
ax.set_xlabel("Conditions K"); ax.set_ylabel("Pearson r (nonzero W)")
ax.set_title("Weight Correlation")
ax.set_xscale("log"); ax.set_ylim(-0.1, 1.1); ax.legend(); ax.grid(True, alpha=0.3)

ax = axes[2]
ax.plot(K_arr, dt_arr, "o-",  color="forestgreen", lw=2, label="Tap (random only)")
ax.plot(K_arr, dc_arr, "s--", color="purple",      lw=2, label="Chem (random only)")
K_targ = sorted(targeted_results.keys())
dt_targ = [targeted_results[k]["div_tap"]  for k in K_targ]
dc_targ = [targeted_results[k]["div_chem"] for k in K_targ]
ax.plot(K_targ, dt_targ, "^:",  color="darkgreen",  lw=2, alpha=0.8, label="Tap (+tap+chem train)")
ax.plot(K_targ, dc_targ, "v:",  color="darkviolet", lw=2, alpha=0.8, label="Chem (+tap+chem train)")
ax.axvline(D_EFF, color="red",  ls="--", lw=1.5, label=f"d_eff={D_EFF}")
ax.axhline(0.05,  color="gray", ls=":",  lw=1.2, label="5% threshold")
ax.set_xlabel("K random conditions"); ax.set_ylabel("Behavioral divergence")
ax.set_title("Behavioral Equivalence\n(random only vs. +tap+chem training)")
ax.set_xscale("log"); ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("simulation/results/generative_model_test.png", dpi=150)
plt.close()
print("\nSaved: simulation/results/generative_model_test.png")

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

samples_per_cond = T_pc
K_pred = max(1, int(np.ceil(D_EFF / samples_per_cond)))

lines = [
    "Generative Model Test v3 (Per-Neuron Dynamical Regression)",
    "===========================================================",
    f"N={N}, d_eff={D_EFF}, T={T_ms}ms/cond, sub={SUB} ({SUB*params.dt}ms), samples/cond={samples_per_cond}",
    f"Ridge lambda={lambda_r}",
    "",
    "Method: z_j(t) = atanh((r_j(t+1)-r_j(t))*tau/dt + r_j(t)) / gain - I_gap_j - I_ext_j",
    "        = sum_i W[i,j] r_i(t)  [exact, no approximation]",
    "Valid: r_j(t+1) > eps (lower clip not active).",
    "Per-neuron A_j: subtract invalid-step contribution from global A.",
    f"Consistency check: mean|z-X@W|_valid = {check:.2e}  [~0 = exact]",
    "",
    f"{'K':>5}  {'frob':>8}  {'pearson':>8}  {'div_tap':>9}  {'div_chem':>9}",
]
for K in K_values:
    r = results[K]
    lines.append(f"{K:5d}  {r['frob']:8.4f}  {r['pearson']:8.4f}  "
                 f"{r['div_tap']:9.4f}  {r['div_chem']:9.4f}")

lines += [
    "",
    f"Threshold K for div_tap < 5%:  {thresh_tap  if thresh_tap  else f'>{K_values[-1]}'}",
    f"Threshold K for div_chem < 5%: {thresh_chem if thresh_chem else f'>{K_values[-1]}'}",
    f"Threshold K for pearson >= 0.9: {thresh_r   if thresh_r   else f'>{K_values[-1]}'}",
    "",
    f"Theoretical K prediction: d_eff / samples_per_cond = {D_EFF}/{samples_per_cond} = {K_pred}",
    "",
    "Assumptions:",
    "  [KNOWN IN SIM] G used in z computation. Real: estimated from structural sample.",
    "  [ESTABLISHED] Dynamical regression exact for rate model (no approximation).",
    "  [THIS PROJECT] d_eff=28 from three-organism scaling law.",
    "",
    "Prediction status:",
    f"  Tap:  K_thresh={thresh_tap} vs K_pred={K_pred}: "
    + ("CONFIRMED" if thresh_tap and thresh_tap <= max(K_pred, 5) else
       "MIXED" if thresh_tap else "FAILED"),
    f"  Chem: K_thresh={thresh_chem} vs K_pred={K_pred}: "
    + ("CONFIRMED" if thresh_chem and thresh_chem <= max(K_pred, 5) else
       "MIXED" if thresh_chem else "FAILED"),
]

summary = "\n".join(lines)
print(summary)
with open("simulation/results/generative_model_test_summary.txt", "w",
          encoding="utf-8") as f:
    f.write(summary)

np.savez("simulation/results/generative_model_test.npz",
         K_values=K_values, frob=fr_arr, pearson=pr_arr,
         div_tap=dt_arr, div_chem=dc_arr, d_eff=D_EFF,
         W_true=W, W_hat_best=results[K_values[-1]]["W_hat"],
         consistency_check=check)
print("Done.")
