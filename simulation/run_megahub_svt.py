"""
Mega-hub reconstruction via Singular Value Thresholding (SVT) multi-task fit.

The N=2000 FlyWire failure is caused by mega-hubs (|supp| > 1000) that the
per-neuron regression cannot reconstruct from K ~ 400 pool observations.

The fix (per math/direction1_megahub_limitation.md): exploit the empirically
measured low d_eff of hub weight columns via a nuclear-norm-penalized
low-rank reconstruction.

For the set of hub columns W_H (N x n_hubs), known to be low-rank:
  minimize  sum_j ||z_j - X[:,supp_j] @ W_H[:,j]||^2  +  lambda * ||W_H||_*

Solved by proximal gradient / SVT iteration:
  1. Gradient step on the data term (per hub column)
  2. Soft-threshold the singular values of the stacked W_H matrix

This script:
  - Builds a synthetic network with mega-hubs where the basic protocol
    FAILS behaviorally (not just in Pearson)
  - Compares: per-neuron strong-ridge  vs  SVT multi-task
  - Behavioral verification, not just Pearson
"""
import os, sys, numpy as np, time
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from simulation.rate_model import RateParams, simulate_rate
from scipy.stats import pearsonr

print("="*72); print("MEGA-HUB SVT MULTI-TASK RECONSTRUCTION"); print("="*72)
params = RateParams(tau=10.0, gain=2.5, w_chem=0.25, w_gap=0.1, dt=0.5)

# Network: N=600. 580 normal neurons + 20 mega-hubs.
# Mega-hubs share a latent rank-r structure (same cell type).
N_normal = 580
N_HUBS = 20
HUB_SUPP = 250        # each mega-hub has 250 inputs
LATENT_RANK = 12      # the 20 hubs' weight columns live in a rank-12 space
N = N_normal + N_HUBS
p_chem = 0.02

rng = np.random.default_rng(1)
W = np.zeros((N, N))
# Normal neurons
mask = (rng.random((N, N_normal)) < p_chem)
np.fill_diagonal(mask[:N_normal,:], False)
W[:, :N_normal][mask] = rng.lognormal(-2.0, 1.0, mask.sum())
# Mega-hubs: shared support, low-rank weights, AND they project downstream
# strongly (so they matter for behavior)
shared_supp = rng.choice(N_normal, size=HUB_SUPP, replace=False)
latent_basis = rng.lognormal(-2.0, 0.5, (N, LATENT_RANK))
hub_cols = list(range(N_normal, N))
for h, j in enumerate(hub_cols):
    coeff = rng.normal(0, 1.0, LATENT_RANK)
    w = np.abs(latent_basis[shared_supp] @ coeff)
    W[shared_supp, j] = w
    # hub projects to 8 downstream normal neurons (strong)
    post = rng.choice(N_normal, size=8, replace=False)
    W[j, post] = rng.lognormal(-1.0, 0.3, 8)

W_norm = W / W.max()
G_norm = np.zeros((N, N))
W_TRUE = W_norm * params.w_chem
G = G_norm * params.w_gap
G_rowsum = G.sum(axis=1)
support = (W_TRUE > 0)
nz_mask = W_TRUE.flatten() > 1e-6

print(f"  N={N}: {N_normal} normal + {N_HUBS} mega-hubs (|supp|={HUB_SUPP})")
u_t, s_t, _ = np.linalg.svd(W_TRUE[:, hub_cols], full_matrices=False)
s2 = s_t**2; d_eff = (s2.sum()**2)/(s2**2).sum()
print(f"  Hub weight columns: true d_eff = {d_eff:.2f} (rank set: {LATENT_RANK})")

T_PROBE_ms = 300.0; T_probe = int(T_PROBE_ms/params.dt)
SS = (int(150.0/params.dt), int(280.0/params.dt)); SUB_SS = 2
EPS = 0.001; SAT_HI = 0.85; SAT_LO = 0.02
AMPS = [0.4, 0.8, 1.5]; N_REPS = 4; NOISE = 0.01
ratio = params.tau/params.dt

# K_pools deliberately small relative to HUB_SUPP: per-neuron fit under-determined
K_POOLS = 80   # K=80 << HUB_SUPP=250: per-neuron hub fit must fail
M = 15
print(f"  Pool stim: K={K_POOLS}, M={M} (K << |supp_hub|={HUB_SUPP} on purpose)")

