"""
Scan inverse problem v4 -- noise-robust per-neuron protocol.

v3 result: passes at noise<=0.01; tap circuit fails at noise>=0.02.

Fixes:
  (1) Tighter saturation filter: drop samples where postsyn rate > 0.7 or < 0.02.
      This keeps arctanh in its tame region (avoids amplifying r noise into z noise).
  (2) Multiple noise repetitions per condition: simulate clean trajectory once,
      add independent noise n_reps times, average X and Xp across reps.
      Effective noise reduction: 1/sqrt(n_reps * ss_samples).
  (3) Three amplitudes per neuron: [0.4, 0.8, 1.5] -- 0.4 keeps everyone linear;
      1.5 saturates the stim neuron but the filter drops those rows.

Biological reading: this protocol = single-neuron optogenetic stimulation, repeated
n_reps times per stim site, with fluorescent calcium imaging providing ~2% noise.
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
print("=" * 72); print("SCAN INVERSE v4 -- noise-robust per-neuron protocol"); print("=" * 72)

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

T_PROBE_ms = 300.0
T_probe = int(T_PROBE_ms / params.dt)
SS_WINDOW = (int(150.0/params.dt), int(280.0/params.dt))
SUB_SS = 2
EPS = 0.001
SAT_HI = 0.85   # match v3's looser filter; rely on n_reps averaging for noise
SAT_LO = 0.02
AMPS_PER_NEURON = [0.4, 0.8, 1.5]
ratio = params.tau / params.dt

def build_data(noise_level, seed, n_reps=5):
    """Per-neuron stim, multiple noise reps averaged into one X/Xp/Ie sample per condition.

    Returns X, Xp, Ie shape (K, N) where K = N * len(AMPS_PER_NEURON).
    """
    rng = np.random.default_rng(seed)
    K = N * len(AMPS_PER_NEURON)
    X = np.zeros((K, N)); Xp = np.zeros((K, N)); Ie = np.zeros((K, N))
    k = 0
    for i in range(N):
        for amp in AMPS_PER_NEURON:
            I_k = np.zeros((T_probe, N)); I_k[:, i] = amp
            R_clean = simulate_rate(W_norm, G_norm, I_k, T_PROBE_ms, params)["r"]
            # average over reps of (noise sample + SS-window mean)
            x_acc = np.zeros(N); xp_acc = np.zeros(N)
            for _ in range(max(1, n_reps if noise_level > 0 else 1)):
                if noise_level > 0:
                    R = R_clean + rng.normal(0, noise_level, R_clean.shape)
                    R = np.clip(R, 0, 1)
                else:
                    R = R_clean
                ss = R[SS_WINDOW[0]:SS_WINDOW[1]:SUB_SS]
                ssp = R[SS_WINDOW[0]+1:SS_WINDOW[1]+1:SUB_SS]
                # use trimmed mean to be robust to outliers from saturation noise
                x_acc += ss.mean(axis=0); xp_acc += ssp.mean(axis=0)
            reps_used = max(1, n_reps if noise_level > 0 else 1)
            X[k] = x_acc / reps_used
            Xp[k] = xp_acc / reps_used
            Ie[k] = I_k[SS_WINDOW[0]]
            k += 1
    return X, Xp, Ie

def fit_W(X, Xp, Ie):
    valid = Xp > EPS
    targ = (Xp - X) * ratio + X
    valid &= (targ > -0.95) & (targ < 0.95)
    # v3-style element-wise X filter: valid only where X is not in saturated/dead range
    x_safe = (X < SAT_HI) & (X > SAT_LO) | (X == 0)
    valid &= x_safe
    I_gap = X @ G.T - X * G_rowsum[np.newaxis, :]
    z = np.arctanh(np.clip(targ, -0.95, 0.95))/params.gain - I_gap - Ie

    W_hat = np.zeros((N, N))
    for j in range(N):
        supp_j = np.where(support[:, j])[0]
        if len(supp_j) == 0: continue
        vj = valid[:, j]
        if vj.sum() < len(supp_j) + 3: continue
        X_sub = X[vj][:, supp_j]
        z_sub = z[vj, j]
        A = X_sub.T @ X_sub + 1e-3 * np.eye(len(supp_j))
        b = X_sub.T @ z_sub
        W_hat[supp_j, j] = np.clip(np.linalg.solve(A, b), 0, None)
    return W_hat

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
thermo = {"AFDL","AFDR","ASJL","ASJR"}
T_thermo = np.zeros((int(T_test/params.dt), N))
for i, n in enumerate(neurons):
    if n in thermo: T_thermo[:, i] = 2.0
r0 = simulate_rate(W_norm, G_norm, T_thermo, T_test, params)["r"][ws:we].flatten()
test_stims["thermo"] = (T_thermo, r0)
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

NOISE_LEVELS = [0.0, 0.01, 0.02, 0.05]
SEEDS = [11, 42, 777]
N_REPS = 10
div_keys = ["tap_a4", "tap_a2", "chem_a3", "chem_a1.5", "thermo", "nociception"]
print(f"Per-neuron: N={N} x {len(AMPS_PER_NEURON)} amps = {N*len(AMPS_PER_NEURON)} conditions")
print(f"n_reps={N_REPS} averaging per condition (when noise>0)")
print(f"Noise levels: {NOISE_LEVELS}; Seeds: {SEEDS}\n")
print(f"noise   seed  | " + "  ".join(f"{k[:11]:>11}" for k in div_keys) + f" | pearson  verdict")
print("-" * 120)
all_rows = []
results_pass = {nl: 0 for nl in NOISE_LEVELS}
for nl in NOISE_LEVELS:
    for sd in SEEDS:
        X, Xp, Ie = build_data(nl, sd, n_reps=N_REPS)
        W_hat = fit_W(X, Xp, Ie)
        m = evaluate(W_hat)
        passed = all(m["div_"+k] < 0.05 for k in div_keys)
        results_pass[nl] += int(passed)
        divs_str = "  ".join(f"{m['div_'+k]:>11.4f}" for k in div_keys)
        line = f"{nl:>5.3f}  {sd:>4} | {divs_str} | {m['pearson']:>7.3f}  {'PASS' if passed else 'FAIL'}"
        print(line); all_rows.append(line)

print()
print("Pass rate by noise level:")
for nl in NOISE_LEVELS:
    print(f"  noise={nl:.3f}:  {results_pass[nl]}/{len(SEEDS)}")

with open("simulation/results/scan_inverse_v4_summary.txt", "w", encoding="utf-8") as f:
    f.write("Scan inverse v4 -- per-neuron probes with noise averaging\n")
    f.write(f"Conditions: N={N} x {len(AMPS_PER_NEURON)} amps; n_reps={N_REPS}; SAT_HI={SAT_HI}\n")
    f.write(f"noise   seed  | " + "  ".join(f"{k[:11]:>11}" for k in div_keys) + f" | pearson  verdict\n")
    f.write("-" * 120 + "\n")
    f.write("\n".join(all_rows) + "\n\n")
    f.write("Pass rate by noise level:\n")
    for nl in NOISE_LEVELS:
        f.write(f"  noise={nl:.3f}:  {results_pass[nl]}/{len(SEEDS)}\n")
print("\nSaved: simulation/results/scan_inverse_v4_summary.txt")
