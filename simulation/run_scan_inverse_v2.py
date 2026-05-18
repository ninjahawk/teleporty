"""
Scan inverse problem v2 -- attack the tap-circuit blocker.

Background (v1 result, scan_inverse_problem.py):
  Best = Approach D (support-aware combined ridge): r=0.72, div_tap=0.57, div_chem=0.056.
  The TAP circuit weights are 27x smaller than mean. Even with binary topology
  known, joint regression contaminates these small weights. Pearson is fine
  (because dominated by large weights) but relative error on tap weights is
  ~30x worse than on chem/locomotion.

Strategy here:
  (1) SUSTAINED TONIC PROBES (not brief pulses): drive each behavior class with a
      step input that runs for hundreds of ms, then sample the STEADY STATE only.
      Removes time-derivative noise from the arctanh linearization.
  (2) PER-CLASS ISOLATION: every probe condition stimulates ONLY one class's
      sensors. No random background. The postsynaptic targets see a clean,
      single-source drive.
  (3) AMPLITUDE LADDER: multiple amplitudes per class give independent steady-
      state constraints on the small weights (more equations than unknowns).
  (4) PER-NEURON CONDITION SELECTION: for each neuron j with support supp_j,
      pick the class whose presynaptic set most overlaps supp_j and weight that
      class's data heavily. Other-class data is suppressed (avoids contamination).

Output: pass criterion is div_tap < 0.05 AND div_chem < 0.05 on a unified W.
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
print("SCAN INVERSE v2 -- sustained probes, per-class isolation, ss sampling")
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
support = (W_TRUE > 0)
nz_mask = (W_TRUE.flatten() > 1e-6)

# Behavior class sensors
classes = {
    "tap":  {"ALML", "ALMR", "AVM", "PLML", "PLMR", "PVM"},
    "chem": {"AWCL", "AWCR", "ASEL", "ASER"},
    # extra "broadcast" class: hit all sensory neurons to give 2-hop neurons coverage
    "amph": {"AWAL", "AWAR", "AWBL", "AWBR", "ASGL", "ASGR", "ASIL", "ASIR",
             "ASJL", "ASJR", "ASKL", "ASKR", "ADFL", "ADFR", "ADLL", "ADLR"},
}
class_idx = {c: [i for i, n in enumerate(neurons) if n in s] for c, s in classes.items()}
for c, idx in class_idx.items():
    print(f"  class {c}: {len(idx)} sensor neurons")

# -----------------------------------------------------------------------------
# Sustained tonic probes: step input, settle to steady state
# -----------------------------------------------------------------------------
params_v2 = params  # same params; we just use a different stimulus protocol
T_PROBE_ms = 400.0  # enough for tau=10ms dynamics to settle (~40 tau)
T_probe = int(T_PROBE_ms / params.dt)
SS_WINDOW = (int(200.0 / params.dt), int(380.0 / params.dt))  # take samples in steady-state window
SUB_SS   = 5    # subsample within ss window
EPS      = 0.001

# Amplitude ladder per class
AMPS = [0.3, 0.6, 1.0, 1.5, 2.5]

def tonic_input(target_idx, amplitude):
    I = np.zeros((T_probe, N))
    I[:, target_idx] = amplitude
    return I

# Build conditions: (class_name, amplitude, I)
stimuli = []
cmeta   = []
for cls, idx_c in class_idx.items():
    for amp in AMPS:
        stimuli.append(tonic_input(idx_c, amp))
        cmeta.append((cls, amp))
K_TOTAL = len(stimuli)
print(f"\nK_total = {K_TOTAL} sustained tonic conditions "
      f"({len(classes)} classes x {len(AMPS)} amplitudes)")

# -----------------------------------------------------------------------------
# Simulate, sample steady state, compute linearized targets z
# -----------------------------------------------------------------------------
ratio = params.tau / params.dt
print("Simulating...")
cond = []
for k, I_k in enumerate(stimuli):
    R = simulate_rate(W_norm, G_norm, I_k, T_PROBE_ms, params)["r"]
    # sample steady-state window
    t_idx = np.arange(SS_WINDOW[0], SS_WINDOW[1], SUB_SS)
    X_k  = R[t_idx].astype(np.float64)
    # next-step sample for derivative
    t_idx_p1 = np.minimum(t_idx + 1, T_probe - 1)
    Xp_k = R[t_idx_p1].astype(np.float64)
    Ie_k = I_k[t_idx].astype(np.float64)

    valid = Xp_k > EPS
    targ  = (Xp_k - X_k) * ratio + X_k
    valid &= (targ > -0.9999) & (targ < 0.9999)
    I_gap = X_k @ G.T - X_k * G_rowsum[np.newaxis, :]
    z = np.arctanh(np.clip(targ, -0.9999, 0.9999)) / params.gain - I_gap - Ie_k
    cond.append(dict(X=X_k, z=z, valid=valid, fv=valid.mean(axis=0),
                     ract=X_k.mean(axis=0)))

# -----------------------------------------------------------------------------
# Test stimuli (same as v1)
# -----------------------------------------------------------------------------
ws, we = int(100/params.dt), int(500/params.dt)
T_test = 600.0
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
    pr = pearsonr(W_TRUE.flatten()[nz_mask], W_hat.flatten()[nz_mask])[0]
    return dict(frob=np.linalg.norm(W_hat - W_TRUE)/np.linalg.norm(W_TRUE),
                pearson=pr,
                div_tap=cdiv(r_tap_orig, r_tap),
                div_chem=cdiv(r_chem_orig, r_chem))

# -----------------------------------------------------------------------------
# Approach G: support-aware combined ridge on tonic SS data
# Just to baseline against v1 D (which used pulsed data).
# -----------------------------------------------------------------------------
X_all = np.concatenate([c["X"] for c in cond], axis=0)
z_all = np.concatenate([c["z"] for c in cond], axis=0)
v_all = np.concatenate([c["valid"] for c in cond], axis=0)

print("\n[Approach G] Support-aware combined (tonic SS data)")
W_G = np.zeros((N, N))
for j in range(N):
    supp_j = np.where(support[:, j])[0]
    if len(supp_j) == 0:
        continue
    valid_j = v_all[:, j]
    X_sub = X_all[valid_j][:, supp_j]
    z_sub = z_all[valid_j, j]
    A = X_sub.T @ X_sub + 1e-3 * np.eye(len(supp_j))
    b = X_sub.T @ z_sub
    W_G[supp_j, j] = np.clip(np.linalg.solve(A, b), 0, None)
r_G = evaluate(W_G)
print(f"  frob={r_G['frob']:.4f}  r={r_G['pearson']:.4f}  "
      f"div_tap={r_G['div_tap']:.4f}  div_chem={r_G['div_chem']:.4f}")

# -----------------------------------------------------------------------------
# Approach H: per-neuron CLASS SELECTION on tonic SS data
# For each neuron j, find which class's sensors best activate j's presynaptic
# inputs (supp_j). Use ONLY that class's amplitude ladder for the fit.
# -----------------------------------------------------------------------------
print("\n[Approach H] Per-neuron class selection (tonic SS)")
# class -> list of condition indices
class_conds = {cls: [k for k, (c, _) in enumerate(cmeta) if c == cls]
               for cls in classes}

# Compute, for each class c, the activation pattern (per-neuron mean activity)
# across that class's amplitude ladder. We score class c for neuron j by:
# mean over class-c conditions of <var of presynaptic supp_j inputs>.
class_act = {}
for cls, ks in class_conds.items():
    # mean across conditions of per-neuron variance (proxy for how much that
    # condition drives each neuron with informative signal)
    var_per_neuron = np.mean([cond[k]["X"].var(axis=0) for k in ks], axis=0)
    class_act[cls] = var_per_neuron  # (N,)

W_H = np.zeros((N, N))
class_choice = np.empty(N, dtype=object)
for j in range(N):
    supp_j = np.where(support[:, j])[0]
    if len(supp_j) == 0:
        class_choice[j] = "none"
        continue
    # score each class by total informative variance over supp_j
    cls_scores = {cls: class_act[cls][supp_j].sum() for cls in classes}
    best_cls = max(cls_scores, key=cls_scores.get)
    class_choice[j] = best_cls
    ks = class_conds[best_cls]
    # Stack data from chosen class only
    X_stack = np.concatenate([cond[k]["X"] for k in ks], axis=0)
    z_stack = np.concatenate([cond[k]["z"] for k in ks], axis=0)
    v_stack = np.concatenate([cond[k]["valid"] for k in ks], axis=0)
    valid_j = v_stack[:, j]
    if valid_j.sum() < len(supp_j) + 5:
        # fall back to all data
        valid_j = v_all[:, j]
        X_sub = X_all[valid_j][:, supp_j]
        z_sub = z_all[valid_j, j]
    else:
        X_sub = X_stack[valid_j][:, supp_j]
        z_sub = z_stack[valid_j, j]
    A = X_sub.T @ X_sub + 1e-3 * np.eye(len(supp_j))
    b = X_sub.T @ z_sub
    W_H[supp_j, j] = np.clip(np.linalg.solve(A, b), 0, None)
r_H = evaluate(W_H)
print(f"  frob={r_H['frob']:.4f}  r={r_H['pearson']:.4f}  "
      f"div_tap={r_H['div_tap']:.4f}  div_chem={r_H['div_chem']:.4f}")
# how many neurons got assigned per class?
from collections import Counter
ccount = Counter(class_choice)
print(f"  class assignments: {dict(ccount)}")

# -----------------------------------------------------------------------------
# Approach I: AS H, plus relative-error rescaling (small-weight friendly)
# For each neuron j, rescale columns of X by the typical magnitude of W_TRUE
# on supp_j... but we don't know W_TRUE. Use a 2-pass scheme:
#   pass 1: estimate W_hat_j from H
#   pass 2: rescale X by max(W_hat_j, eps) so that small weights get more
#           "voltage" per unit of residual penalty
# This is equivalent to a per-coordinate ridge with lambda_k = lambda/W_hat_jk^2
# -----------------------------------------------------------------------------
print("\n[Approach I] H + small-weight friendly rescaling (2-pass)")
W_I = np.zeros((N, N))
for j in range(N):
    supp_j = np.where(support[:, j])[0]
    if len(supp_j) == 0:
        continue
    # pass-1 estimate from H
    w0 = W_H[supp_j, j]
    if w0.sum() < 1e-10:
        W_I[supp_j, j] = w0
        continue
    best_cls = class_choice[j]
    ks = class_conds.get(best_cls, [])
    if not ks:
        W_I[supp_j, j] = w0
        continue
    X_stack = np.concatenate([cond[k]["X"] for k in ks], axis=0)
    z_stack = np.concatenate([cond[k]["z"] for k in ks], axis=0)
    v_stack = np.concatenate([cond[k]["valid"] for k in ks], axis=0)
    valid_j = v_stack[:, j]
    if valid_j.sum() < len(supp_j) + 5:
        W_I[supp_j, j] = w0
        continue
    X_sub = X_stack[valid_j][:, supp_j]
    z_sub = z_stack[valid_j, j]
    # per-coordinate ridge: smaller penalty on coordinates that have small w0
    # i.e. trust the data more for small-weight inputs (let them grow if data supports)
    scale = np.maximum(w0, 0.005)  # floor to avoid blowup at zero
    D = np.diag(1.0 / scale)
    X_resc = X_sub @ D  # column-scaled
    A = X_resc.T @ X_resc + 1e-4 * np.eye(len(supp_j))
    b = X_resc.T @ z_sub
    w_resc = np.linalg.solve(A, b)
    w_j = w_resc / scale  # un-rescale
    W_I[supp_j, j] = np.clip(w_j, 0, None)
r_I = evaluate(W_I)
print(f"  frob={r_I['frob']:.4f}  r={r_I['pearson']:.4f}  "
      f"div_tap={r_I['div_tap']:.4f}  div_chem={r_I['div_chem']:.4f}")

# -----------------------------------------------------------------------------
# Diagnostic: focus on tap-circuit neurons specifically
# -----------------------------------------------------------------------------
print("\n--- TAP CIRCUIT diagnostic ---")
tap_sensor_idx = class_idx["tap"]
# tap-postsynaptic neurons: those with any nonzero tap presynaptic input
tap_post = np.where(support[tap_sensor_idx, :].any(axis=0))[0]
print(f"  tap sensors: {len(tap_sensor_idx)};  tap-postsynaptic neurons: {len(tap_post)}")

def tap_weight_stats(W_hat, label):
    # restrict to weights from tap sensors to tap-postsynaptic neurons that are
    # genuinely nonzero in W_TRUE
    rel_errs = []
    for j in tap_post:
        for i in tap_sensor_idx:
            if W_TRUE[i, j] > 1e-6:
                err = abs(W_hat[i, j] - W_TRUE[i, j]) / W_TRUE[i, j]
                rel_errs.append(err)
    rel = np.array(rel_errs) if rel_errs else np.array([np.nan])
    print(f"  {label:18s} tap-presyn rel-err: "
          f"median={np.median(rel):.3f}  mean={np.mean(rel):.3f}  n={len(rel)}")

tap_weight_stats(W_G, "G (support+all)")
tap_weight_stats(W_H, "H (per-class)")
tap_weight_stats(W_I, "I (H + rescale)")

# -----------------------------------------------------------------------------
# Summary + plot
# -----------------------------------------------------------------------------
def pass_str(r): return "PASS" if (r["div_tap"]<0.05 and r["div_chem"]<0.05) else "FAIL"
print("\n" + "=" * 72)
print("SUMMARY (v2)")
print("=" * 72)
rows = [("G support+all-tonic", r_G),
        ("H per-class tonic",   r_H),
        ("I H + rel-err rescale", r_I)]
for name, r in rows:
    print(f"{name:<25} frob={r['frob']:.4f}  r={r['pearson']:.4f}  "
          f"div_tap={r['div_tap']:.4f}  div_chem={r['div_chem']:.4f}  {pass_str(r)}")

# Best
best_name, best_r = min(rows, key=lambda x: x[1]["div_tap"]+x[1]["div_chem"])
print(f"\nBest: {best_name}")

# Save
with open("simulation/results/scan_inverse_v2_summary.txt", "w", encoding="utf-8") as f:
    f.write("Scan Inverse v2 -- tonic SS probes, per-class isolation\n")
    f.write("=" * 60 + "\n")
    f.write(f"K_total = {K_TOTAL} ({len(classes)} classes x {len(AMPS)} amps)\n\n")
    for name, r in rows:
        f.write(f"{name:<25} frob={r['frob']:.4f}  r={r['pearson']:.4f}  "
                f"div_tap={r['div_tap']:.4f}  div_chem={r['div_chem']:.4f}  {pass_str(r)}\n")
    f.write(f"\nBest: {best_name}\n")

np.savez("simulation/results/scan_inverse_v2.npz",
         W_TRUE=W_TRUE, W_G=W_G, W_H=W_H, W_I=W_I,
         r_G=r_G, r_H=r_H, r_I=r_I)
print("Saved: simulation/results/scan_inverse_v2_summary.txt + .npz")
