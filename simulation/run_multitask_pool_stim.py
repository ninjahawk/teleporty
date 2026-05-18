"""
Multi-task pool-stim protocol test.

Builds a synthetic network with multiple hub neurons that share latent
structure (same cell type). The current independent-fit protocol needs
K > |supp_j| per hub. Multi-task fit (low-rank factorization) needs
K > d_eff of the shared latent space.

Setup:
  N = 1000 neurons
  10 hub neurons (type "T"), each with |supp_j| = 300, all sharing a
  rank-r latent structure (their weight columns are linear combinations
  of r=20 latent basis vectors)
  990 normal neurons with mean |supp| = 12

Test: pool stim with K_pools varying. Compare three fits:
  (A) Per-neuron independent (current protocol)
  (B) Multi-task low-rank for the hub type

Predict: A fails for K < 300, B works for K > 30.
"""
import os, sys, numpy as np, time
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from simulation.rate_model import RateParams, simulate_rate
from scipy.stats import pearsonr

print("="*72); print("MULTI-TASK POOL-STIM PROTOCOL TEST"); print("="*72)
params = RateParams(tau=10.0, gain=2.5, w_chem=0.25, w_gap=0.1, dt=0.5)

N = 1000
N_HUBS = 10
HUB_SUPP = 300
LATENT_RANK = 20      # the hubs' weight columns are rank-r combinations of a basis
p_chem = 0.012        # for normal neurons -> mean |supp| ~ 12

rng = np.random.default_rng(0)
W = np.zeros((N, N))

# Normal-neuron weights (first N-N_HUBS neurons)
N_normal = N - N_HUBS
mask = (rng.random((N, N_normal)) < p_chem)
np.fill_diagonal(mask[:N_normal, :], False)
W[:, :N_normal][mask] = rng.lognormal(-2.0, 1.0, mask.sum())

# Hub neurons (last N_HUBS): each has |supp|=HUB_SUPP, all from a shared rank-r basis
# Generate r latent "input patterns" of length N
latent_basis = rng.lognormal(-2.0, 0.5, (N, LATENT_RANK))
# Each hub picks a random subset of HUB_SUPP presyn neurons and a random
# coefficient vector in the latent space
hub_supports = []
for h in range(N_HUBS):
    hub_col = N_normal + h
    supp = rng.choice(N_normal, size=HUB_SUPP, replace=False)
    hub_supports.append(supp)
    # weight column: w[supp] = sum_k coeff_k * latent_basis[supp, k]
    coeff = rng.normal(0, 1.0, LATENT_RANK)
    w = latent_basis[supp] @ coeff
    w = np.abs(w)  # non-negative weights
    W[supp, hub_col] = w

W_norm = W / W.max()
# Tiny gap junctions to keep dynamics stable
G_n = np.zeros((N, N))
G_norm = G_n
W_TRUE = W_norm * params.w_chem
G = G_norm * params.w_gap
G_rowsum = G.sum(axis=1)
support = (W_TRUE > 0)

mean_supp_normal = support[:, :N_normal].sum(axis=0).mean()
hub_supp_size = HUB_SUPP
print(f"  Normal neurons: {N_normal}, mean |supp| = {mean_supp_normal:.1f}")
print(f"  Hub neurons: {N_HUBS}, |supp| = {hub_supp_size}, latent rank = {LATENT_RANK}")

# Verify the latent rank empirically
W_hubs_true = np.stack([W_TRUE[hub_supports[h], N_normal + h] for h in range(N_HUBS)], axis=1)
# This won't work because each hub has a different support set. Use full columns:
W_hubs_full = W_TRUE[:, N_normal:]
u, s_true, _ = np.linalg.svd(W_hubs_full, full_matrices=False)
s2 = s_true**2; d_eff_emp = (s2.sum()**2) / (s2**2).sum()
print(f"  Empirical d_eff of hub weight columns: {d_eff_emp:.1f}")

# Pool stim protocol
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

def fit_independent(X, z, valid, j_range):
    """Standard per-neuron fit. Skips j where vj.sum() < |supp_j|+3."""
    W_hat = np.zeros((N,N))
    for j in j_range:
        sj = np.where(support[:,j])[0]
        if len(sj)==0: continue
        vj = valid[:,j]
        if vj.sum() < len(sj)+3: continue
        Xs = X[vj][:,sj]; zs = z[vj,j]
        A = Xs.T@Xs + 1e-3*np.eye(len(sj)); b = Xs.T@zs
        W_hat[sj,j] = np.clip(np.linalg.solve(A,b),0,None)
    return W_hat

