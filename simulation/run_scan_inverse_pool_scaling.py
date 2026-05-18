"""
Pool scan inverse -- scaling test on synthetic networks.

Question: does pool stim quality / trial count scale predictably with N?
Prediction: K_pools needed ~ 6 * mean|supp_j| (from C. elegans floor).

We build synthetic sparse random connectomes at N = 500, 1000, 2000 with
similar statistics to C. elegans (chemical sparsity p ~ 0.04, gap-junction
sparsity ~ 0.024), and test pool stim with K_pools scaled appropriately.
"""
import os, sys, numpy as np, time
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from simulation.rate_model import RateParams, simulate_rate
from scipy.stats import pearsonr

print("="*72); print("POOL SCAN INVERSE -- synthetic network scaling"); print("="*72)

params = RateParams(tau=10.0, gain=2.5, w_chem=0.25, w_gap=0.1, dt=0.5)

def make_synthetic(N, p_chem=0.04, p_gap=0.024, seed=0):
    rng = np.random.default_rng(seed)
    # chemical synapses: directed sparse with lognormal weights
    mask = rng.random((N, N)) < p_chem
    np.fill_diagonal(mask, False)
    W = np.zeros((N, N))
    n_edge = mask.sum()
    weights = rng.lognormal(mean=-2.0, sigma=1.0, size=n_edge)  # weights ~ 0.1
    W[mask] = weights
    W_norm = W / (W.max() or 1.0)
    # gap junctions: symmetric sparse
    G_mask = rng.random((N, N)) < p_gap
    G_mask = G_mask | G_mask.T
    np.fill_diagonal(G_mask, False)
    G = np.zeros((N, N))
    G[G_mask] = rng.lognormal(mean=-2.0, sigma=0.5, size=G_mask.sum())
    G_norm = G / (G.max() or 1.0)
    return W_norm, G_norm

T_PROBE_ms = 300.0; T_probe = int(T_PROBE_ms/params.dt)
SS = (int(150.0/params.dt), int(280.0/params.dt)); SUB_SS = 2
EPS = 0.001; SAT_HI = 0.85; SAT_LO = 0.02
AMPS = [0.4, 0.8, 1.5]; N_REPS = 5  # reduce reps for speed at larger N
NOISE = 0.01
ratio = params.tau/params.dt

def build_and_fit(W_norm, G_norm, K_pools, M_pool, seed):
    N = W_norm.shape[0]
    W_TRUE = W_norm * params.w_chem
    G = G_norm * params.w_gap
    G_rowsum = G.sum(axis=1)
    support = (W_TRUE > 0)
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

    valid = Xp > EPS
    targ = (Xp - X)*ratio + X
    valid &= (targ>-0.95)&(targ<0.95)
    x_safe = (X<SAT_HI)&(X>SAT_LO)|(X==0); valid &= x_safe
    I_gap = X@G.T - X*G_rowsum[np.newaxis,:]
    z = np.arctanh(np.clip(targ,-0.95,0.95))/params.gain - I_gap - Ie

    W_hat = np.zeros((N,N))
    for j in range(N):
        sj = np.where(support[:,j])[0]
        if len(sj)==0: continue
        vj = valid[:,j]
        if vj.sum() < len(sj)+3: continue
        Xs = X[vj][:, sj]; zs = z[vj, j]
        A = Xs.T@Xs + 1e-3*np.eye(len(sj)); b = Xs.T@zs
        W_hat[sj, j] = np.clip(np.linalg.solve(A, b), 0, None)
    nz_mask = W_TRUE.flatten() > 1e-6
    r = pearsonr(W_TRUE.flatten()[nz_mask], W_hat.flatten()[nz_mask])[0]
    frob = np.linalg.norm(W_hat - W_TRUE)/np.linalg.norm(W_TRUE)
    return W_hat, r, frob

print(f"{'N':>5} {'mean|supp|':>10} {'K_pools':>8} {'M':>4} {'trials':>8} {'Pearson':>8} {'frob':>8} {'time(s)':>8}")
print("-"*70)

# Test 3 sizes with K_pools scaled as 6 * mean|supp_j|
results = []
for N in [300, 600, 1000]:
    W_norm, G_norm = make_synthetic(N, seed=1)
    W_TRUE = W_norm * params.w_chem
    mean_supp = (W_TRUE > 0).sum(axis=0).mean()  # mean incoming-degree per neuron
    K_target = int(np.ceil(8 * mean_supp))  # 8x the support size, safety margin over 6x
    M_target = max(15, int(mean_supp))      # at least 15, scale up if support is larger
    t0 = time.time()
    W_hat, r, frob = build_and_fit(W_norm, G_norm, K_target, M_target, seed=42)
    elapsed = time.time() - t0
    n_trials = K_target * len(AMPS) * N_REPS
    print(f"{N:>5} {mean_supp:>10.2f} {K_target:>8} {M_target:>4} {n_trials:>8} {r:>8.4f} {frob:>8.4f} {elapsed:>8.1f}")
    results.append((N, mean_supp, K_target, M_target, n_trials, r, frob))

print("\nScaling observations:")
print(f"  K_pools / mean|supp_j| ratio is held at 8 across sizes")
print(f"  M_pool scaled to track mean|supp_j|")
print(f"  Pearson r ranges:", [f"{r[5]:.3f}" for r in results])

# Save
with open("simulation/results/scan_inverse_pool_scaling.txt", "w", encoding="utf-8") as f:
    f.write("Pool scan inverse -- scaling on synthetic networks\n"+"="*55+"\n")
    f.write(f"{'N':>5} {'mean|supp|':>10} {'K_pools':>8} {'M':>4} {'trials':>8} {'Pearson':>8} {'frob':>8}\n")
    for N, ms, Kp, M, nt, r, fr in results:
        f.write(f"{N:>5} {ms:>10.2f} {Kp:>8} {M:>4} {nt:>8} {r:>8.4f} {fr:>8.4f}\n")
    f.write(f"\nK_pools / mean|supp_j| ratio held at 8.\n")
print("\nSaved: simulation/results/scan_inverse_pool_scaling.txt")
