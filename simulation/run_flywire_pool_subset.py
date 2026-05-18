"""
Pool-stim pipeline test on a real Drosophila (FlyWire) subset.

Real biological data at intermediate scale (N~10^3-10^4). Tests:
  1. Can we extract a coherent subset (one neuropil or strongly-connected component)?
  2. Does pool stim recover its connectivity at Pearson r >> 0?
  3. Behavioral verification: pick "sensory" inputs (high-out-degree) and "motor"
     outputs, measure population trajectory under test stimuli.
"""
import os, sys, numpy as np, pandas as pd, time
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from simulation.rate_model import RateParams, simulate_rate
from scipy.stats import pearsonr

print("="*72); print("FLYWIRE INTERMEDIATE-SCALE POOL STIM"); print("="*72)

t0 = time.time()
print("Loading flywire...")
df = pd.read_feather('simulation/data/flywire_connections_783.feather')
print(f"  {len(df)} rows in {time.time()-t0:.1f}s")

# Filter to ONE neuropil. Mushroom body is a classic learning circuit with
# Kenyon cells (hubs) -- good test of the protocol on a real circuit.
# But neuropil names may vary; pick the most common one as a sample.
np_counts = df['neuropil'].value_counts()
print(f"\nTop neuropils by edge count:")
print(np_counts.head(8))

# Pick a small-ish neuropil with ~10^4 neurons
target_np = "MB_CA_R"  # Mushroom Body Calyx Right -- classic Kenyon cell area
if target_np not in np_counts.index:
    target_np = np_counts.index[3]  # fallback to 4th-largest
print(f"\nTargeting neuropil: {target_np}")

df_sub = df[df['neuropil'] == target_np][['pre_pt_root_id','post_pt_root_id','syn_count']]
df_sub = df_sub[df_sub['syn_count'] >= 3]
print(f"  Edges in {target_np}: {len(df_sub)}")

unique_neurons = pd.unique(df_sub[['pre_pt_root_id','post_pt_root_id']].values.ravel())
n2idx = {nid: i for i, nid in enumerate(unique_neurons)}
N = len(unique_neurons)
print(f"  Unique neurons: {N}")

# Build dense W (N x N) -- only feasible if N <= ~3000
N_CAP = int(os.environ.get('FLYWIRE_N_CAP', '800'))
if N > N_CAP:
    print(f"  N={N} too large; subsampling top {N_CAP} by total degree")
    deg_in = df_sub.groupby('post_pt_root_id').size()
    deg_out = df_sub.groupby('pre_pt_root_id').size()
    deg = deg_in.add(deg_out, fill_value=0)
    keep_ids = deg.nlargest(N_CAP).index.values
    keep_set = set(keep_ids.tolist())
    df_sub = df_sub[df_sub['pre_pt_root_id'].isin(keep_set) & df_sub['post_pt_root_id'].isin(keep_set)]
    unique_neurons = pd.unique(df_sub[['pre_pt_root_id','post_pt_root_id']].values.ravel())
    n2idx = {nid: i for i, nid in enumerate(unique_neurons)}
    N = len(unique_neurons)
    print(f"  Subsampled to N={N}")

W = np.zeros((N, N))
for _, row in df_sub.iterrows():
    pre_i = n2idx[row['pre_pt_root_id']]
    post_j = n2idx[row['post_pt_root_id']]
    W[pre_i, post_j] = row['syn_count']
print(f"  W density: {(W > 0).mean():.4f}, nonzeros: {(W>0).sum()}")

W_norm = W / W.max()
G_norm = np.zeros((N, N))

params = RateParams(tau=10.0, gain=2.5, w_chem=0.25, w_gap=0.1, dt=0.5)
W_TRUE = W_norm * params.w_chem
G = G_norm * params.w_gap
G_rowsum = G.sum(axis=1)
support = (W_TRUE > 0)
nz_mask = W_TRUE.flatten() > 1e-6

mean_supp = support.sum(axis=0).mean()
max_supp = support.sum(axis=0).max()
print(f"  Mean |supp|: {mean_supp:.1f}, max: {max_supp}")

# Pool stim setup
T_PROBE_ms = 300.0; T_probe = int(T_PROBE_ms/params.dt)
SS = (int(150.0/params.dt), int(280.0/params.dt)); SUB_SS = 2
EPS = 0.001; SAT_HI = 0.85; SAT_LO = 0.02
# Amplitude ladder: env-selectable. 'low' adds small amplitudes so mega-hubs
# stay out of saturation and remain observable.
_AMP_MODE = os.environ.get('FLYWIRE_AMPS', 'default')
if _AMP_MODE == 'low':
    AMPS = [0.05, 0.1, 0.2, 0.4, 0.8]   # spans into the unsaturated regime