def fit_multitask_lowrank(X, z, valid, hub_cols, rank, max_iter=20):
    """Multi-task low-rank fit for hub columns.

    Model: W[:, hub_cols] = B @ C, where B is N x rank, C is rank x n_hubs.
    Support-constrained: W[i, j] = 0 outside supp_j.

    Alternating least squares with support masks.
    """
    n_hubs = len(hub_cols)
    # Initialize: each hub's C column from a small independent fit if possible,
    # B from random
    rng_i = np.random.default_rng(0)
    B = rng_i.normal(0, 0.1, (N, rank))
    C = rng_i.normal(0, 0.1, (rank, n_hubs))
    # Restrict B rows: only rows that appear in any hub's support
    union_supp = np.zeros(N, dtype=bool)
    for j in hub_cols:
        union_supp |= support[:, j]
    B[~union_supp, :] = 0

    for it in range(max_iter):
        # Update C: for each hub j, solve z_j = X @ (B @ c_j) with support mask
        for h, j in enumerate(hub_cols):
            sj = np.where(support[:, j])[0]
            if len(sj) == 0: continue
            vj = valid[:, j]
            if vj.sum() < rank + 3: continue
            X_eff = X[vj][:, sj] @ B[sj, :]  # (n_valid, rank)
            z_eff = z[vj, j]
            A = X_eff.T @ X_eff + 1e-3 * np.eye(rank)
            b = X_eff.T @ z_eff
            C[:, h] = np.linalg.solve(A, b)
        # Update B: B[i, :] determines weights at presyn i across all hubs that include i
        # For each row i in union_supp, fit B[i, :] from columns j where i in supp_j
        for i in np.where(union_supp)[0]:
            # Hubs that include i in their support
            j_active = [h for h, j in enumerate(hub_cols) if support[i, j]]
            if len(j_active) < 2:  # need at least 2 constraints
                continue
            # z[..., j] = sum_{i' in supp_j} X[..., i'] * W[i', j]
            # The contribution from B[i, :] to z[..., j] is X[..., i] * (B[i, :] @ c_j)
            # Residual from other rows: z[t, j] - sum_{i' != i, i' in supp_j} X[t, i'] * (B[i', :] @ c_j)
            A_b = np.zeros((rank, rank))
            v_b = np.zeros(rank)
            for h in j_active:
                j = hub_cols[h]
                sj = np.where(support[:, j])[0]
                sj_other = sj[sj != i]
                vj = valid[:, j]
                if vj.sum() < 5: continue
                x_i = X[vj, i]
                if sj_other.size > 0:
                    w_other = B[sj_other, :] @ C[:, h]  # weights at other supp rows for hub h
                    z_resid = z[vj, j] - X[vj][:, sj_other] @ w_other
                else:
                    z_resid = z[vj, j]
                # Now: z_resid = x_i * (B[i, :] @ C[:, h])
                # i.e. z_resid = (C[:, h] outer x_i) -- but as scalar equation per t
                # Stack across t: (n_valid, rank) where each row is x_i[t] * C[:, h]
                # And target: z_resid
                X_b = x_i[:, np.newaxis] * C[:, h][np.newaxis, :]
                A_b += X_b.T @ X_b
                v_b += X_b.T @ z_resid
            A_b += 1e-3 * np.eye(rank)
            B[i, :] = np.linalg.solve(A_b, v_b)
            # Enforce non-negativity: project B@c_j to be non-negative isn't trivial;
            # instead, we'll just clip the final W after factorization

    # Construct final W_hat from B @ C
    W_hat = np.zeros((N, N))
    for h, j in enumerate(hub_cols):
        sj = np.where(support[:, j])[0]
        w_full = B[:, :] @ C[:, h]
        W_hat[sj, j] = np.clip(w_full[sj], 0, None)
    return W_hat

# Test: sweep K_pools
hub_cols = list(range(N_normal, N))
print(f"\nSweeping K_pools for hub recovery (independent vs multi-task)...")
print(f"{'K_pools':>8}  {'M':>4}  {'trials':>7}  {'Indep r_hub':>12}  {'Multi r_hub':>12}")
print("-"*55)

# We measure r_hub for the hub columns specifically.
# Independent fit's r_hub will be 0 if K < hub_supp, since it skips under-determined.
# Multi-task should work even at K small.
results = []
for K_pools in [50, 100, 200, 500]:
    M = 15
    n_trials = K_pools * len(AMPS) * N_REPS
    X, Xp, Ie = simulate_pool(K_pools, M)
    z, valid = get_z(X, Xp, Ie)
    # Independent
    W_ind = fit_independent(X, z, valid, hub_cols)
    # Multi-task with rank LATENT_RANK
    W_mt = fit_multitask_lowrank(X, z, valid, hub_cols, rank=LATENT_RANK, max_iter=15)
    # Compute r_hub for each
    r_hub_ind_list = []
    r_hub_mt_list = []
    for j in hub_cols:
        sj = np.where(support[:, j])[0]
        true_w = W_TRUE[sj, j]
        if true_w.std() < 1e-9: continue
        ind_w = W_ind[sj, j]
        mt_w = W_mt[sj, j]
        if ind_w.std() > 1e-9:
            r_hub_ind_list.append(pearsonr(true_w, ind_w)[0])
        if mt_w.std() > 1e-9:
            r_hub_mt_list.append(pearsonr(true_w, mt_w)[0])
    r_hub_ind = np.mean(r_hub_ind_list) if r_hub_ind_list else 0.0
    r_hub_mt = np.mean(r_hub_mt_list) if r_hub_mt_list else 0.0
    line = f"{K_pools:>8}  {M:>4}  {n_trials:>7}  {r_hub_ind:>12.4f}  {r_hub_mt:>12.4f}"
    print(line); results.append((K_pools, r_hub_ind, r_hub_mt))

print(f"\nSummary: |supp_hub| = {HUB_SUPP}, latent rank = {LATENT_RANK}")
print(f"  Independent fit needs K > {HUB_SUPP} per hub")
print(f"  Multi-task fit (rank={LATENT_RANK}) should work at K > {LATENT_RANK}+a-few")

with open("simulation/results/multitask_pool_stim.txt", "w", encoding="utf-8") as f:
    f.write("Multi-task pool stim test\n"+"="*45+"\n")
    f.write(f"|supp_hub| = {HUB_SUPP}, true latent rank = {LATENT_RANK}\n\n")
    f.write(f"{'K_pools':>8}  {'Indep r_hub':>12}  {'Multi r_hub':>12}\n")
    for K, ri, rm in results:
        f.write(f"{K:>8}  {ri:>12.4f}  {rm:>12.4f}\n")
print("\nSaved: simulation/results/multitask_pool_stim.txt")