def simulate_pool():
    rng_p = np.random.default_rng(42)
    K_total = K_POOLS*len(AMPS)
    X = np.zeros((K_total,N)); Xp = np.zeros((K_total,N)); Ie = np.zeros((K_total,N))
    k=0
    for p in range(K_POOLS):
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

def fit_normal(X, z, valid):
    """Standard per-neuron fit for the normal neurons only."""
    W_hat = np.zeros((N,N))
    for j in range(N_normal):
        sj = np.where(support[:,j])[0]
        if len(sj)==0: continue
        vj = valid[:,j]
        if vj.sum() < 5: continue
        ridge = 0.5 if vj.sum() < len(sj)+3 else 1e-3
        Xs = X[vj][:,sj]; zs = z[vj,j]
        A = Xs.T@Xs + ridge*np.eye(len(sj)); b = Xs.T@zs
        W_hat[sj,j] = np.clip(np.linalg.solve(A,b),0,None)
    return W_hat

def fit_hubs_perneuron(X, z, valid, W_hat):
    """Per-neuron strong-ridge for hub columns (the failing baseline)."""
    for j in hub_cols:
        sj = np.where(support[:,j])[0]
        vj = valid[:,j]
        if vj.sum() < 5: continue
        Xs = X[vj][:,sj]; zs = z[vj,j]
        A = Xs.T@Xs + 0.5*np.eye(len(sj)); b = Xs.T@zs
        W_hat[sj,j] = np.clip(np.linalg.solve(A,b),0,None)
    return W_hat

def fit_hubs_svt(X, z, valid, W_hat, rank_target, n_iter=200, step=None):
    """SVT multi-task fit for hub columns.

    All hubs share support `shared_supp`. Stack into matrix H (S x n_hubs)
    where S = |shared_supp|. Minimize data error + nuclear norm via
    proximal gradient (iterative singular value soft-thresholding).
    """
    S = len(shared_supp)
    nh = len(hub_cols)
    # Precompute per-hub design matrices restricted to shared_supp
    designs = []   # (X_j, z_j) for each hub
    for h, j in enumerate(hub_cols):
        vj = valid[:, j]
        Xj = X[vj][:, shared_supp]   # (n_valid, S)
        zj = z[vj, j]
        designs.append((Xj, zj))
    # Lipschitz const estimate for step size
    if step is None:
        max_op = max((np.linalg.norm(Xj, 2)**2 if Xj.shape[0] > 0 else 1.0)
                     for Xj, _ in designs)
        step = 1.0 / (max_op + 1e-6)
    # init H from per-neuron strong-ridge
    H = np.zeros((S, nh))
    for h, (Xj, zj) in enumerate(designs):
        if Xj.shape[0] < 5: continue
        A = Xj.T@Xj + 0.5*np.eye(S); b = Xj.T@zj
        H[:, h] = np.linalg.solve(A, b)
    # nuclear-norm threshold tuned so that ~rank_target singular values survive
    for it in range(n_iter):
        # gradient step on data term, per hub
        grad = np.zeros((S, nh))
        for h, (Xj, zj) in enumerate(designs):
            if Xj.shape[0] < 5: continue
            resid = Xj @ H[:, h] - zj
            grad[:, h] = Xj.T @ resid
        H = H - step * grad
        # SVD soft-threshold
        u, s, vt = np.linalg.svd(H, full_matrices=False)
        # threshold: keep top rank_target, shrink the rest
        if len(s) > rank_target:
            thresh = s[rank_target]
        else:
            thresh = 0.0
        s_new = np.maximum(s - thresh, 0)
        H = u @ np.diag(s_new) @ vt
    # write back, non-negative + support
    for h, j in enumerate(hub_cols):
        W_hat[shared_supp, j] = np.clip(H[:, h], 0, None)
    return W_hat

# Behavioral verification
ws, we = int(100/params.dt), int(500/params.dt); T_test = 600.0
def cdiv(a,b):
    na,nb=np.linalg.norm(a),np.linalg.norm(b)
    return 1.0-np.dot(a,b)/(na*nb) if na>1e-10 and nb>1e-10 else 1.0