else:
    AMPS = [0.4, 0.8, 1.5]
N_REPS = 3; NOISE = 0.01
ratio = params.tau/params.dt

M = max(15, int(mean_supp * 0.5))
# coverage multiplier from env (default 1.0 -> fast failing run for diagnostic)
COV = float(os.environ.get('FLYWIRE_COV', '1.0'))
K_pools = max(75, int(8 * mean_supp), int(np.ceil(COV * N / M)))
print(f"\nPool stim: K_pools = {K_pools}, M = {M}, total trials = {K_pools*len(AMPS)*N_REPS}")

t0 = time.time()
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
            R = R0 + rng.normal(0,NOISE,R0.shape); R = np.clip(R,0,1)
            ss = R[SS[0]:SS[1]:SUB_SS]; ssp = R[SS[0]+1:SS[1]+1:SUB_SS]
            x_acc+=ss.mean(0); xp_acc+=ssp.mean(0)
        X[k]=x_acc/N_REPS; Xp[k]=xp_acc/N_REPS; Ie[k]=I_k[SS[0]]; k+=1
print(f"  Simulation: {time.time()-t0:.1f}s")

t0 = time.time()
valid = Xp>EPS
targ = (Xp-X)*ratio + X
valid &= (targ>-0.95)&(targ<0.95)
x_safe = (X<SAT_HI)&(X>SAT_LO)|(X==0); valid &= x_safe
I_gap = X@G.T - X*G_rowsum[np.newaxis,:]
z = np.arctanh(np.clip(targ,-0.95,0.95))/params.gain - I_gap - Ie

W_hat = np.zeros((N,N))
skipped = 0
under_det = 0
skipped_idx = []
megahub_idx = []
for j in range(N):
    sj = np.where(support[:,j])[0]
    if len(sj)==0: continue
    if len(sj) > 500:
        megahub_idx.append(j)
    vj = valid[:,j]
    if vj.sum() < 5:   # too few observations even with strong ridge
        skipped += 1
        skipped_idx.append(j)
        continue
    if vj.sum() < len(sj)+3:
        under_det += 1
        ridge = 0.5  # STRONG ridge for under-determined hubs
    else:
        ridge = 1e-3
    Xs = X[vj][:,sj]; zs = z[vj,j]
    A = Xs.T@Xs + ridge*np.eye(len(sj)); b = Xs.T@zs
    W_hat[sj,j] = np.clip(np.linalg.solve(A,b),0,None)
print(f"  Under-determined neurons (strong ridge applied): {under_det}/{N}")
print(f"  Fit: {time.time()-t0:.1f}s, skipped (under-det): {skipped}/{N} neurons")
print(f"  Mega-hubs (|supp|>500): {len(megahub_idx)}")

pr = pearsonr(W_TRUE.flatten()[nz_mask], W_hat.flatten()[nz_mask])[0]
frob = np.linalg.norm(W_hat - W_TRUE)/np.linalg.norm(W_TRUE)
print(f"\nRecovery: Pearson r = {pr:.4f}, frob = {frob:.4f}")

# Behavioral test: pick 3 random "stimulation patterns" and compare trajectories
ws, we = int(100/params.dt), int(500/params.dt); T_test = 600.0
def cdiv(a,b):
    na,nb=np.linalg.norm(a),np.linalg.norm(b)
    return 1.0-np.dot(a,b)/(na*nb) if na>1e-10 and nb>1e-10 else 1.0

print(f"\nBehavioral verification (5 random test stimuli):")
Wn = np.clip(W_hat/params.w_chem, 0, None)
rng_t = np.random.default_rng(99)
divs = []
for t in range(5):
    stim_idx = rng_t.choice(N, size=10, replace=False)
    I_t = np.zeros((int(T_test/params.dt), N)); I_t[:, stim_idx] = 3.0
    r0 = simulate_rate(W_norm, G_norm, I_t, T_test, params)["r"][ws:we].flatten()
    rh = simulate_rate(Wn, G_norm, I_t, T_test, params)["r"][ws:we].flatten()
    d = cdiv(r0, rh)
    divs.append(d)
    print(f"  stim {t+1}: div = {d:.4f}  [{'PASS' if d<0.05 else 'FAIL'}]")
