"""
Robustness check for scan_inverse v2 finding:
  Tonic SS probes + support-aware combined ridge passed at div_tap=0.003,
  div_chem<0.001 in a single run.

We need to confirm this is not an artifact of:
  (a) the specific test stimulus (test only one amplitude / one onset)
  (b) zero measurement noise (synthetic recordings are clean)
  (c) zero seed variability (only one run)

This script:
  - Runs the v2 pipeline across SEEDS x NOISE_LEVELS
  - Tests reconstruction quality on multiple test stimuli (tap onsets, chem onsets,
    plus a held-out "thermo" stimulus)
  - Reports pass rate
"""
import os, sys, numpy as np
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from simulation.load_connectome import load_connectome, load_gap_junctions
from simulation.rate_model import RateParams, simulate_rate, make_tap_input, make_chem_input
from scipy.stats import pearsonr

print("=" * 72)
print("SCAN INVERSE v2 -- ROBUSTNESS CHECK")
print("=" * 72)

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

classes = {
    "tap":  {"ALML", "ALMR", "AVM", "PLML", "PLMR", "PVM"},
    "chem": {"AWCL", "AWCR", "ASEL", "ASER"},
    "amph": {"AWAL", "AWAR", "AWBL", "AWBR", "ASGL", "ASGR", "ASIL", "ASIR",
             "ASJL", "ASJR", "ASKL", "ASKR", "ADFL", "ADFR", "ADLL", "ADLR"},
}
class_idx = {c: [i for i, n in enumerate(neurons) if n in s] for c, s in classes.items()}

AMPS = [0.3, 0.6, 1.0, 1.5, 2.5]
T_PROBE_ms = 400.0
T_probe = int(T_PROBE_ms / params.dt)
SS_WINDOW = (int(200.0/params.dt), int(380.0/params.dt))
SUB_SS = 5
EPS = 0.001
ratio = params.tau / params.dt

def tonic_input(target_idx, amplitude):
    I = np.zeros((T_probe, N)); I[:, target_idx] = amplitude; return I

def run_recovery(noise_level, seed):
    rng = np.random.default_rng(seed)
    stimuli, cmeta = [], []
    for cls, idx_c in class_idx.items():
        for amp in AMPS:
            stimuli.append(tonic_input(idx_c, amp)); cmeta.append((cls, amp))
    K = len(stimuli)
    cond = []
    for I_k in stimuli:
        R = simulate_rate(W_norm, G_norm, I_k, T_PROBE_ms, params)["r"]
        # ADD MEASUREMENT NOISE to observed activity
        if noise_level > 0:
            R = R + rng.normal(0, noise_level, R.shape)
            R = np.clip(R, 0, 1)
        t_idx = np.arange(SS_WINDOW[0], SS_WINDOW[1], SUB_SS)
        X = R[t_idx].astype(np.float64)
        Xp = R[np.minimum(t_idx+1, T_probe-1)].astype(np.float64)
        Ie = I_k[t_idx].astype(np.float64)
        valid = Xp > EPS
        targ = (Xp - X) * ratio + X
        valid &= (targ > -0.9999) & (targ < 0.9999)
        I_gap = X @ G.T - X * G_rowsum[np.newaxis, :]
        z = np.arctanh(np.clip(targ, -0.9999, 0.9999))/params.gain - I_gap - Ie
        cond.append((X, z, valid))

    X_all = np.concatenate([c[0] for c in cond], axis=0)
    z_all = np.concatenate([c[1] for c in cond], axis=0)
    v_all = np.concatenate([c[2] for c in cond], axis=0)

    W_hat = np.zeros((N, N))
    for j in range(N):
        supp_j = np.where(support[:, j])[0]
        if len(supp_j) == 0: continue
        vj = v_all[:, j]
        X_sub = X_all[vj][:, supp_j]
        z_sub = z_all[vj, j]
        A = X_sub.T @ X_sub + 1e-3 * np.eye(len(supp_j))
        b = X_sub.T @ z_sub
        W_hat[supp_j, j] = np.clip(np.linalg.solve(A, b), 0, None)
    return W_hat

