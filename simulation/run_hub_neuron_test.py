"""
Hub-neuron stress test.

Build a synthetic network with one Purkinje-like neuron receiving
|supp| = 500 inputs (where N=300 mean is 12). K_pools = 100 (much less
than |supp_hub|). Does pool stim recover the hub neuron's weights?

The rate-distortion conjecture: d_eff(hub's input vector) << |supp_hub|,
so the regression is under-determined in raw rank but well-determined
in functional rank. We test by:
  - Recovery quality on the hub specifically (vs other neurons)
  - Functional output (does the hub still fire correctly?)

If pool stim handles this, the human-scale scaling is robust to hubs.
"""
import os, sys, numpy as np
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from simulation.rate_model import RateParams, simulate_rate
from scipy.stats import pearsonr

print("="*72); print("HUB-NEURON STRESS TEST"); print("="*72)
params = RateParams(tau=10.0, gain=2.5, w_chem=0.25, w_gap=0.1, dt=0.5)

# Build a network with N=400; first 300 are 'normal' (mean |supp|~12);
# last 1 is a 'Purkinje' hub with |supp|=200 (66% of normal network).
N = 400
rng = np.random.default_rng(0)
p_chem = 0.04
W = np.zeros((N, N))
W_mask = (rng.random((N-1, N-1)) < p_chem) & ~np.eye(N-1, dtype=bool)
W[:N-1, :N-1][W_mask] = rng.lognormal(-2.0, 1.0, W_mask.sum())
# Hub neuron at index N-1 (399): connect from 200 random pre-syn neurons
hub_pre = rng.choice(N-1, size=200, replace=False)
hub_weights = rng.lognormal(-2.0, 1.0, 200) * 0.5  # smaller per-synapse weights
W[hub_pre, N-1] = hub_weights
# Hub projects out to 5 downstream neurons
hub_post = rng.choice(N-1, size=5, replace=False)
W[N-1, hub_post] = rng.lognormal(-1.0, 0.5, 5)
W_norm = W / W.max()

# Gap junctions (none for hub neuron)
G_mask = (rng.random((N, N)) < 0.02)
G_mask = G_mask | G_mask.T; np.fill_diagonal(G_mask, False)
G_mask[N-1, :] = False; G_mask[:, N-1] = False
G_n = np.zeros((N, N)); G_n[G_mask] = rng.lognormal(-2.0, 0.5, G_mask.sum())
G_norm = G_n / (G_n.max() or 1.0)

W_TRUE = W_norm * params.w_chem
G = G_norm * params.w_gap
G_rowsum = G.sum(axis=1)
support = (W_TRUE > 0)
hub_supp_size = support[:, N-1].sum()
mean_supp = support[:, :N-1].sum(axis=0).mean()
print(f"  Normal neurons: N-1 = {N-1}, mean |supp| = {mean_supp:.1f}")
print(f"  Hub neuron (idx {N-1}): |supp| = {hub_supp_size}  (16x the mean!)")

# Pool stim protocol
T_PROBE_ms = 300.0; T_probe = int(T_PROBE_ms/params.dt)
SS = (int(150.0/params.dt), int(280.0/params.dt)); SUB_SS = 2
EPS = 0.001; SAT_HI = 0.85; SAT_LO = 0.02
AMPS = [0.4, 0.8, 1.5]; N_REPS = 10
ratio = params.tau/params.dt

def run(K_pools, M, noise):
    rng = np.random.default_rng(42)
    K_total = K_pools*len(AMPS)
    X = np.zeros((K_total,N)); Xp = np.zeros((K_total,N)); Ie = np.zeros((K_total,N))
    k=0
    for p in range(K_pools):
        pool = rng.choice(N, size=M, replace=False)
        for amp in AMPS:
            I_k = np.zeros((T_probe,N)); I_k[:,pool]=amp
            R0 = simulate_rate(W_norm, G_norm, I_k, T_PROBE_ms, params)["r"]
            x_acc=np.zeros(N); xp_acc=np.zeros(N)
            for _ in range(N_REPS):
                R = R0 + rng.normal(0,noise,R0.shape); R = np.clip(R,0,1)
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
    for j in range(N):
        sj = np.where(support[:,j])[0]
        if len(sj)==0: continue
        vj = valid[:,j]
        if vj.sum() < len(sj)+3: continue
        Xs = X[vj][:,sj]; zs = z[vj,j]
        A = Xs.T@Xs + 1e-3*np.eye(len(sj)); b = Xs.T@zs
        W_hat[sj,j] = np.clip(np.linalg.solve(A,b),0,None)
    return W_hat

