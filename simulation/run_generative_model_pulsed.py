"""
Generative model test — Prediction 3, pulsed training stimuli.

Previous result (v3, constant drive): div_tap stuck at 60-70% even at K=50.
Root cause: constant drive saturates tap neurons at r~0.97. Regression near
tanh saturation is ill-conditioned. Transient test (30ms pulse) probes dynamics
that constant training never spanned.

This version: replace constant training stimuli with pulsed stimuli matching
the temporal structure of the tap test (30ms pulses at random neurons).

Prediction: div_tap drops to <5% for K ~ a few pulsed conditions.
If confirmed: the scanner prediction holds, but the correct protocol is
pulsed/naturalistic behavioral recording, not constant random drive.
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
# Pulsed stimuli — each condition is a 600ms trial with multiple
# 30ms pulses at random neurons, matching the tap test structure.
# -------------------------------------------------------------------
rng = np.random.default_rng(99)
T_ms    = 600.0
T_steps = int(T_ms / params.dt)   # 1200
SUB     = 20
EPS     = 0.001
PULSE_DUR_MS  = 30.0
PULSE_DUR_STEPS = int(PULSE_DUR_MS / params.dt)   # 60 steps

K_values = [1, 2, 3, 5, 8, 10, 15, 20, 30, 50]
K_max    = max(K_values)

def make_pulsed_stimulus(rng, N, T_steps, dt,
                          n_pulses_range=(2, 6),
                          n_neurons_range=(5, 40),
                          amplitude_range=(2.0, 5.0),
                          pulse_dur_steps=PULSE_DUR_STEPS):
    """Build a (T_steps, N) stimulus array with random short pulses."""
    I = np.zeros((T_steps, N))
    n_pulses = rng.integers(*n_pulses_range)
    for _ in range(n_pulses):
        onset = rng.integers(0, T_steps - pulse_dur_steps)
        n_d   = rng.integers(*n_neurons_range)
        idx   = rng.choice(N, size=n_d, replace=False)
        amp   = rng.uniform(*amplitude_range, size=n_d)
        I[onset:onset + pulse_dur_steps, idx] += amp
    return I

print(f"\nGenerating {K_max} pulsed conditions (T={T_ms}ms, pulse={PULSE_DUR_MS}ms)...")
stimuli_full = []
for k in range(K_max):
    stimuli_full.append(make_pulsed_stimulus(rng, N, T_steps, params.dt))

print("Simulating pulsed conditions...")
r_t_list, r_tp1_list, I_list = [], [], []
for k in range(K_max):
    if (k+1) % 10 == 0:
        print(f"  {k+1}/{K_max}")
    r = simulate_rate(W_norm, G_norm, stimuli_full[k], T_ms, params)["r"]
    t_idx = np.arange(0, T_steps - 1, SUB)
    r_t_list.append(r[t_idx].astype(np.float64))
    r_tp1_list.append(r[t_idx + 1].astype(np.float64))
    I_list.append(stimuli_full[k][t_idx].astype(np.float64))

T_pc    = r_t_list[0].shape[0]
T_total = T_pc * K_max

X_all  = np.concatenate(r_t_list,   axis=0)
Xp_all = np.concatenate(r_tp1_list, axis=0)
Ie_all = np.concatenate(I_list,     axis=0)

print(f"T_pc={T_pc}, T_total={T_total}")
print(f"Activity: mean={X_all.mean():.4f}, frac>{EPS}: {(X_all > EPS).mean():.3f}")

valid    = Xp_all > EPS
ratio    = params.tau / params.dt
tanh_arg = (Xp_all - X_all) * ratio + X_all
valid   &= (tanh_arg > -0.9999) & (tanh_arg < 0.9999)

frac_valid = valid.mean(axis=0)
print(f"Validity: mean={frac_valid.mean():.3f}, min={frac_valid.min():.3f}")

I_gap_all = X_all @ G.T - X_all * G_rowsum[np.newaxis, :]
z_all     = np.arctanh(np.clip(tanh_arg, -0.9999, 0.9999)) / params.gain \
            - I_gap_all - Ie_all

z_expected = X_all @ W
check = np.abs((z_all - z_expected)[valid]).mean()
print(f"Consistency check (valid): mean|z - X@W| = {check:.3e}  [expect ~0]")

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
# Per-neuron ridge regression
# -------------------------------------------------------------------
lambda_r = 1e-4
print(f"\nPer-neuron ridge regression (lambda={lambda_r})...")
results = {}

for K in K_values:
    T_K = K * T_pc
    X_K = X_all[:T_K]
    z_K = z_all[:T_K]
    v_K = valid[:T_K]

    A_K = X_K.T @ X_K
    B_K = X_K.T @ (z_K * v_K.astype(float))

    W_hat = np.zeros((N, N))
    for j in range(N):
        inv_j   = ~v_K[:, j]
        X_inv_j = X_K[inv_j]
        A_inv_j = X_inv_j.T @ X_inv_j
        A_j     = A_K - A_inv_j + lambda_r * np.eye(N)
        b_j     = B_K[:, j]
        W_hat[:, j] = np.linalg.solve(A_j, b_j)

    frac_valid_K = v_K.mean(axis=0)
    W_hat[:, frac_valid_K < 0.05] = 0.0

    frob = np.linalg.norm(W_hat - W) / (np.linalg.norm(W) + 1e-10)
    nz   = W.flatten() > 1e-6
    pr   = pearsonr(W.flatten()[nz], W_hat.flatten()[nz])[0] if nz.sum() > 5 else 0.0

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
# Tap neuron activity check — key diagnostic
# -------------------------------------------------------------------
tap_neurons  = {"ALML", "ALMR", "AVM", "PLML", "PLMR", "PVM"}
chem_neurons = {"AWCL", "AWCR", "ASEL", "ASER"}
tap_idx  = [i for i, n in enumerate(neurons) if n in tap_neurons]
chem_idx = [i for i, n in enumerate(neurons) if n in chem_neurons]

# Mean activity of tap neurons at the subset of frames that are NOT
# saturated (r < 0.9) — these are the frames where regression is well-conditioned
tap_act = X_all[:, tap_idx]
tap_unsaturated_mean = tap_act[tap_act < 0.9].mean() if (tap_act < 0.9).any() else 0.0
print(f"\nTap neuron activity in pulsed training data:")
print(f"  overall mean:              {tap_act.mean():.4f}")
print(f"  mean when unsaturated (<0.9): {tap_unsaturated_mean:.4f}")
print(f"  frac saturated (>0.9):     {(tap_act > 0.9).mean():.4f}")
print(f"Chem neuron mean activity: {X_all[:, chem_idx].mean():.4f}")
print(f"Global mean activity:      {X_all.mean():.4f}")

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
fig.suptitle("Generative Model Test — Pulsed Training Stimuli\n"
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
ax.plot(K_arr, dt_arr, "o-",  color="forestgreen", lw=2, label="Tap")
ax.plot(K_arr, dc_arr, "s--", color="purple",      lw=2, label="Chem")
ax.axvline(D_EFF, color="red",  ls="--", lw=1.5, label=f"d_eff={D_EFF}")
ax.axhline(0.05,  color="gray", ls=":",  lw=1.2, label="5% threshold")
ax.set_xlabel("K pulsed conditions"); ax.set_ylabel("Behavioral divergence")
ax.set_title("Behavioral Equivalence\n(pulsed training)")
ax.set_xscale("log"); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("simulation/results/generative_model_pulsed.png", dpi=150)
plt.close()
print("\nSaved: simulation/results/generative_model_pulsed.png")

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
    "Generative Model Test — Pulsed Training Stimuli",
    "================================================",
    f"N={N}, d_eff={D_EFF}, T={T_ms}ms/cond, sub={SUB} ({SUB*params.dt}ms), samples/cond={samples_per_cond}",
    f"Pulse duration: {PULSE_DUR_MS}ms, random onset, random neurons",
    f"Ridge lambda={lambda_r}",
    "",
    "Hypothesis: constant-drive training saturates tap neurons (tanh flat at +1),",
    "making regression ill-conditioned for transient test stimuli.",
    "Pulsed training spans the transient regime and should fix div_tap.",
    "",
    f"{'K':>5}  {'frob':>8}  {'pearson':>8}  {'div_tap':>9}  {'div_chem':>9}",
]
for K in K_values:
    r = results[K]
    lines.append(f"{K:5d}  {r['frob']:8.4f}  {r['pearson']:8.4f}  "
                 f"{r['div_tap']:9.4f}  {r['div_chem']:9.4f}")

lines += [
    "",
    f"Threshold K for div_tap  < 5%:  {thresh_tap  if thresh_tap  else f'>{K_values[-1]}'}",
    f"Threshold K for div_chem < 5%:  {thresh_chem if thresh_chem else f'>{K_values[-1]}'}",
    f"Threshold K for pearson >= 0.9: {thresh_r    if thresh_r    else f'>{K_values[-1]}'}",
    "",
    f"Theoretical K prediction: d_eff / samples_per_cond = {D_EFF}/{samples_per_cond} = {K_pred}",
    "",
    "Assumptions:",
    "  [KNOWN IN SIM] G used in z computation. Real scanner: estimated from structural sample.",
    "  [ESTABLISHED] Dynamical regression exact for this rate model.",
    "  [THIS PROJECT] d_eff=28 from three-organism scaling law.",
    "  [THIS EXPERIMENT] Pulsed stimuli match test temporal structure (transient dynamics).",
    "",
    "Prediction status:",
    f"  Tap:  K_thresh={thresh_tap} vs K_pred={K_pred}: "
    + ("CONFIRMED" if thresh_tap and thresh_tap <= max(K_pred, 5) else
       "MIXED" if thresh_tap else "FAILED — tap circuit requires additional structure"),
    f"  Chem: K_thresh={thresh_chem} vs K_pred={K_pred}: "
    + ("CONFIRMED" if thresh_chem and thresh_chem <= max(K_pred, 5) else
       "MIXED" if thresh_chem else "FAILED"),
    "",
    "Comparison to v3 (constant drive):",
    "  If pulsed fixes tap: training protocol is the scanner spec (naturalistic/pulsed recording).",
    "  If pulsed fails: tap circuit has gap-junction or history-dependent structure",
    "  not captured by the rate model — more data or a different model class required.",
]

summary = "\n".join(lines)
print(summary)
with open("simulation/results/generative_model_pulsed_summary.txt", "w",
          encoding="utf-8") as f:
    f.write(summary)

np.savez("simulation/results/generative_model_pulsed.npz",
         K_values=K_values, frob=fr_arr, pearson=pr_arr,
         div_tap=dt_arr, div_chem=dc_arr, d_eff=D_EFF,
         W_true=W, W_hat_best=results[K_values[-1]]["W_hat"],
         consistency_check=check)
print("Done.")
