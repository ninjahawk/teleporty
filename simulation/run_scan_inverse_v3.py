"""
Scan inverse problem v3 -- per-neuron optogenetic perturbation.

v2 finding: tonic SS probes work at zero noise but
  (a) fail on held-out classes (thermo), because only tap+chem+amph were probed
  (b) collapse at noise >= 0.005 because arctanh near saturation amplifies noise.

v3 protocol (biologically realizable with cell-specific channelrhodopsin):
  Stimulate each neuron individually at MODERATE amplitude. Record steady-state
  population response. With N=302 conditions and ~12 unknowns per support, the
  per-neuron fit is massively over-determined.

  To tame arctanh noise:
    * use MODERATE amplitudes (0.4-0.8) that keep rates well below saturation
    * filter samples where any postsyn rate exceeds 0.85 or drops below 0.02
    * average across the SS-window timesteps to reduce stochastic measurement noise
"""
import os, sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from simulation.load_connectome import load_connectome, load_gap_junctions
from simulation.rate_model import RateParams, simulate_rate, make_tap_input, make_chem_input

os.makedirs("simulation/results", exist_ok=True)
print("=" * 72)
print("SCAN INVERSE v3 -- per-neuron perturbation, noise-robust")
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

# -------------------- Probe protocol --------------------
T_PROBE_ms = 300.0
T_probe = int(T_PROBE_ms / params.dt)
SS_WINDOW = (int(150.0/params.dt), int(280.0/params.dt))
SUB_SS = 2  # finely sample to enable averaging
EPS = 0.001
SAT_HI = 0.85
SAT_LO = 0.02
AMPS_PER_NEURON = [0.4, 0.8]   # 2 amplitudes per neuron
ratio = params.tau / params.dt

def build_data(noise_level, seed):
    rng = np.random.default_rng(seed)
    # per-neuron stimulation: N neurons * len(AMPS_PER_NEURON) conditions
    obs_X, obs_Xp, obs_Ie = [], [], []
    for i in range(N):
        for amp in AMPS_PER_NEURON:
            I_k = np.zeros((T_probe, N))
            I_k[:, i] = amp
            R = simulate_rate(W_norm, G_norm, I_k, T_PROBE_ms, params)["r"]
            if noise_level > 0:
                R = R + rng.normal(0, noise_level, R.shape)
                R = np.clip(R, 0, 1)
            # average across SS window to reduce noise (single sample per condition)
            ss_slice = R[SS_WINDOW[0]:SS_WINDOW[1]]
            ss_mean = ss_slice.mean(axis=0)            # (N,) -- one X per condition
            # use one-step-forward sample for derivative as well
            R_fwd = R[SS_WINDOW[0]+1 : SS_WINDOW[1]+1]
            ss_fwd = R_fwd.mean(axis=0) if R_fwd.size else ss_mean
            obs_X.append(ss_mean)
            obs_Xp.append(ss_fwd)
            obs_Ie.append(I_k[SS_WINDOW[0]])           # constant during SS
    X = np.array(obs_X)       # (K, N)
    Xp = np.array(obs_Xp)
    Ie = np.array(obs_Ie)
    return X, Xp, Ie

def fit_W(X, Xp, Ie):
    # linearization target z_j = arctanh((Xp-X)*ratio + X)/gain - I_gap - I_ext
    valid = Xp > EPS
    targ = (Xp - X) * ratio + X
    valid &= (targ > -0.9999) & (targ < 0.9999)
    # saturation filter on the SOURCE state X (X drives the regression)
    # we don't want X near 1 since arctanh blows up
    valid &= (X < SAT_HI) & (X > SAT_LO) | (X == 0)  # 0 is fine; ~saturation is not
    I_gap = X @ G.T - X * G_rowsum[np.newaxis, :]
    z = np.arctanh(np.clip(targ, -0.9999, 0.9999))/params.gain - I_gap - Ie

    W_hat = np.zeros((N, N))
    for j in range(N):
        supp_j = np.where(support[:, j])[0]
        if len(supp_j) == 0: continue
        vj = valid[:, j]
        if vj.sum() < len(supp_j) + 3:
            # not enough usable rows for this neuron; skip
            continue
        X_sub = X[vj][:, supp_j]
        z_sub = z[vj, j]
        # near-saturation filter on the regressor columns: if any column entry > SAT_HI, drop that row
        row_ok = (X_sub < SAT_HI).all(axis=1)
        X_sub, z_sub = X_sub[row_ok], z_sub[row_ok]
        if X_sub.shape[0] < len(supp_j) + 3: continue
        A = X_sub.T @ X_sub + 1e-3 * np.eye(len(supp_j))
        b = X_sub.T @ z_sub
        W_hat[supp_j, j] = np.clip(np.linalg.solve(A, b), 0, None)
    return W_hat