# Try a few K_pools values, including some BELOW |supp_hub|
configs = [
    ("K=50 << hub|supp|=200", 50, 25),
    ("K=100 << hub|supp|=200", 100, 30),
    ("K=200 = hub|supp|=200", 200, 30),
    ("K=400 > hub|supp|=200", 400, 30),
]

print(f"\n{'config':>25}  {'r_full':>8}  {'r_normal':>9}  {'r_hub':>8}  hub_pass")
print("-"*65)
W_TRUE_flat = W_TRUE.flatten()
nz_mask = W_TRUE_flat > 1e-6
hub_col = N - 1
hub_nz_mask = W_TRUE[:, hub_col] > 1e-6
results = []
for desc, K, M in configs:
    W_hat = run(K, M, 0.01)
    r_full = pearsonr(W_TRUE_flat[nz_mask], W_hat.flatten()[nz_mask])[0]
    # Pearson for normal neurons (exclude hub column)
    normal_mask = nz_mask.reshape(N,N).copy(); normal_mask[:, hub_col] = False
    r_normal = pearsonr(W_TRUE[normal_mask], W_hat[normal_mask])[0] if normal_mask.sum() > 10 else 0
    # Pearson for the hub column specifically
    r_hub = pearsonr(W_TRUE[hub_nz_mask, hub_col], W_hat[hub_nz_mask, hub_col])[0] if hub_nz_mask.sum() > 10 else 0
    # Functional test: stimulate one of the hub's downstream targets, see if response matches
    hub_post_first = np.where(W_TRUE[hub_col, :] > 0)[0]
    if len(hub_post_first) > 0:
        # Stim 5 random presyn to hub at moderate amp, measure response of hub downstream
        I_t = np.zeros((int(300/params.dt), N))
        hub_input_test = rng.choice(hub_pre, size=20, replace=False)
        I_t[:, hub_input_test] = 1.5
        Wn = np.clip(W_hat/params.w_chem, 0, None)
        r_true = simulate_rate(W_norm, G_norm, I_t, 300.0, params)["r"][100:].flatten()
        r_recon = simulate_rate(Wn, G_norm, I_t, 300.0, params)["r"][100:].flatten()
        div_full = 1.0 - np.dot(r_true,r_recon)/(np.linalg.norm(r_true)*np.linalg.norm(r_recon))
    else:
        div_full = 1.0
    hub_pass = "PASS" if div_full < 0.05 else "FAIL"
    print(f"{desc:>25}  {r_full:>8.3f}  {r_normal:>9.3f}  {r_hub:>8.3f}  {hub_pass} (div={div_full:.4f})")
    results.append((desc, K, r_full, r_normal, r_hub, div_full))

print(f"\nKey question: does Pearson r_hub stay high when K < |supp_hub|?")
print(f"Answer: K=50, r_hub = {results[0][4]:.3f}; K=200, r_hub = {results[2][4]:.3f}")
if results[0][4] > 0.5 and results[0][5] < 0.05:
    print(f"\n=> Hub recovery WORKS even with K < |supp_hub|.")
    print(f"   Rate-distortion conjecture confirmed: d_eff(hub) << |supp_hub|.")
    print(f"   Human-scale Purkinje scaling is fine.")
else:
    print(f"\n=> Hub recovery FAILS at K < |supp_hub|.")
    print(f"   Need additional priors / sparse regularization for human-scale hubs.")

with open("simulation/results/hub_neuron_test.txt","w",encoding="utf-8") as f:
    f.write("Hub-neuron stress test\n"+"="*45+"\n")
    f.write(f"Hub neuron has |supp| = {hub_supp_size}, vs mean = {mean_supp:.1f}\n\n")
    f.write(f"{'config':>25}  {'r_full':>8}  {'r_normal':>9}  {'r_hub':>8}  div_hub\n")
    for desc, K, rf, rn, rh, dh in results:
        f.write(f"{desc:>25}  {rf:>8.3f}  {rn:>9.3f}  {rh:>8.3f}  {dh:>8.4f}\n")
print("\nSaved: simulation/results/hub_neuron_test.txt")
