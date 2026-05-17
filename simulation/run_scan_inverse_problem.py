"""
Scan inverse problem: recover a UNIFIED connectome W that drives multiple
behaviors simultaneously.

Standalone modular result (run_generative_model_modular.py):
  K=1 (tap-targeted only):  div_tap=0.005 ✓, div_chem=0.44 ✗
  K=2 (tap + chem):         div_tap=0.39 ✗, div_chem=0.007 ✓
  K=8+:                     numerical blowup (frob > 25)

The argmax-modular combination assigns each neuron to a single condition. At K=2,
this means some tap-circuit neurons get assigned to the chem condition (because
that's where their score is highest), and their weights are estimated from data
where they are barely active. Bad.

This script tests four candidate fixes:

  (A) MANY-CONDITION COMBINED ridge regression, with adaptive ridge that scales
      with the per-neuron observability spectrum (avoids the K>=8 blowup).
  (B) WEIGHTED-BLEND modular: per-neuron weighted average across conditions
      (softmax over scores instead of argmax).
  (C) ITERATIVE REFINEMENT: start from modular argmax, then re-fit using
      activity predicted from the unified W (one-shot fixed point pass).
  (D) DIVERSE COMPOSITIONAL stimuli: 20 conditions targeting random subsets
      of 30-80 neurons each at moderate amplitudes, giving every neuron
      enough independent activation patterns.

Output: which approach (or combination) achieves Pearson r > 0.9 AND
both div_tap < 0.05 AND div_chem < 0.05 on a unified W.
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

print("=" * 72)
print("SCAN INVERSE PROBLEM -- search for a unified W")
print("=" * 72)

# -----------------------------------------------------------------------------
# Setup
# -----------------------------------------------------------------------------
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
W_TRUE = W_norm * params.w_chem
G = G_norm * params.w_gap
G_rowsum = G.sum(axis=1)
nz_mask = (W_TRUE.flatten() > 1e-6)

tap_neurons  = {"ALML", "ALMR", "AVM", "PLML", "PLMR", "PVM"}
chem_neurons = {"AWCL", "AWCR", "ASEL", "ASER"}
tap_idx  = [i for i, n in enumerate(neurons) if n in tap_neurons]
chem_idx = [i for i, n in enumerate(neurons) if n in chem_neurons]

T_ms      = 600.0
T_steps   = int(T_ms / params.dt)
SUB       = 20
EPS       = 0.001
PULSE_DUR = int(30.0 / params.dt)
ratio     = params.tau / params.dt

# -----------------------------------------------------------------------------
# Stimulus generators
# -----------------------------------------------------------------------------
def make_targeted_pulsed(rng, target_idx, amplitude, n_pulses=4):
    I = np.zeros((T_steps, N))
    for _ in range(n_pulses):
        onset = rng.integers(0, max(1, T_steps - PULSE_DUR))
        for idx in target_idx:
            I[onset:onset+PULSE_DUR, idx] = amplitude * rng.uniform(0.7, 1.3)
    return I

def make_random_subset_pulsed(rng, n_pulses=5, subset_lo=30, subset_hi=80,
                              amp_lo=1.0, amp_hi=2.0):
    """Compositional probe: hit random subsets of N neurons at moderate amp."""
    I = np.zeros((T_steps, N))
    for _ in range(n_pulses):
        onset = rng.integers(0, max(1, T_steps - PULSE_DUR))
        n_d   = rng.integers(subset_lo, subset_hi)
        idx   = rng.choice(N, size=n_d, replace=False)
        amp   = rng.uniform(amp_lo, amp_hi, size=n_d)
        I[onset:onset+PULSE_DUR, idx] += amp
    return I

# -----------------------------------------------------------------------------
# Build K_total = 20 conditions: 2 targeted tap + 2 targeted chem + 16 compositional
# -----------------------------------------------------------------------------
rng = np.random.default_rng(11)
stimuli = []
labels  = []
for _ in range(2):
    stimuli.append(make_targeted_pulsed(rng, tap_idx,  1.5));  labels.append("tap")
    stimuli.append(make_targeted_pulsed(rng, chem_idx, 1.5));  labels.append("chem")
for _ in range(16):
    stimuli.append(make_random_subset_pulsed(rng));  labels.append("rand")

K_TOTAL = len(stimuli)
print(f"\nK_total = {K_TOTAL} conditions ({labels.count('tap')} tap + "
      f"{labels.count('chem')} chem + {labels.count('rand')} compositional)")

# -----------------------------------------------------------------------------
# Run simulations and build per-condition (X, z, valid) tensors
# -----------------------------------------------------------------------------
print("Simulating...")
cond = []
for k, I_k in enumerate(stimuli):
    r = simulate_rate(W_norm, G_norm, I_k, T_ms, params)["r"]
    t_idx = np.arange(0, T_steps - 1, SUB)
    X_k   = r[t_idx].astype(np.float64)
    Xp_k  = r[t_idx + 1].astype(np.float64)
    Ie_k  = I_k[t_idx].astype(np.float64)

    valid_k = Xp_k > EPS
    tanh_arg = (Xp_k - X_k) * ratio + X_k
    valid_k &= (tanh_arg > -0.9999) & (tanh_arg < 0.9999)
    I_gap_k = X_k @ G.T - X_k * G_rowsum[np.newaxis, :]
    z_k = np.arctanh(np.clip(tanh_arg, -0.9999, 0.9999)) / params.gain - I_gap_k - Ie_k
    cond.append(dict(X=X_k, z=z_k, valid=valid_k, fv=valid_k.mean(axis=0)))

# Helpers ---------------------------------------------------------------------
ws, we     = int(100/params.dt), int(500/params.dt)
T_test     = 600.0
I_tap_test  = make_tap_input(N, neurons, T_test, params.dt,
                              onset_ms=50.0, duration_ms=30.0, amplitude=4.0)
I_chem_test = make_chem_input(N, neurons, T_test, params.dt, amplitude=3.0)
r_tap_orig  = simulate_rate(W_norm, G_norm, I_tap_test,  T_test, params)["r"][ws:we].flatten()
r_chem_orig = simulate_rate(W_norm, G_norm, I_chem_test, T_test, params)["r"][ws:we].flatten()

def cdiv(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 1.0 - np.dot(a, b)/(na*nb) if na > 1e-10 and nb > 1e-10 else 1.0

def evaluate(W_hat):
    Wh_norm = np.clip(W_hat / params.w_chem, 0, None)
    r_tap  = simulate_rate(Wh_norm, G_norm, I_tap_test,  T_test, params)["r"][ws:we].flatten()
    r_chem = simulate_rate(Wh_norm, G_norm, I_chem_test, T_test, params)["r"][ws:we].flatten()
    frob = np.linalg.norm(W_hat - W_TRUE) / np.linalg.norm(W_TRUE)
    pr   = pearsonr(W_TRUE.flatten()[nz_mask], W_hat.flatten()[nz_mask])[0]
    return dict(frob=frob, pearson=pr,
                div_tap=cdiv(r_tap_orig, r_tap),
                div_chem=cdiv(r_chem_orig, r_chem))

def fit_per_condition(X_k, z_k, valid_k, lam):
    Wh = np.zeros((N, N))
    A_k = X_k.T @ X_k
    B_k = X_k.T @ (z_k * valid_k.astype(float))
    for j in range(N):
        inv_j = ~valid_k[:, j]
        A_j   = A_k - X_k[inv_j].T @ X_k[inv_j] + lam * np.eye(N)
        Wh[:, j] = np.linalg.solve(A_j, B_k[:, j])
    Wh[:, valid_k.mean(axis=0) < 0.05] = 0.0
    return Wh

# Compute per-condition W_hat with adaptive ridge (scale lambda with X's spectrum)
print("\nFitting per-condition W_hats with adaptive ridge...")
W_hats = []
for k in range(K_TOTAL):
    X_k = cond[k]["X"]
    s = np.linalg.svd(X_k, compute_uv=False)
    lam = max(1e-3, 1e-3 * s[0]**2 / N)
    Wh = fit_per_condition(X_k, cond[k]["z"], cond[k]["valid"], lam)
    W_hats.append(Wh)

# -----------------------------------------------------------------------------
# Approach A: combined ridge, all K conditions stacked
# -----------------------------------------------------------------------------
print("\n[Approach A] Combined ridge over all K conditions")
X_all  = np.concatenate([c["X"]     for c in cond], axis=0)
z_all  = np.concatenate([c["z"]     for c in cond], axis=0)
v_all  = np.concatenate([c["valid"] for c in cond], axis=0)
s_all  = np.linalg.svd(X_all, compute_uv=False)
lam_A  = max(1e-2, 1e-3 * s_all[0]**2 / N)
W_A    = fit_per_condition(X_all, z_all, v_all, lam_A)
res_A  = evaluate(W_A)
print(f"  lambda={lam_A:.3e}  frob={res_A['frob']:.4f}  r={res_A['pearson']:.4f}  "
      f"div_tap={res_A['div_tap']:.4f}  div_chem={res_A['div_chem']:.4f}")

# -----------------------------------------------------------------------------
# Approach B: weighted blend (softmax over score)
# -----------------------------------------------------------------------------
print("\n[Approach B] Weighted blend modular")
scores = np.zeros((K_TOTAL, N))
for k in range(K_TOTAL):
    scores[k] = cond[k]["fv"] * cond[k]["X"].var(axis=0)
# softmax with temperature
for tau in [0.5, 1.0, 2.0, 4.0]:
    s_norm = scores / (scores.max(axis=0, keepdims=True) + 1e-12)
    w = np.exp(tau * s_norm)
    w /= w.sum(axis=0, keepdims=True)   # (K, N) softmax weights per neuron
    W_B = np.zeros((N, N))
    for j in range(N):
        for k in range(K_TOTAL):
            W_B[:, j] += w[k, j] * W_hats[k][:, j]
    r = evaluate(W_B)
    print(f"  tau={tau:.1f}  frob={r['frob']:.4f}  r={r['pearson']:.4f}  "
          f"div_tap={r['div_tap']:.4f}  div_chem={r['div_chem']:.4f}")
    if tau == 2.0:
        res_B = r; W_B_best = W_B

# -----------------------------------------------------------------------------
# Approach C: iterative refinement
# -----------------------------------------------------------------------------
print("\n[Approach C] Iterative refinement starting from modular argmax")
best_cond = scores.argmax(axis=0)
W_C = np.zeros((N, N))
for j in range(N):
    W_C[:, j] = W_hats[best_cond[j]][:, j]
print(f"  initial argmax-modular:  frob={evaluate(W_C)['frob']:.4f}  "
      f"r={evaluate(W_C)['pearson']:.4f}")

# Iterate: use W_C to predict activity, then re-fit per-neuron using stacked
# residuals across all K conditions (each condition contributes to each neuron j
# weighted by that condition's score for j).
for it in range(3):
    # Re-fit each neuron j using a per-condition observation weighted by score[:,j].
    W_new = np.zeros((N, N))
    for j in range(N):
        # Stack data across conditions, weight rows by score for neuron j
        w_j = scores[:, j] / (scores[:, j].sum() + 1e-12)
        # Build weighted normal equations
        A = np.zeros((N, N))
        b = np.zeros(N)
        for k in range(K_TOTAL):
            if w_j[k] < 1e-3: continue
            X_k = cond[k]["X"]; z_k = cond[k]["z"]; v_k = cond[k]["valid"]
            valid_j = v_k[:, j]
            X_kj = X_k[valid_j]
            z_kj = z_k[valid_j, j]
            A += w_j[k] * (X_kj.T @ X_kj)
            b += w_j[k] * (X_kj.T @ z_kj)
        A += 1e-3 * np.eye(N)
        W_new[:, j] = np.linalg.solve(A, b)
    W_C = W_new
    r = evaluate(W_C)
    print(f"  iter {it+1}:  frob={r['frob']:.4f}  r={r['pearson']:.4f}  "
          f"div_tap={r['div_tap']:.4f}  div_chem={r['div_chem']:.4f}")
res_C = r

# -----------------------------------------------------------------------------
# Approach D: support-aware fit -- restrict regression to known nonzero columns
# -----------------------------------------------------------------------------
print("\n[Approach D] Support-aware combined regression")
print("  Assumption: the scanner knows the binary support (which neurons connect).")
print("  Fit only the nonzero weights per neuron (much smaller least-squares per j).")
W_D = np.zeros((N, N))
support = (W_TRUE > 0)
for j in range(N):
    supp_j = np.where(support[:, j])[0]
    if len(supp_j) == 0:
        continue
    X_sub = X_all[:, supp_j]
    valid_j = v_all[:, j]
    Xv = X_sub[valid_j]
    zv = z_all[valid_j, j]
    A = Xv.T @ Xv + 1e-3 * np.eye(len(supp_j))
    b = Xv.T @ zv
    w_j = np.linalg.solve(A, b)
    W_D[supp_j, j] = np.clip(w_j, 0, None)   # biological: non-negative chemical weights
res_D = evaluate(W_D)
print(f"  frob={res_D['frob']:.4f}  r={res_D['pearson']:.4f}  "
      f"div_tap={res_D['div_tap']:.4f}  div_chem={res_D['div_chem']:.4f}")

# -----------------------------------------------------------------------------
# Approach E: support-aware + per-neuron weighted condition selection
# For each neuron j, the topology gives us its ~12 nonzero inputs.
# Different conditions activate j by different amounts; we weight each condition's
# data by how strongly it drives j (variance of j during that condition).
# -----------------------------------------------------------------------------
print("\n[Approach E] Support-aware + per-neuron condition weighting")
W_E = np.zeros((N, N))
for j in range(N):
    supp_j = np.where(support[:, j])[0]
    if len(supp_j) == 0:
        continue

    # weights: how much each condition activates neuron j
    activations = np.array([cond[k]["X"][:, j].var() for k in range(K_TOTAL)])
    if activations.sum() < 1e-12:
        continue
    w_k = activations / activations.sum()                # (K,)

    A = np.zeros((len(supp_j), len(supp_j)))
    b = np.zeros(len(supp_j))
    for k in range(K_TOTAL):
        if w_k[k] < 1e-4: continue
        X_k = cond[k]["X"][:, supp_j]
        v_kj = cond[k]["valid"][:, j]
        z_kj = cond[k]["z"][v_kj, j]
        Xv = X_k[v_kj]
        A += w_k[k] * (Xv.T @ Xv)
        b += w_k[k] * (Xv.T @ z_kj)
    A += 1e-3 * np.eye(len(supp_j))
    w_sol = np.linalg.solve(A, b)
    W_E[supp_j, j] = np.clip(w_sol, 0, None)
res_E = evaluate(W_E)
print(f"  frob={res_E['frob']:.4f}  r={res_E['pearson']:.4f}  "
      f"div_tap={res_E['div_tap']:.4f}  div_chem={res_E['div_chem']:.4f}")

# -----------------------------------------------------------------------------
# Approach F: support-aware modular (per-neuron, pick best condition, fit on support)
# This combines the two ingredients that each worked separately:
#   * known support (Approach D): cuts unknowns from N=300 to ~12 per neuron
#   * per-neuron condition selection (standalone K=1 modular): isolates the
#     condition where neuron j is best observed, avoiding cross-circuit contamination
# -----------------------------------------------------------------------------
print("\n[Approach F] Support-aware modular (per-neuron best condition, on support)")
W_F = np.zeros((N, N))
for j in range(N):
    supp_j = np.where(support[:, j])[0]
    if len(supp_j) == 0:
        continue
    # pick the condition where j is most active AND well-observed
    scores_j = np.array([cond[k]["X"][:, j].var() * cond[k]["fv"][j] for k in range(K_TOTAL)])
    if scores_j.max() < 1e-12:
        continue
    k_best = int(scores_j.argmax())
    X_k = cond[k_best]["X"][:, supp_j]
    v_kj = cond[k_best]["valid"][:, j]
    Xv = X_k[v_kj]
    zv = cond[k_best]["z"][v_kj, j]
    A  = Xv.T @ Xv + 1e-3 * np.eye(len(supp_j))
    b  = Xv.T @ zv
    W_F[supp_j, j] = np.clip(np.linalg.solve(A, b), 0, None)
res_F = evaluate(W_F)
print(f"  frob={res_F['frob']:.4f}  r={res_F['pearson']:.4f}  "
      f"div_tap={res_F['div_tap']:.4f}  div_chem={res_F['div_chem']:.4f}")

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
def pass_str(r):
    return "PASS" if (r["div_tap"] < 0.05 and r["div_chem"] < 0.05) else "FAIL"

print("\n" + "=" * 72)
print("SUMMARY")
print("=" * 72)
print(f"{'Approach':<28}  {'frob':>8}  {'r':>8}  {'div_tap':>9}  {'div_chem':>9}  verdict")
print("-" * 80)
rows = [
    ("A combined ridge",         res_A),
    ("B weighted blend (tau=2)", res_B),
    ("C iterative refinement",   res_C),
    ("D support-aware combined", res_D),
    ("E support + cond-weighted",res_E),
    ("F support-aware modular",  res_F),
]
for name, r in rows:
    print(f"{name:<28}  {r['frob']:>8.4f}  {r['pearson']:>8.4f}  "
          f"{r['div_tap']:>9.4f}  {r['div_chem']:>9.4f}  {pass_str(r)}")

best_name, best_r = min(rows, key=lambda x: x[1]["div_tap"] + x[1]["div_chem"])
print(f"\nBest unified W: {best_name}")
print(f"  Pearson r = {best_r['pearson']:.4f}")
print(f"  div_tap   = {best_r['div_tap']:.4f}  [{'PASS' if best_r['div_tap']<0.05 else 'FAIL'}]")
print(f"  div_chem  = {best_r['div_chem']:.4f}  [{'PASS' if best_r['div_chem']<0.05 else 'FAIL'}]")

# Plot
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
names_short = ["A combined", "B blend", "C iter", "D support", "E supp+wgt", "F supp+mod"]
divs_tap  = [r[1]["div_tap"]  for r in rows]
divs_chem = [r[1]["div_chem"] for r in rows]
pearsons  = [r[1]["pearson"]  for r in rows]

x = np.arange(len(names_short)); w = 0.35
axes[0].bar(x - w/2, divs_tap,  w, label="tap",  color="steelblue")
axes[0].bar(x + w/2, divs_chem, w, label="chem", color="darkorange")
axes[0].axhline(0.05, color="red", ls="--", label="5% threshold")
axes[0].set_yscale("log"); axes[0].set_xticks(x); axes[0].set_xticklabels(names_short)
axes[0].set_ylabel("behavioral divergence"); axes[0].legend(); axes[0].grid(alpha=0.3, axis="y")
axes[0].set_title("Behavioral divergence per approach")

axes[1].bar(x, pearsons, color="purple")
axes[1].axhline(0.9, color="red", ls="--", label="r = 0.9")
axes[1].set_xticks(x); axes[1].set_xticklabels(names_short)
axes[1].set_ylabel("Pearson r (W_hat vs W_true)")
axes[1].set_title("Weight-matrix correlation"); axes[1].legend(); axes[1].grid(alpha=0.3, axis="y")
axes[1].set_ylim(0, 1.05)

plt.tight_layout()
plt.savefig("simulation/results/scan_inverse_problem.png", dpi=150)
plt.close()
print("\nSaved: simulation/results/scan_inverse_problem.png")

# Save numbers
with open("simulation/results/scan_inverse_problem_summary.txt", "w", encoding="utf-8") as f:
    f.write("Scan Inverse Problem -- search for a unified W\n")
    f.write("=" * 52 + "\n")
    f.write(f"K_total = {K_TOTAL} conditions\n\n")
    f.write(f"{'Approach':<28}  {'frob':>8}  {'r':>8}  {'div_tap':>9}  {'div_chem':>9}  verdict\n")
    for name, r in rows:
        f.write(f"{name:<28}  {r['frob']:>8.4f}  {r['pearson']:>8.4f}  "
                f"{r['div_tap']:>9.4f}  {r['div_chem']:>9.4f}  {pass_str(r)}\n")
    f.write(f"\nBest unified W: {best_name}\n")

np.savez("simulation/results/scan_inverse_problem.npz",
         W_TRUE=W_TRUE,
         W_A=W_A, W_B=W_B_best, W_C=W_C, W_D=W_D, W_E=W_E, W_F=W_F,
         res_A=res_A, res_B=res_B, res_C=res_C, res_D=res_D, res_E=res_E, res_F=res_F)
print("Done.")
