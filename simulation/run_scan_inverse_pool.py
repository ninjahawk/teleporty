"""
Pool-based scan inverse -- toward human-scale recovery.

v4 protocol: stimulate each of N neurons individually -> O(N) trials.
For C. elegans this is 900 trials; for human (N=8.6e10) it's 2.6e12 trials,
not serially feasible.

This script tests random-POOL stimulation: each trial stimulates a random
subset of M neurons simultaneously, K total trials. Recovery uses the same
support-aware ridge regression. Question: at what (K, M) does pool stim
match per-neuron quality?

If K << N succeeds, then for the human scanner each "pool" maps to a
cell-type or anatomical subregion of optogenetic addressing, and human-scale
scanning becomes practical (~10^4-10^5 trials instead of 10^12).
"""
import os, sys, numpy as np
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from simulation.load_connectome import load_connectome, load_gap_junctions
from simulation.rate_model import RateParams, simulate_rate, make_tap_input, make_chem_input
from scipy.stats import pearsonr

print("="*72); print("POOL SCAN INVERSE -- toward human-scale recovery"); print("="*72)

W_raw, neurons, W_norm = load_connectome()
G_raw, g_neurons = load_gap_junctions()
N = len(neurons)
g_idx = {n:i for i,n in enumerate(g_neurons)}; g_set = set(g_neurons)
G_aligned = np.zeros((N, N))
for i, ni in enumerate(neurons):
    for j, nj in enumerate(neurons):
        if ni in g_set and nj in g_set:
            G_aligned[i,j] = G_raw[g_idx[ni], g_idx[nj]]
G_norm = G_aligned/(G_aligned.max() or 1.0)

params = RateParams(tau=10.0, gain=2.5, w_chem=0.25, w_gap=0.1, dt=0.5)
W_TRUE = W_norm*params.w_chem; G = G_norm*params.w_gap
G_rowsum = G.sum(axis=1); support = (W_TRUE>0); nz_mask = W_TRUE.flatten()>1e-6

T_PROBE_ms = 300.0; T_probe = int(T_PROBE_ms/params.dt)
SS = (int(150.0/params.dt), int(280.0/params.dt)); SUB_SS = 2
EPS = 0.001; SAT_HI = 0.85; SAT_LO = 0.02
AMPS = [0.4, 0.8, 1.5]; N_REPS = 10; NOISE = 0.01
ratio = params.tau/params.dt

def build_data(K_pools, M_pool, seed):
    """K_pools random pools of M_pool neurons each x len(AMPS) amplitudes."""
    rng = np.random.default_rng(seed)
    K_total = K_pools * len(AMPS)
    X = np.zeros((K_total, N)); Xp = np.zeros((K_total, N)); Ie = np.zeros((K_total, N))
    k = 0
    for p in range(K_pools):
        pool = rng.choice(N, size=M_pool, replace=False)
        for amp in AMPS:
            I_k = np.zeros((T_probe, N)); I_k[:, pool] = amp
            R0 = simulate_rate(W_norm, G_norm, I_k, T_PROBE_ms, params)["r"]
            x_acc = np.zeros(N); xp_acc = np.zeros(N)
            for _ in range(N_REPS):
                R = R0 + rng.normal(0, NOISE, R0.shape); R = np.clip(R, 0, 1)
                ss = R[SS[0]:SS[1]:SUB_SS]; ssp = R[SS[0]+1:SS[1]+1:SUB_SS]
                x_acc += ss.mean(0); xp_acc += ssp.mean(0)
            X[k] = x_acc/N_REPS; Xp[k] = xp_acc/N_REPS; Ie[k] = I_k[SS[0]]; k+=1
    return X, Xp, Ie

def fit(X, Xp, Ie):
    valid = Xp > EPS
    targ = (Xp - X)*ratio + X
    valid &= (targ>-0.95)&(targ<0.95)
    x_safe = (X<SAT_HI)&(X>SAT_LO) | (X==0)
    valid &= x_safe
    I_gap = X@G.T - X*G_rowsum[np.newaxis,:]
    z = np.arctanh(np.clip(targ,-0.95,0.95))/params.gain - I_gap - Ie
    W_hat = np.zeros((N,N))
    for j in range(N):
        sj = np.where(support[:,j])[0]
        if len(sj)==0: continue
        vj = valid[:, j]
        if vj.sum() < len(sj)+3: continue
        Xs = X[vj][:, sj]; zs = z[vj, j]
        A = Xs.T@Xs + 1e-3*np.eye(len(sj)); b = Xs.T@zs
        W_hat[sj, j] = np.clip(np.linalg.solve(A, b), 0, None)
    return W_hat