# -------------------- Evaluation harness --------------------
ws, we = int(100/params.dt), int(500/params.dt)
T_test = 600.0
def cdiv(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 1.0 - np.dot(a,b)/(na*nb) if na>1e-10 and nb>1e-10 else 1.0

test_stims = {}
for amp, name in [(4.0, "tap_a4"), (2.0, "tap_a2")]:
    I = make_tap_input(N, neurons, T_test, params.dt, onset_ms=50.0, duration_ms=30.0, amplitude=amp)
    r0 = simulate_rate(W_norm, G_norm, I, T_test, params)["r"][ws:we].flatten()
    test_stims[name] = (I, r0)
for amp, name in [(3.0, "chem_a3"), (1.5, "chem_a1.5")]:
    I = make_chem_input(N, neurons, T_test, params.dt, amplitude=amp)
    r0 = simulate_rate(W_norm, G_norm, I, T_test, params)["r"][ws:we].flatten()
    test_stims[name] = (I, r0)
# thermo
thermo = {"AFDL","AFDR","ASJL","ASJR"}
T_thermo = np.zeros((int(T_test/params.dt), N))
for i, n in enumerate(neurons):
    if n in thermo: T_thermo[:, i] = 2.0
r0 = simulate_rate(W_norm, G_norm, T_thermo, T_test, params)["r"][ws:we].flatten()
test_stims["thermo"] = (T_thermo, r0)
# nociception (ASHL, ASHR)
T_noc = np.zeros((int(T_test/params.dt), N))
for i, n in enumerate(neurons):
    if n in {"ASHL","ASHR"}: T_noc[:, i] = 2.5
r0 = simulate_rate(W_norm, G_norm, T_noc, T_test, params)["r"][ws:we].flatten()
test_stims["nociception"] = (T_noc, r0)

def evaluate(W_hat):
    Wh_norm = np.clip(W_hat/params.w_chem, 0, None)
    pr = pearsonr(W_TRUE.flatten()[nz_mask], W_hat.flatten()[nz_mask])[0]
    out = {"pearson": pr,
           "frob": np.linalg.norm(W_hat - W_TRUE)/np.linalg.norm(W_TRUE)}
    for name, (I_test, r_orig) in test_stims.items():
        r_hat = simulate_rate(Wh_norm, G_norm, I_test, T_test, params)["r"][ws:we].flatten()
        out["div_"+name] = cdiv(r_orig, r_hat)
    return out

# -------------------- Run --------------------
NOISE_LEVELS = [0.0, 0.005, 0.01, 0.02, 0.05]
SEEDS = [11, 42, 777]
print(f"Per-neuron probes: N={N} neurons x {len(AMPS_PER_NEURON)} amps = {N*len(AMPS_PER_NEURON)} conditions")
print(f"Running {len(NOISE_LEVELS)} noise levels x {len(SEEDS)} seeds...\n")

div_keys = ["tap_a4", "tap_a2", "chem_a3", "chem_a1.5", "thermo", "nociception"]
print(f"noise   seed  | " + "  ".join(f"{k[:10]:>10}" for k in div_keys) + f"  | pearson  verdict")
print("-" * 110)
all_rows = []
results_pass = {nl: 0 for nl in NOISE_LEVELS}
for nl in NOISE_LEVELS:
    for sd in SEEDS:
        X, Xp, Ie = build_data(nl, sd)
        W_hat = fit_W(X, Xp, Ie)
        m = evaluate(W_hat)
        passed = all(m["div_"+k] < 0.05 for k in div_keys)
        results_pass[nl] += int(passed)
        divs_str = "  ".join(f"{m['div_'+k]:>10.4f}" for k in div_keys)
        verdict = "PASS" if passed else "FAIL"
        line = f"{nl:>5.3f}  {sd:>4} | {divs_str}  | {m['pearson']:>7.3f}  {verdict}"
        print(line); all_rows.append(line)

print()
print("Pass rate by noise level:")
for nl in NOISE_LEVELS:
    print(f"  noise={nl:.3f}:  {results_pass[nl]}/{len(SEEDS)}")

# Save
with open("simulation/results/scan_inverse_v3_summary.txt", "w", encoding="utf-8") as f:
    f.write("Scan inverse v3 -- per-neuron probes, noise-robust\n")
    f.write(f"Conditions: N={N} neurons x {len(AMPS_PER_NEURON)} amps = {N*len(AMPS_PER_NEURON)}\n\n")
    f.write(f"noise   seed  | " + "  ".join(f"{k[:10]:>10}" for k in div_keys) + f"  | pearson  verdict\n")
    f.write("-" * 110 + "\n")
    f.write("\n".join(all_rows) + "\n\n")
    f.write("Pass rate by noise level:\n")
    for nl in NOISE_LEVELS:
        f.write(f"  noise={nl:.3f}:  {results_pass[nl]}/{len(SEEDS)}\n")
print("\nSaved: simulation/results/scan_inverse_v3_summary.txt")
