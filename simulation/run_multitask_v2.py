"""
Multi-task pool-stim v2: SVD shrinkage post-processing.

The ALS approach (v1) was slow and didn't converge well. Cleaner approach:

  1. Run standard independent pool-stim fits (gets noisy W_hat per hub).
  2. For each cell-type, stack the recovered W_hat columns into a matrix.
  3. SVD-truncate to rank d_eff (denoises and exploits low-rank structure).
  4. Re-fill weights from the truncated reconstruction.

This works as long as independent fits get SOME signal. For under-determined
cases (K << |supp|), even the independent fit's noisy/zero output can be
improved by enforcing the cell-type subspace structure.

We test on a synthetic hub network with shared support across hubs.
"""
import os, sys, numpy as np, time
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from simulation.rate_model import RateParams, simulate_rate
from scipy.stats import pearsonr

print("="*72); print("MULTI-TASK POOL-STIM v2 (SVD shrinkage)"); print("="*72)
params = RateParams(tau=10.0, gain=2.5, w_chem=0.25, w_gap=0.1, dt=0.5)

# Compact: N=500 normal + 10 hubs sharing the same 150-neuron support
N_normal = 500
N_HUBS = 10
HUB_SUPP = 150
LATENT_RANK = 8
N = N_normal + N_HUBS
p_chem = 0.02   # mean |supp|_normal ~ 10

rng = np.random.default_rng(0)
W = np.zeros((N, N))

# Normal neurons (cols 0..N_normal-1)
mask = (rng.random((N, N_normal)) < p_chem)
np.fill_diagonal(mask[:N_normal, :], False)
W[:, :N_normal][mask] = rng.lognormal(-2.0, 1.0, mask.sum())

# Hub neurons: SHARED support, low-rank weight structure
latent_basis = rng.lognormal(-2.0, 0.5, (N, LATENT_RANK))
shared_supp = rng.choice(N_normal, size=HUB_SUPP, replace=False)
hub_cols = list(range(N_normal, N))
for h, j in enumerate(hub_cols):
    coeff = rng.normal(0, 1.0, LATENT_RANK)
    w = latent_basis[shared_supp] @ coeff
    W[shared_supp, j] = np.abs(w)

W_norm = W / W.max()
G_norm = np.zeros((N, N))
W_TRUE = W_norm * params.w_chem
G = G_norm * params.w_gap
G_rowsum = G.sum(axis=1)
support = (W_TRUE > 0)

# Verify d_eff of hub columns
W_hubs_full = W_TRUE[:, hub_cols]
u_t, s_t, _ = np.linalg.svd(W_hubs_full, full_matrices=False)
s_t2 = s_t**2; d_eff_true = (s_t2.sum()**2) / (s_t2**2).sum()
print(f"  True hub d_eff: {d_eff_true:.2f}  (set rank: {LATENT_RANK})")

# Pool stim
T_PROBE_ms = 300.0; T_probe = int(T_PROBE_ms/params.dt)
SS = (int(150.0/params.dt), int(280.0/params.dt)); SUB_SS = 2
EPS = 0.001; SAT_HI = 0.85; SAT_LO = 0.02
AMPS = [0.4, 0.8, 1.5]; N_REPS = 5; NOISE = 0.01
ratio = params.tau/params.dt

def simulate_pool(K_pools, M):
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
    return X, Xp, Ie

def get_z(X, Xp, Ie):
    valid = Xp > EPS
    targ = (Xp - X)*ratio + X
    valid &= (targ>-0.95)&(targ<0.95)
    x_safe = (X<SAT_HI)&(X>SAT_LO)|(X==0); valid &= x_safe
    I_gap = X@G.T - X*G_rowsum[np.newaxis,:]
    z = np.arctanh(np.clip(targ,-0.95,0.95))/params.gain - I_gap - Ie
    return z, valid