ws, we = int(100/params.dt), int(500/params.dt); T_test = 600.0
def cdiv(a,b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 1.0 - np.dot(a,b)/(na*nb) if na>1e-10 and nb>1e-10 else 1.0

test_stims = {}
I = make_tap_input(N, neurons, T_test, params.dt, 50.0, 30.0, 4.0)
test_stims["tap"] = (I, simulate_rate(W_norm, G_norm, I, T_test, params)["r"][ws:we].flatten())
I = make_chem_input(N, neurons, T_test, params.dt, 3.0)
test_stims["chem"] = (I, simulate_rate(W_norm, G_norm, I, T_test, params)["r"][ws:we].flatten())
I = np.zeros((int(T_test/params.dt), N))
for ii,n in enumerate(neurons):
    if n in {"AFDL","AFDR","ASJL","ASJR"}: I[:, ii]=2.0
test_stims["thermo"] = (I, simulate_rate(W_norm, G_norm, I, T_test, params)["r"][ws:we].flatten())
I = np.zeros((int(T_test/params.dt), N))
for ii,n in enumerate(neurons):
    if n in {"ASHL","ASHR"}: I[:, ii]=2.5
test_stims["nociception"] = (I, simulate_rate(W_norm, G_norm, I, T_test, params)["r"][ws:we].flatten())

def evaluate(W_hat):
    Wn = np.clip(W_hat/params.w_chem, 0, None)
    out = {}
    out["pearson"] = pearsonr(W_TRUE.flatten()[nz_mask], W_hat.flatten()[nz_mask])[0]
    for name, (I_test, r0) in test_stims.items():
        r = simulate_rate(Wn, G_norm, I_test, T_test, params)["r"][ws:we].flatten()
        out["div_"+name] = cdiv(r0, r)
    return out

# Sweep (K_pools, M_pool)
configs = [
    (300, 1),   # per-neuron baseline (matches v4) for reference
    (200, 5),
    (150, 10),
    (100, 15),
    (75,  20),
    (50,  30),
    (30,  50),
    (20,  80),
]

print(f"\n{'K_pools':>8}  {'M':>4}  {'total trials':>14}  {'pearson':>8}  {'div_tap':>8}  {'div_chem':>9}  {'div_th':>7}  {'div_no':>7}  verdict")
print("-"*100)
results = []
for K_p, M in configs:
    total_trials = K_p * len(AMPS) * N_REPS
    X, Xp, Ie = build_data(K_p, M, seed=42)
    W_hat = fit(X, Xp, Ie)
    m = evaluate(W_hat)
    passed = all(m["div_"+k] < 0.05 for k in ["tap","chem","thermo","nociception"])
    line = (f"{K_p:>8}  {M:>4}  {total_trials:>14}  {m['pearson']:>8.3f}  "
            f"{m['div_tap']:>8.4f}  {m['div_chem']:>9.4f}  "
            f"{m['div_thermo']:>7.4f}  {m['div_nociception']:>7.4f}  "
            f"{'PASS' if passed else 'FAIL'}")
    print(line); results.append((K_p, M, m, passed))

# Find smallest K_p that still passes
passing = [r for r in results if r[3]]
if passing:
    best = min(passing, key=lambda r: r[0]*r[1])
    K_p, M, m, _ = best
    speedup = (300 * 1) / (K_p * M / N)
    print(f"\nSmallest passing config: K_pools={K_p}, M={M}")
    print(f"  Total trials: {K_p*len(AMPS)*N_REPS} (v4: 9000 = {300*len(AMPS)*N_REPS})")
    print(f"  Pool-stim trial reduction: {(300*len(AMPS)*N_REPS)/(K_p*len(AMPS)*N_REPS):.1f}x fewer trials")

with open("simulation/results/scan_inverse_pool_summary.txt", "w", encoding="utf-8") as f:
    f.write("Pool-based scan inverse sweep\n"+"="*60+"\n")
    f.write(f"{'K_pools':>8}  {'M':>4}  {'trials':>10}  {'pearson':>8}  "
            f"{'div_tap':>8}  {'div_chem':>9}  {'div_th':>7}  {'div_no':>7}  verdict\n")
    for K_p, M, m, p in results:
        f.write(f"{K_p:>8}  {M:>4}  {K_p*len(AMPS)*N_REPS:>10}  {m['pearson']:>8.3f}  "
                f"{m['div_tap']:>8.4f}  {m['div_chem']:>9.4f}  "
                f"{m['div_thermo']:>7.4f}  {m['div_nociception']:>7.4f}  "
                f"{'PASS' if p else 'FAIL'}\n")
print("\nSaved: simulation/results/scan_inverse_pool_summary.txt")
