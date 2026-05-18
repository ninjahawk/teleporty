"""
n_reps sweep at fixed noise=0.02 and 0.05 to see how much averaging is needed
to bring tap circuit under threshold (div_tap < 0.05).
"""
import os, sys, numpy as np
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
# Reuse v4 by importing its primitives via re-implementation (faster than subprocess)
from simulation.load_connectome import load_connectome, load_gap_junctions
from simulation.rate_model import RateParams, simulate_rate, make_tap_input, make_chem_input
from scipy.stats import pearsonr

W_raw, neurons, W_norm = load_connectome()
G_raw, g_neurons = load_gap_junctions()
N = len(neurons)
g_idx = {n: i for i, n in enumerate(g_neurons)}; g_set = set(g_neurons)
G_aligned = np.zeros((N, N))
for i, ni in enumerate(neurons):
    for j, nj in enumerate(neurons):
        if ni in g_set and nj in g_set:
            G_aligned[i, j] = G_raw[g_idx[ni], g_idx[nj]]
G_norm = G_aligned/(G_aligned.max() or 1.0)

params = RateParams(tau=10.0, gain=2.5, w_chem=0.25, w_gap=0.1, dt=0.5)
W_TRUE = W_norm * params.w_chem; G = G_norm * params.w_gap
G_rowsum = G.sum(axis=1); support = (W_TRUE > 0); nz_mask = (W_TRUE.flatten() > 1e-6)

T_PROBE_ms = 300.0; T_probe = int(T_PROBE_ms/params.dt)
SS = (int(150.0/params.dt), int(280.0/params.dt)); SUB = 2
EPS = 0.001; SAT_HI = 0.85; SAT_LO = 0.02
AMPS = [0.4, 0.8, 1.5]; ratio = params.tau/params.dt

def build_data(noise, seed, n_reps):
    rng = np.random.default_rng(seed)
    K = N*len(AMPS); X=np.zeros((K,N)); Xp=np.zeros((K,N)); Ie=np.zeros((K,N))
    k=0
    for i in range(N):
        for amp in AMPS:
            I_k = np.zeros((T_probe, N)); I_k[:, i] = amp
            R0 = simulate_rate(W_norm, G_norm, I_k, T_PROBE_ms, params)["r"]
            x_acc = np.zeros(N); xp_acc = np.zeros(N)
            reps = n_reps if noise > 0 else 1
            for _ in range(reps):
                R = R0 + rng.normal(0, noise, R0.shape) if noise > 0 else R0
                if noise > 0: R = np.clip(R, 0, 1)
                ss = R[SS[0]:SS[1]:SUB]; ssp = R[SS[0]+1:SS[1]+1:SUB]
                x_acc += ss.mean(0); xp_acc += ssp.mean(0)
            X[k] = x_acc/reps; Xp[k] = xp_acc/reps; Ie[k] = I_k[SS[0]]; k+=1
    return X, Xp, Ie

def fit_W(X, Xp, Ie):
    valid = Xp > EPS
    targ = (Xp - X)*ratio + X
    valid &= (targ > -0.95) & (targ < 0.95)
    x_safe = (X < SAT_HI) & (X > SAT_LO) | (X == 0)
    valid &= x_safe
    I_gap = X @ G.T - X * G_rowsum[np.newaxis,:]
    z = np.arctanh(np.clip(targ, -0.95, 0.95))/params.gain - I_gap - Ie
    W_hat = np.zeros((N,N))
    for j in range(N):
        sj = np.where(support[:, j])[0]
        if len(sj) == 0: continue
        vj = valid[:, j]
        if vj.sum() < len(sj)+3: continue
        Xs = X[vj][:, sj]; zs = z[vj, j]
        A = Xs.T @ Xs + 1e-3 * np.eye(len(sj)); b = Xs.T @ zs
        W_hat[sj, j] = np.clip(np.linalg.solve(A, b), 0, None)
    return W_hat

ws, we = int(100/params.dt), int(500/params.dt); T_test = 600.0
def cdiv(a,b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 1.0 - np.dot(a,b)/(na*nb) if na>1e-10 and nb>1e-10 else 1.0

I_tap_test = make_tap_input(N, neurons, T_test, params.dt, 50.0, 30.0, 4.0)
r_tap_orig = simulate_rate(W_norm, G_norm, I_tap_test, T_test, params)["r"][ws:we].flatten()
I_chem_test = make_chem_input(N, neurons, T_test, params.dt, 3.0)
r_chem_orig = simulate_rate(W_norm, G_norm, I_chem_test, T_test, params)["r"][ws:we].flatten()

def divs(W_hat):
    Wn = np.clip(W_hat/params.w_chem, 0, None)
    rt = simulate_rate(Wn, G_norm, I_tap_test, T_test, params)["r"][ws:we].flatten()
    rc = simulate_rate(Wn, G_norm, I_chem_test, T_test, params)["r"][ws:we].flatten()
    pr = pearsonr(W_TRUE.flatten()[nz_mask], W_hat.flatten()[nz_mask])[0]
    return cdiv(r_tap_orig, rt), cdiv(r_chem_orig, rc), pr

print("="*72); print("n_reps sweep at noise=0.02 and 0.05"); print("="*72)
print(f"{'noise':>7}  {'n_reps':>6}  {'div_tap':>8}  {'div_chem':>9}  {'pearson':>8}  verdict")
print("-"*60)
lines=[]
for noise in [0.02, 0.05]:
    for nr in [10, 30, 100]:
        W_hat = fit_W(*build_data(noise, 42, nr))
        dt, dc, pr = divs(W_hat)
        verdict = "PASS" if dt<0.05 and dc<0.05 else "FAIL"
        line = f"{noise:>7.3f}  {nr:>6}  {dt:>8.4f}  {dc:>9.4f}  {pr:>8.3f}  {verdict}"
        print(line); lines.append(line)

with open("simulation/results/scan_inverse_nreps_sweep.txt","w",encoding="utf-8") as f:
    f.write("n_reps sweep -- noise vs reps needed for PASS\n"+"="*50+"\n")
    f.write(f"{'noise':>7}  {'n_reps':>6}  {'div_tap':>8}  {'div_chem':>9}  {'pearson':>8}  verdict\n")
    f.write("-"*60+"\n"+"\n".join(lines)+"\n")
print("\nSaved: simulation/results/scan_inverse_nreps_sweep.txt")