all_pass = all(d<0.05 for d in divs)
print(f"\n*** {'PASS' if all_pass else 'FAIL'} on real Drosophila subset (N={N}) ***")

# === DIAGNOSTIC: isolate the failure cause ===
if not all_pass:
    print(f"\n--- DIAGNOSTIC: isolating failure cause ---")
    def behav(W_test):
        Wn_t = np.clip(W_test/params.w_chem, 0, None)
        rng_d = np.random.default_rng(99)
        ds = []
        for t in range(5):
            stim_idx = rng_d.choice(N, size=10, replace=False)
            I_t = np.zeros((int(T_test/params.dt), N)); I_t[:, stim_idx] = 3.0
            r0 = simulate_rate(W_norm, G_norm, I_t, T_test, params)["r"][ws:we].flatten()
            rh = simulate_rate(Wn_t, G_norm, I_t, T_test, params)["r"][ws:we].flatten()
            ds.append(cdiv(r0, rh))
        return ds

    # (A) substitute W_TRUE for skipped columns
    W_fix_skip = W_hat.copy()
    for j in skipped_idx:
        W_fix_skip[:, j] = W_TRUE[:, j]
    d_skip = behav(W_fix_skip)
    print(f"  (A) W_TRUE for {len(skipped_idx)} skipped cols:  div_mean = {np.mean(d_skip):.4f}  "
          f"[{'PASS' if all(d<0.05 for d in d_skip) else 'FAIL'}]")

    # (B) substitute W_TRUE for mega-hub columns
    W_fix_hub = W_hat.copy()
    for j in megahub_idx:
        W_fix_hub[:, j] = W_TRUE[:, j]
    d_hub = behav(W_fix_hub)
    print(f"  (B) W_TRUE for {len(megahub_idx)} mega-hub cols:  div_mean = {np.mean(d_hub):.4f}  "
          f"[{'PASS' if all(d<0.05 for d in d_hub) else 'FAIL'}]")

    # (C) substitute W_TRUE for BOTH
    W_fix_both = W_hat.copy()
    for j in set(skipped_idx) | set(megahub_idx):
        W_fix_both[:, j] = W_TRUE[:, j]
    d_both = behav(W_fix_both)
    print(f"  (C) W_TRUE for skipped+megahub:        div_mean = {np.mean(d_both):.4f}  "
          f"[{'PASS' if all(d<0.05 for d in d_both) else 'FAIL'}]")

    with open("simulation/results/flywire_diagnostic.txt", "w", encoding="utf-8") as f:
        f.write(f"FlyWire N={N} failure diagnostic\n"+"="*45+"\n")
        f.write(f"Baseline div_mean: {np.mean(divs):.4f} (FAIL)\n")
        f.write(f"Skipped neurons: {len(skipped_idx)}, mega-hubs: {len(megahub_idx)}\n\n")
        f.write(f"(A) W_TRUE for skipped:        {np.mean(d_skip):.4f}  "
                f"{'PASS' if all(d<0.05 for d in d_skip) else 'FAIL'}\n")
        f.write(f"(B) W_TRUE for mega-hubs:      {np.mean(d_hub):.4f}  "
                f"{'PASS' if all(d<0.05 for d in d_hub) else 'FAIL'}\n")
        f.write(f"(C) W_TRUE for skipped+hubs:   {np.mean(d_both):.4f}  "
                f"{'PASS' if all(d<0.05 for d in d_both) else 'FAIL'}\n")
    print(f"  Saved: simulation/results/flywire_diagnostic.txt")

with open("simulation/results/flywire_pool_subset.txt", "w", encoding="utf-8") as f:
    f.write(f"Pool stim on FlyWire neuropil subset\n"+"="*55+"\n")
    f.write(f"Neuropil: {target_np}\nN: {N}, mean |supp|: {mean_supp:.1f}\n")
    f.write(f"K_pools: {K_pools}, M: {M}, total trials: {K_pools*len(AMPS)*N_REPS}\n")
    f.write(f"Skipped (under-determined): {skipped}/{N}\n")
    f.write(f"Pearson r = {pr:.4f}\n")
    f.write(f"Frob = {frob:.4f}\n\n")
    f.write(f"5 random test stimuli:\n")
    for i, d in enumerate(divs):
        f.write(f"  stim {i+1}: div = {d:.4f}  [{'PASS' if d<0.05 else 'FAIL'}]\n")
    f.write(f"\nOverall: {'PASS' if all_pass else 'FAIL'}\n")
print(f"\nSaved: simulation/results/flywire_pool_subset.txt")