ws, we = int(100/params.dt), int(500/params.dt)
T_test = 600.0
def cdiv(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 1.0 - np.dot(a,b)/(na*nb) if na>1e-10 and nb>1e-10 else 1.0

def evaluate(W_hat, test_stims):
    Wh_norm = np.clip(W_hat/params.w_chem, 0, None)
    out = {}
    for name, (I_test, r_orig) in test_stims.items():
        r_hat = simulate_rate(Wh_norm, G_norm, I_test, T_test, params)["r"][ws:we].flatten()
        out["div_"+name] = cdiv(r_orig, r_hat)
    return out

# build test stimuli set
test_stims = {}
# tap at two amplitudes, two onsets
for amp, name in [(4.0, "tap_a4"), (2.0, "tap_a2")]:
    I = make_tap_input(N, neurons, T_test, params.dt, onset_ms=50.0, duration_ms=30.0, amplitude=amp)
    r0 = simulate_rate(W_norm, G_norm, I, T_test, params)["r"][ws:we].flatten()
    test_stims[name] = (I, r0)
for amp, name in [(3.0, "chem_a3"), (1.5, "chem_a1.5")]:
    I = make_chem_input(N, neurons, T_test, params.dt, amplitude=amp)
    r0 = simulate_rate(W_norm, G_norm, I, T_test, params)["r"][ws:we].flatten()
    test_stims[name] = (I, r0)
# held-out: thermosensory ASJ stimulation
thermo = {"AFDL","AFDR","ASJL","ASJR"}
T_thermo = np.zeros((int(T_test/params.dt), N))
for i, n in enumerate(neurons):
    if n in thermo: T_thermo[:, i] = 2.0
r0 = simulate_rate(W_norm, G_norm, T_thermo, T_test, params)["r"][ws:we].flatten()
test_stims["thermo"] = (T_thermo, r0)

print(f"\nTest stimuli: {list(test_stims.keys())}")

# Run across seeds and noise levels
SEEDS = [11, 23, 42, 101, 777]
NOISE_LEVELS = [0.0, 0.005, 0.01, 0.02, 0.05]
print(f"Running {len(SEEDS)} seeds x {len(NOISE_LEVELS)} noise levels...")
results = {}
for nl in NOISE_LEVELS:
    row = []
    for sd in SEEDS:
        W_hat = run_recovery(nl, sd)
        m = evaluate(W_hat, test_stims)
        row.append(m)
    results[nl] = row

# Report
print("\n" + "=" * 72)
print("RESULTS  (divergence; PASS = all stimuli < 0.05)")
print("=" * 72)
keys = list(test_stims.keys())
header = "noise     | " + " | ".join(f"{k:>10}" for k in keys) + " | passrate"
print(header)
print("-" * len(header))
import statistics
all_lines = [header, "-" * len(header)]
for nl in NOISE_LEVELS:
    medians = {k: statistics.median([r["div_"+k] for r in results[nl]]) for k in keys}
    pass_rate = sum(all(r["div_"+k] < 0.05 for k in keys) for r in results[nl]) / len(SEEDS)
    line = f"{nl:<9.3f} | " + " | ".join(f"{medians[k]:>10.4f}" for k in keys) + f" |  {pass_rate*100:.0f}%"
    print(line); all_lines.append(line)

with open("simulation/results/scan_inverse_v2_robustness.txt", "w", encoding="utf-8") as f:
    f.write("Scan inverse v2 -- robustness (medians across seeds)\n")
    f.write(f"Seeds: {SEEDS}\nNoise levels: {NOISE_LEVELS}\n\n")
    f.write("\n".join(all_lines) + "\n")
print("\nSaved: simulation/results/scan_inverse_v2_robustness.txt")
