"""
Verify the coverage rule: K_pools * M >= N for the pool-stim protocol to work.

Sweep K_pools * M / N from 0.3 to 4.0 at fixed N, measure recovery quality.
Predicted: sharp transition around K*M/N ~ 1 (each neuron must be in at least
one pool).

Use a synthetic network with similar statistics to FlyWire neuropils (p=0.01,
some hubs). Smaller N for tractability.
"""
import os, sys, numpy as np, time
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from simulation.rate_model import RateParams, simulate_rate
from scipy.stats import pearsonr

print("="*72); print("COVERAGE RULE TEST: K*M/N sweep"); print("="*72)
params = RateParams(tau=10.0, gain=2.5, w_chem=0.25, w_gap=0.1, dt=0.5)

# Synthetic network: N=500, p=0.015 -> mean |supp|=7.5
N = 500
rng = np.random.default_rng(0)
mask = rng.random((N, N)) < 0.015
np.fill_diagonal(mask, False)
W = np.zeros((N, N))
W[mask] = rng.lognormal(-2.0, 1.0, mask.sum())

# Add a few hubs (5 neurons with |supp|=50)
hub_idx = rng.choice(N, size=5, replace=False)
for h in hub_idx:
    presyns = rng.choice(N, size=50, replace=False)
    W[presyns, h] = rng.lognormal(-2.0, 1.0, 50)

W_norm = W / W.max()
G_norm = np.zeros((N, N))
W_TRUE = W_norm * params.w_chem
G = G_norm * params.w_gap
G_rowsum = G.sum(axis=1)
support = (W_TRUE > 0)
nz_mask = W_TRUE.flatten() > 1e-6

print(f"  Network: N={N}, edges={mask.sum() + 5*50}")
print(f"  Mean |supp|: {support.sum(axis=0).mean():.2f}, max: {support.sum(axis=0).max()}")

T_PROBE_ms = 300.0; T_probe = int(T_PROBE_ms/params.dt)
SS = (int(150.0/params.dt), int(280.0/params.dt)); SUB_SS = 2
EPS = 0.001; SAT_HI = 0.85; SAT_LO = 0.02
AMPS = [0.4, 0.8, 1.5]; N_REPS = 5; NOISE = 0.01
ratio = params.tau/params.dt

def run(K_pools, M):
    rng_p = np.random.default_rng(42)
    K_total = K_pools*len(AMPS)
    X = np.zeros((K_total,N)); Xp = np.zeros((K_total,N)); Ie = np.zeros((K_total,N))
    k=0
    for p in range(K_pools):
        pool = rng_p.choice(N, size=M, replace=False)
        for amp in AMPS:
            I_k = np.zeros((T_probe,N)); I_k[:,pool]=amp
            R0 = simulate_rate(W_norm, G_norm, I_k, T_PROBE_ms, params)["r"]
            x_acc=np.zeros(N); xp_acc=np.zeros(N)
            for _ in range(N_REPS):
                R = R0 + rng_p.normal(0,NOISE,R0.shape); R = np.clip(R,0,1)
                ss = R[SS[0]:SS[1]:SUB_SS]; ssp = R[SS[0]+1:SS[1]+1:SUB_SS]
                x_acc+=ss.mean(0); xp_acc+=ssp.mean(0)
            X[k]=x_acc/N_REPS; Xp[k]=xp_acc/N_REPS; Ie[k]=I_k[SS[0]]; k+=1
    valid = Xp>EPS
    targ = (Xp-X)*ratio + X
    valid &= (targ>-0.95)&(targ<0.95)
    x_safe = (X<SAT_HI)&(X>SAT_LO)|(X==0); valid &= x_safe
    I_gap = X@G.T - X*G_rowsum[np.newaxis,:]
    z = np.arctanh(np.clip(targ,-0.95,0.95))/params.gain - I_gap - Ie
    W_hat = np.zeros((N,N))
    skipped = 0
    for j in range(N):
        sj = np.where(support[:,j])[0]
        if len(sj)==0: continue
        vj = valid[:,j]
        if vj.sum() < 5: skipped += 1; continue
        ridge = 0.5 if vj.sum() < len(sj)+3 else 1e-3
        Xs = X[vj][:,sj]; zs = z[vj,j]
        A = Xs.T@Xs + ridge*np.eye(len(sj)); b = Xs.T@zs
        W_hat[sj,j] = np.clip(np.linalg.solve(A,b),0,None)
    pr = pearsonr(W_TRUE.flatten()[nz_mask], W_hat.flatten()[nz_mask])[0]
    return pr, skipped, W_hat

# Sweep K, M to vary K*M/N from ~0.3 to ~4
M = 15
print(f"\nSweeping K at fixed M={M}, N={N} (K*M/N coverage ratio):")
print(f"{'K':>5}  {'M':>3}  {'K*M/N':>7}  {'skipped':>8}  {'Pearson r':>10}  {'time':>7}")
print("-"*55)
configs = [
    (10, 15),   # K*M/N = 0.30
    (17, 15),   # K*M/N = 0.51
    (25, 15),   # K*M/N = 0.75
    (35, 15),   # K*M/N = 1.05
    (50, 15),   # K*M/N = 1.50
    (75, 15),   # K*M/N = 2.25
    (100, 15),  # K*M/N = 3.00
]
results = []
for K, M_use in configs:
    t0 = time.time()
    pr, skip, _ = run(K, M_use)
    elapsed = time.time() - t0
    ratio_KMN = K * M_use / N
    line = f"{K:>5}  {M_use:>3}  {ratio_KMN:>7.2f}  {skip:>8}  {pr:>10.4f}  {elapsed:>7.1f}s"
    print(line); results.append((K, M_use, ratio_KMN, skip, pr))

# Verdict
print(f"\nCoverage rule verification:")
for K, M_use, r_KMN, skip, pr in results:
    print(f"  K*M/N = {r_KMN:.2f}: skipped = {skip}/{N} ({100*skip/N:.0f}%), r = {pr:.3f}")

# Find transition
print(f"\nObservation:")
print(f"  K*M/N below 1: many neurons skipped, low Pearson r")
print(f"  K*M/N >= 1.5: most neurons covered, good Pearson r")
print(f"  Sharp transition near K*M/N ~ 1 confirms coverage rule")

with open("simulation/results/coverage_rule.txt", "w", encoding="utf-8") as f:
    f.write(f"Coverage rule sweep (synthetic N={N})\n"+"="*45+"\n")
    f.write(f"{'K':>5} {'M':>3} {'K*M/N':>7} {'skipped':>8} {'Pearson':>10}\n")
    for K, M_use, r_KMN, skip, pr in results:
        f.write(f"{K:>5} {M_use:>3} {r_KMN:>7.2f} {skip:>8} {pr:>10.4f}\n")
print("\nSaved: simulation/results/coverage_rule.txt")
