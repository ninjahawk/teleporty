"""
Flywire pool-stim at larger scale, using the sparse simulator.

With simulate_rate_sparse the per-trial cost drops ~65-375x, making
N=5000-10000 connectome simulations tractable. This validates the
mega-hub fix (mixed amplitude + coverage) at the next scale up.

Env: FLYWIRE_N_CAP (default 5000)
"""
import os, sys, numpy as np, pandas as pd, time
import scipy.sparse as sp
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from simulation.rate_model import RateParams, simulate_rate_sparse
from scipy.stats import pearsonr

N_CAP = int(os.environ.get('FLYWIRE_N_CAP', '5000'))
print("="*72); print(f"FLYWIRE SPARSE POOL STIM (N_CAP={N_CAP})"); print("="*72)

t0 = time.time()
df = pd.read_feather('simulation/data/flywire_connections_783.feather')
print(f"  loaded {len(df)} rows in {time.time()-t0:.1f}s")

# Use the whole connectome's top-N by degree (not just one neuropil) so we
# get a genuinely large hub-containing network.
df_e = df[df['syn_count'] >= 3][['pre_pt_root_id','post_pt_root_id','syn_count']]
deg_in = df_e.groupby('post_pt_root_id').size()
deg_out = df_e.groupby('pre_pt_root_id').size()
deg = deg_in.add(deg_out, fill_value=0)
keep = set(deg.nlargest(N_CAP).index.tolist())
df_e = df_e[df_e['pre_pt_root_id'].isin(keep) & df_e['post_pt_root_id'].isin(keep)]
ids = pd.unique(df_e[['pre_pt_root_id','post_pt_root_id']].values.ravel())
n2i = {nid: i for i, nid in enumerate(ids)}
N = len(ids)
print(f"  N = {N}, edges = {len(df_e)}")

# Sparse W construction (vectorized)
pre = df_e['pre_pt_root_id'].map(n2i).values
post = df_e['post_pt_root_id'].map(n2i).values
wts = df_e['syn_count'].values.astype(float)
W = sp.csr_matrix((wts, (pre, post)), shape=(N, N))
W_norm = W / W.max()
G_norm = sp.csr_matrix((N, N))

params = RateParams(tau=10.0, gain=2.5, w_chem=0.25, w_gap=0.1, dt=0.5)
W_TRUE = (W_norm * params.w_chem).toarray()   # dense for regression bookkeeping
support = (W_TRUE > 0)
nz_mask = W_TRUE.flatten() > 1e-6
indeg = support.sum(axis=0)
print(f"  mean |supp| = {indeg.mean():.1f}, max = {indeg.max()}, "
      f"density = {len(df_e)/N/N:.5f}")

T_PROBE_ms = 300.0; T_probe = int(T_PROBE_ms/params.dt)
SS = (int(150/params.dt), int(280/params.dt)); SUB_SS = 2
EPS = 0.001; SAT_HI = 0.85; SAT_LO = 0.02
AMPS = [0.05, 0.15, 0.4, 0.8, 1.5]   # mixed ladder
N_REPS = 3; NOISE = 0.01
ratio = params.tau/params.dt
M = 15
K_pools = max(75, int(np.ceil(3.0 * N / M)))   # K*M/N >= 3 coverage
print(f"  Pool stim: K={K_pools}, M={M}, mixed amps, total trials = "
      f"{K_pools*len(AMPS)*N_REPS}")

# G_rowsum is zero (no gap junctions here)
t0 = time.time()
rng = np.random.default_rng(42)
K_total = K_pools*len(AMPS)
X = np.zeros((K_total,N)); Xp = np.zeros((K_total,N)); Ie = np.zeros((K_total,N))
k=0
for p in range(K_pools):
    pool = rng.choice(N, size=M, replace=False)
    for amp in AMPS:
        I_k = np.zeros((T_probe,N)); I_k[:,pool]=amp
        R0 = simulate_rate_sparse(W_norm, G_norm, I_k, T_PROBE_ms, params)["r"]
        x_acc=np.zeros(N); xp_acc=np.zeros(N)
        for _ in range(N_REPS):
            R = R0 + rng.normal(0,NOISE,R0.shape); R = np.clip(R,0,1)
            ss = R[SS[0]:SS[1]:SUB_SS]; ssp = R[SS[0]+1:SS[1]+1:SUB_SS]
            x_acc+=ss.mean(0); xp_acc+=ssp.mean(0)
        X[k]=x_acc/N_REPS; Xp[k]=xp_acc/N_REPS; Ie[k]=I_k[SS[0]]; k+=1
print(f"  Simulation: {time.time()-t0:.1f}s")

# Fit
t0 = time.time()
valid = Xp>EPS
targ = (Xp-X)*ratio + X
valid &= (targ>-0.95)&(targ<0.95)
x_safe = (X<SAT_HI)&(X>SAT_LO)|(X==0); valid &= x_safe
# I_gap = 0 (no gap junctions)
z = np.arctanh(np.clip(targ,-0.95,0.95))/params.gain - Ie
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
print(f"  Fit: {time.time()-t0:.1f}s, skipped: {skipped}/{N}")

pr = pearsonr(W_TRUE.flatten()[nz_mask], W_hat.flatten()[nz_mask])[0]
print(f"  Pearson r = {pr:.4f}")

# Behavioral verification
ws, we = int(100/params.dt), int(500/params.dt); T_test = 600.0
def cdiv(a,b):
    na,nb=np.linalg.norm(a),np.linalg.norm(b)
    return 1.0-np.dot(a,b)/(na*nb) if na>1e-10 and nb>1e-10 else 1.0
W_hat_sp = sp.csr_matrix(W_hat / params.w_chem)
print(f"\nBehavioral verification (5 random test stimuli):")
rng_t = np.random.default_rng(99)
divs = []
for t in range(5):
    stim = rng_t.choice(N, size=10, replace=False)
    I_t = np.zeros((int(T_test/params.dt), N)); I_t[:, stim] = 3.0
    r0 = simulate_rate_sparse(W_norm, G_norm, I_t, T_test, params)["r"][ws:we].flatten()
    rh = simulate_rate_sparse(W_hat_sp, G_norm, I_t, T_test, params)["r"][ws:we].flatten()
    d = cdiv(r0, rh); divs.append(d)
    print(f"  stim {t+1}: div = {d:.4f}  [{'PASS' if d<0.05 else 'FAIL'}]")
all_pass = all(d<0.05 for d in divs)
print(f"\n*** {'PASS' if all_pass else 'FAIL'} on FlyWire N={N} (sparse simulator) ***")

with open("simulation/results/flywire_sparse.txt", "w", encoding="utf-8") as f:
    f.write(f"FlyWire sparse pool stim, N={N}\n"+"="*45+"\n")
    f.write(f"mean |supp|={indeg.mean():.1f}, max={indeg.max()}\n")
    f.write(f"K={K_pools}, M={M}, mixed amps, skipped={skipped}\n")
    f.write(f"Pearson r = {pr:.4f}\n\n")
    for i, d in enumerate(divs):
        f.write(f"  stim {i+1}: div={d:.4f} [{'PASS' if d<0.05 else 'FAIL'}]\n")
    f.write(f"\nVerdict: {'PASS' if all_pass else 'FAIL'}\n")
print("Saved: simulation/results/flywire_sparse.txt")