def fit_independent_lenient(X, z, valid, hub_cols, ridge=1e-1):
    """Per-neuron fit. When under-determined (K < |supp|), use STRONG ridge
    to get a regularized solution rather than skip. This gives noisy but
    non-zero estimates that SVD-shrinkage can clean up."""
    W_hat = np.zeros((N,N))
    for j in hub_cols:
        sj = np.where(support[:,j])[0]
        if len(sj)==0: continue
        vj = valid[:,j]
        if vj.sum() < 5: continue   # need at least 5 valid observations
        Xs = X[vj][:, sj]; zs = z[vj, j]
        A = Xs.T @ Xs + ridge * np.eye(len(sj))
        b = Xs.T @ zs
        W_hat[sj, j] = np.linalg.solve(A, b)  # NOT clipped yet
    return W_hat

def svd_shrink(W_hat, hub_cols, rank):
    """Truncate the hub-columns submatrix to rank, then re-fill."""
    M = W_hat[:, hub_cols]  # (N, n_hubs)
    u, s, vt = np.linalg.svd(M, full_matrices=False)
    s[rank:] = 0
    M_low = u @ np.diag(s) @ vt
    W_out = W_hat.copy()
    W_out[:, hub_cols] = M_low
    # Enforce non-negativity and support
    W_out[:, hub_cols] = np.clip(W_out[:, hub_cols], 0, None)
    for h, j in enumerate(hub_cols):
        sj = ~support[:, j]
        W_out[sj, j] = 0  # zero outside support
    return W_out

# Sweep K
print(f"\n{'K_pools':>8}  {'M':>4}  {'Indep r':>10}  {'Indep+SVD r':>14}  {'r_true':>8}")
print("-"*55)
results = []
for K_pools in [50, 100, 150, 200, 400]:
    M = 15
    t0 = time.time()
    X, Xp, Ie = simulate_pool(K_pools, M)
    z, valid = get_z(X, Xp, Ie)
    W_ind = fit_independent_lenient(X, z, valid, hub_cols, ridge=0.1)
    W_mt = svd_shrink(W_ind, hub_cols, rank=LATENT_RANK)
    # Pearson per-hub, averaged
    r_ind = []; r_mt = []
    for j in hub_cols:
        sj = np.where(support[:,j])[0]
        tw = W_TRUE[sj, j]
        if tw.std() < 1e-9: continue
        if W_ind[sj, j].std() > 1e-9:
            r_ind.append(pearsonr(tw, W_ind[sj, j])[0])
        if W_mt[sj, j].std() > 1e-9:
            r_mt.append(pearsonr(tw, W_mt[sj, j])[0])
    r_ind_mean = np.mean(r_ind) if r_ind else 0.0
    r_mt_mean = np.mean(r_mt) if r_mt else 0.0
    elapsed = time.time() - t0
    line = f"{K_pools:>8}  {M:>4}  {r_ind_mean:>10.4f}  {r_mt_mean:>14.4f}  {d_eff_true:>8.2f}  ({elapsed:.1f}s)"
    print(line); results.append((K_pools, r_ind_mean, r_mt_mean))

print(f"\nSummary:")
print(f"  Setup: 10 hubs, |supp|=150 (shared), true latent rank = {LATENT_RANK}, d_eff = {d_eff_true:.1f}")
print(f"  Independent fit needs K > 150 (|supp|).")
print(f"  SVD-shrinkage post-processing should work even at K << |supp|.")

with open("simulation/results/multitask_v2.txt", "w", encoding="utf-8") as f:
    f.write("Multi-task pool stim v2 (SVD shrinkage)\n"+"="*55+"\n")
    f.write(f"|supp_hub|={HUB_SUPP}, true latent rank={LATENT_RANK}, true d_eff={d_eff_true:.1f}\n\n")
    f.write(f"{'K_pools':>8}  {'Indep r':>10}  {'Indep+SVD r':>14}\n")
    for K, ri, rm in results:
        f.write(f"{K:>8}  {ri:>10.4f}  {rm:>14.4f}\n")
print(f"\nSaved: simulation/results/multitask_v2.txt")