rng_t = np.random.default_rng(7)
test_stims = []
for t in range(5):
    stim = rng_t.choice(N_normal, size=10, replace=False)
    I_t = np.zeros((int(T_test/params.dt), N)); I_t[:, stim] = 3.0
    r0 = simulate_rate(W_norm, G_norm, I_t, T_test, params)["r"][ws:we].flatten()
    test_stims.append((I_t, r0))

def behavioral(W_hat):
    Wn = np.clip(W_hat/params.w_chem, 0, None)
    divs = []
    for I_t, r0 in test_stims:
        rh = simulate_rate(Wn, G_norm, I_t, T_test, params)["r"][ws:we].flatten()
        divs.append(cdiv(r0, rh))
    return divs

# === Run ===
print("\nSimulating pool stim...")
t0 = time.time()
X, Xp, Ie = simulate_pool()
z, valid = get_z(X, Xp, Ie)
print(f"  done in {time.time()-t0:.1f}s")

W_base = fit_normal(X, z, valid)

# Baseline: per-neuron strong ridge for hubs
W_pn = fit_hubs_perneuron(X, z, valid, W_base.copy())
divs_pn = behavioral(W_pn)
r_pn = pearsonr(W_TRUE.flatten()[nz_mask], W_pn.flatten()[nz_mask])[0]

# SVT multi-task for hubs
t0 = time.time()
W_svt = fit_hubs_svt(X, z, valid, W_base.copy(), rank_target=LATENT_RANK)
print(f"  SVT fit: {time.time()-t0:.1f}s")
divs_svt = behavioral(W_svt)
r_svt = pearsonr(W_TRUE.flatten()[nz_mask], W_svt.flatten()[nz_mask])[0]

# Hub-only Pearson
def hub_pearson(W_hat):
    tw, hw = [], []
    for j in hub_cols:
        sj = np.where(support[:,j])[0]
        tw.extend(W_TRUE[sj,j]); hw.extend(W_hat[sj,j])
    return pearsonr(tw, hw)[0]

print("\n" + "="*72)
print(f"{'Method':<28}  {'r_all':>7}  {'r_hub':>7}  {'div (mean)':>11}  verdict")
print("-"*65)
for name, W_h, divs in [("Per-neuron strong-ridge", W_pn, divs_pn),
                          ("SVT multi-task", W_svt, divs_svt)]:
    rh = hub_pearson(W_h)
    ra = pearsonr(W_TRUE.flatten()[nz_mask], W_h.flatten()[nz_mask])[0]
    dmean = np.mean(divs)
    passed = all(d<0.05 for d in divs)
    print(f"{name:<28}  {ra:>7.3f}  {rh:>7.3f}  {dmean:>11.4f}  {'PASS' if passed else 'FAIL'}")

print(f"\nPer-test divergences:")
print(f"  per-neuron: {[f'{d:.3f}' for d in divs_pn]}")
print(f"  SVT:        {[f'{d:.3f}' for d in divs_svt]}")

svt_pass = all(d<0.05 for d in divs_svt)
pn_pass = all(d<0.05 for d in divs_pn)
print(f"\n=== VERDICT ===")
if svt_pass and not pn_pass:
    print("SVT multi-task FIXES the mega-hub failure that per-neuron cannot.")
elif svt_pass and pn_pass:
    print("Both pass -- this synthetic case wasn't hard enough to distinguish.")
elif not svt_pass and not pn_pass:
    print("Both fail -- SVT implementation needs work, or problem is harder.")
else:
    print("SVT worse than per-neuron -- implementation bug.")

with open("simulation/results/megahub_svt.txt", "w", encoding="utf-8") as f:
    f.write("Mega-hub SVT multi-task reconstruction test\n"+"="*55+"\n")
    f.write(f"N={N}, {N_HUBS} mega-hubs |supp|={HUB_SUPP}, latent rank={LATENT_RANK}\n")
    f.write(f"K_pools={K_POOLS} (<< |supp_hub|), M={M}\n\n")
    f.write(f"Per-neuron strong-ridge: r_hub={hub_pearson(W_pn):.3f}, "
            f"div_mean={np.mean(divs_pn):.4f}, {'PASS' if pn_pass else 'FAIL'}\n")
    f.write(f"SVT multi-task:          r_hub={hub_pearson(W_svt):.3f}, "
            f"div_mean={np.mean(divs_svt):.4f}, {'PASS' if svt_pass else 'FAIL'}\n")
print("\nSaved: simulation/results/megahub_svt.txt")
