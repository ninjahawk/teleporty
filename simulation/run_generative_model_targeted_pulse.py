"""
Generative model test — targeted pulsed training stimuli.

History:
  v3 (constant random): div_tap stuck 60-70%. Tap neurons saturated at r~0.97.
  pulsed random: div_tap stuck 60-70%. Tap neurons underactivated (mean r=0.014).

Root cause of both failures: tap neurons never in the well-conditioned linear
regime (tanh' ~ 1, r in 0.2-0.7) during training.

This experiment: pulsed stimuli specifically targeting tap neurons at moderate
amplitude (1.5), putting r_tap in [0.2, 0.7]. This is the only untested regime.

If this works: the scanner protocol must include stimuli that activate each
sensory circuit in its linear dynamic range. Implication for the teleportation
scanner: structured probe signals, not random.

If this also fails: the tap circuit has a structural property (e.g. gap junction
dominance, precise timing requirement) that requires lower distortion tolerance
than chemotaxis. The 30% distortion tolerance is behavior-class-specific.
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

tap_neurons  = {"ALML", "ALMR", "AVM", "PLML", "PLMR", "PVM"}
chem_neurons = {"AWCL", "AWCR", "ASEL", "ASER"}
tap_idx  = [i for i, n in enumerate(neurons) if n in tap_neurons]
chem_idx = [i for i, n in enumerate(neurons) if n in chem_neurons]

rng = np.random.default_rng(7)
T_ms      = 600.0
T_steps   = int(T_ms / params.dt)
SUB       = 20
EPS       = 0.001

PULSE_DUR_STEPS = int(30.0 / params.dt)   # 60 steps = 30ms

# -------------------------------------------------------------------
# Amplitude sweep: find the regime where tap neurons are in [0.2, 0.7]
# -------------------------------------------------------------------
print("\nAmplitude sweep for tap neurons...")
for amp in [0.5, 1.0, 1.5, 2.0, 3.0, 4.0]:
    I_probe = np.zeros((T_steps, N))
    onset = int(50.0 / params.dt)
    for idx in tap_idx:
        I_probe[onset:onset+PULSE_DUR_STEPS, idx] = amp
    r_probe = simulate_rate(W_norm, G_norm, I_probe, T_ms, params)["r"]
    tap_peak = r_probe[onset:onset+PULSE_DUR_STEPS, :][:, tap_idx].max()
    tap_mean_during = r_probe[onset:onset+PULSE_DUR_STEPS, :][:, tap_idx].mean()
    print(f"  amp={amp:.1f}: tap peak={tap_peak:.3f}, mean during pulse={tap_mean_during:.3f}")

# Choose amp=1.5 as the working point (verified to avoid saturation)
TAP_AMP  = 1.5
CHEM_AMP = 1.5

# -------------------------------------------------------------------
# Build targeted pulsed training conditions
# Three types, combined:
#   - Tap-targeted: pulses to tap neurons at TAP_AMP
#   - Chem-targeted: pulses to chem neurons at CHEM_AMP
#   - Mixed random: pulses to random neurons (for global coverage)
# -------------------------------------------------------------------
def make_targeted_pulsed(rng, N, T_steps, target_idx, n_pulses, amplitude,
                          pulse_dur_steps=PULSE_DUR_STEPS):
    """Pulsed stimulus targeting specific neurons."""
    I = np.zeros((T_steps, N))
    for _ in range(n_pulses):
        onset = rng.integers(0, max(1, T_steps - pulse_dur_steps))
        for idx in target_idx:
            I[onset:onset+pulse_dur_steps, idx] = amplitude * rng.uniform(0.7, 1.3)
    return I

def make_random_pulsed(rng, N, T_steps, n_pulses=3, amp_range=(1.0, 3.0),
                        n_neurons_range=(5, 40), pulse_dur_steps=PULSE_DUR_STEPS):
    I = np.zeros((T_steps, N))
    for _ in range(n_pulses):
        onset = rng.integers(0, max(1, T_steps - pulse_dur_steps))
        n_d   = rng.integers(*n_neurons_range)
        idx   = rng.choice(N, size=n_d, replace=False)
        amp   = rng.uniform(*amp_range, size=n_d)
        I[onset:onset+pulse_dur_steps, idx] += amp
    return I

K_values = [1, 2, 3, 5, 8, 10, 15, 20, 30, 50]
K_max    = max(K_values)

# Build K_max conditions: alternating tap-targeted, chem-targeted, random
print(f"\nGenerating {K_max} targeted pulsed conditions...")
stimuli_full = []
for k in range(K_max):
    mod = k % 3
    if mod == 0:
        I_k = make_targeted_pulsed(rng, N, T_steps, tap_idx, n_pulses=4, amplitude=TAP_AMP)
    elif mod == 1:
        I_k = make_targeted_pulsed(rng, N, T_steps, chem_idx, n_pulses=4, amplitude=CHEM_AMP)
    else:
        I_k = make_random_pulsed(rng, N, T_steps)
    stimuli_full.append(I_k)

print("Simulating...")
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

tap_act = X_all[:, tap_idx]
print(f"\nTap neuron activity (targeted pulsed training):")
print(f"  mean={tap_act.mean():.4f}, "
      f"frac in [0.1,0.8]={((tap_act>0.1)&(tap_act<0.8)).mean():.4f}, "
      f"frac saturated(>0.9)={( tap_act>0.9).mean():.4f}")
print(f"Global mean activity: {X_all.mean():.4f}")

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
print(f"Consistency check: mean|z - X@W| = {check:.3e}  [expect ~0]")

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
# Regression — higher lambda for sparse pulsed data
# -------------------------------------------------------------------
lambda_r = 1e-3   # increased from 1e-4 to stabilize sparse activity regime
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
# Plot
# -------------------------------------------------------------------
K_arr  = np.array(K_values)
fr_arr = np.array([results[K]["frob"]     for K in K_values])
pr_arr = np.array([results[K]["pearson"]  for K in K_values])
dt_arr = np.array([results[K]["div_tap"]  for K in K_values])
dc_arr = np.array([results[K]["div_chem"] for K in K_values])

D_EFF = 28
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Generative Model Test — Targeted Pulsed Training\n"
             f"Tap amp={TAP_AMP} (linear regime), Chem amp={CHEM_AMP}, mixed random", fontsize=11)

ax = axes[0]
ax.plot(K_arr, np.minimum(fr_arr, 5.0), "o-", color="steelblue", lw=2)
ax.axvline(D_EFF, color="red", ls="--", lw=1.5, label=f"d_eff={D_EFF}")
ax.set_xlabel("Conditions K"); ax.set_ylabel("||W_hat-W||/||W|| (capped at 5)")
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
ax.set_xlabel("K conditions"); ax.set_ylabel("Behavioral divergence")
ax.set_title("Behavioral Equivalence\n(tap-targeted pulsed training)")
ax.set_xscale("log"); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("simulation/results/generative_model_targeted_pulse.png", dpi=150)
plt.close()
print("\nSaved: simulation/results/generative_model_targeted_pulse.png")

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
K_pred = max(1, int(np.ceil(D_EFF / T_pc)))

lines = [
    "Generative Model Test — Targeted Pulsed Training",
    "=================================================",
    f"N={N}, d_eff={D_EFF}, T={T_ms}ms/cond, sub={SUB}, samples/cond={T_pc}",
    f"Tap amp={TAP_AMP} (linear regime), Chem amp={CHEM_AMP}, cycling tap/chem/random",
    f"Ridge lambda={lambda_r}",
    "",
    f"Tap neuron mean activity: {tap_act.mean():.4f}",
    f"Tap in linear regime [0.1,0.8]: {((tap_act>0.1)&(tap_act<0.8)).mean():.4f}",
    f"Tap saturated (>0.9): {(tap_act>0.9).mean():.4f}",
    f"Consistency check: {check:.2e}",
    "",
    f"{'K':>5}  {'frob':>8}  {'pearson':>8}  {'div_tap':>9}  {'div_chem':>9}",
]
for K in K_values:
    r = results[K]
    lines.append(f"{K:5d}  {r['frob']:8.4f}  {r['pearson']:8.4f}  "
                 f"{r['div_tap']:9.4f}  {r['div_chem']:9.4f}")

tap_status  = ("CONFIRMED" if thresh_tap  and thresh_tap  <= max(K_pred, 5) else
               "PARTIAL"   if thresh_tap  else
               "FAILED — tap circuit requires lower distortion tolerance or different model")
chem_status = ("CONFIRMED" if thresh_chem and thresh_chem <= max(K_pred, 5) else
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
    "Training protocol: 1/3 tap-targeted pulses, 1/3 chem-targeted pulses, 1/3 random pulses.",
    "This ensures target circuit neurons are in the linear tanh regime during training.",
    "",
    "Assumptions:",
    "  [KNOWN IN SIM] G known exactly. Real scanner: G estimated from structural sample.",
    "  [ESTABLISHED] Dynamical regression exact for this rate model.",
    "  [THIS PROJECT] d_eff=28, distortion tolerance D=0.30 (from C. elegans simulation).",
    "  [THIS EXPERIMENT] Linear-regime activation is sufficient for weight observability.",
    "",
    "If tap still fails: the tap circuit distortion tolerance is < 30%.",
    "  This means D is behavior-class-specific — not a universal constant.",
    "  The 42 KB figure is a lower bound valid only for chemotaxis-class behaviors.",
    "  Tap-class (transient) behaviors require higher fidelity reconstruction.",
]

summary = "\n".join(lines)
print(summary)
with open("simulation/results/generative_model_targeted_pulse_summary.txt", "w",
          encoding="utf-8") as f:
    f.write(summary)

np.savez("simulation/results/generative_model_targeted_pulse.npz",
         K_values=K_values, frob=fr_arr, pearson=pr_arr,
         div_tap=dt_arr, div_chem=dc_arr, d_eff=D_EFF, tap_amp=TAP_AMP,
         W_true=W, W_hat_best=results[K_values[-1]]["W_hat"],
         consistency_check=check)
print("Done.")
