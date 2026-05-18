"""
FlyWire pool-stim with the HETEROGENEOUS-excitability model.

The uniform rate model failed on FlyWire: real synapse weights span 3.4
orders of magnitude and no global normalization keeps weak + strong
synapses both observable (direction1_density_limitation.md).

The heterogeneous model (per-neuron gain/theta, response-matching
homeostatic calibration) validated on C. elegans at Pearson 0.975.
This script tests whether it resolves the FlyWire failure.

Env: FLYWIRE_N_CAP (default 2000), FLYWIRE_NORM (default 'max').
"""
import os, sys, numpy as np, pandas as pd, time
import scipy.sparse as sp
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from simulation.rate_model import (RateParams, simulate_rate_hetero,
                                    calibrate_homeostatic)
from scipy.stats import pearsonr

N_CAP = int(os.environ.get('FLYWIRE_N_CAP', '2000'))
NORM = os.environ.get('FLYWIRE_NORM', 'max')
print("="*72); print(f"FLYWIRE HETEROGENEOUS-MODEL POOL STIM (N_CAP={N_CAP})"); print("="*72)

t0 = time.time()
df = pd.read_feather('simulation/data/flywire_connections_783.feather')
df_e = df[df['syn_count'] >= 3][['pre_pt_root_id','post_pt_root_id','syn_count']]
deg = df_e.groupby('post_pt_root_id').size().add(
      df_e.groupby('pre_pt_root_id').size(), fill_value=0)
keep = set(deg.nlargest(N_CAP).index.tolist())
df_e = df_e[df_e['pre_pt_root_id'].isin(keep) & df_e['post_pt_root_id'].isin(keep)]
ids = pd.unique(df_e[['pre_pt_root_id','post_pt_root_id']].values.ravel())
n2i = {nid:i for i,nid in enumerate(ids)}
N = len(ids)
pre = df_e['pre_pt_root_id'].map(n2i).values
post = df_e['post_pt_root_id'].map(n2i).values
wts = df_e['syn_count'].values.astype(float)
W = sp.csr_matrix((wts, (pre, post)), shape=(N, N))
denom = {'p99': np.percentile(wts,99), 'p995': np.percentile(wts,99.5)}.get(NORM, W.max())
W_norm = W / denom
G_norm = sp.csr_matrix((N, N))
print(f"  N={N}, edges={len(df_e)}, weight-norm={NORM} (denom={denom:.1f}), loaded {time.time()-t0:.1f}s")

params = RateParams(tau=10.0, gain=2.5, w_chem=0.25, w_gap=0.1, dt=0.5)
W_TRUE = (W_norm * params.w_chem).toarray()
support = (W_TRUE > 0); nz_mask = W_TRUE.flatten() > 1e-6
indeg = support.sum(axis=0)
print(f"  mean |supp|={indeg.mean():.1f}, max={indeg.max()}")

T_PROBE_ms = 300.0; T_probe = int(T_PROBE_ms/params.dt)
SS = (int(150/params.dt), int(280/params.dt)); SUB_SS = 2
EPS = 0.001; SAT_HI = 0.85; SAT_LO = 0.02
AMPS = [0.15, 0.4, 0.8, 1.5]   # heterogeneous model handles saturation via
                                # calibration, so the very-low 0.05 isn't needed
N_REPS = int(os.environ.get('FLYWIRE_REPS', '10'))
NOISE = 0.01
ratio = params.tau/params.dt
M = 15
K_pools = max(75, int(np.ceil(3.0 * N / M)))

# Calibrate the heterogeneous model on a reference ensemble
print("Calibrating heterogeneous model...")
t0 = time.time()
rng = np.random.default_rng(7)
ref = []
for _ in range(24):
    pool = rng.choice(N, size=M, replace=False)
    # calibration ensemble must match the probe-amplitude range, else
    # neurons calibrated for a gentle ensemble saturate under the real probe
    amp = rng.choice(AMPS)
    I_r = np.zeros((T_probe, N)); I_r[:, pool] = amp
    ref.append(I_r)
gain_vec, theta_vec = calibrate_homeostatic(W_norm, G_norm, params, ref, n_rounds=8)
print(f"  gain: mean={gain_vec.mean():.2f} range=[{gain_vec.min():.2f},{gain_vec.max():.2f}]")
print(f"  calibration: {time.time()-t0:.1f}s")

# Pool stim
print(f"Pool stim K={K_pools}, M={M}, mixed amps, {K_pools*len(AMPS)*N_REPS} trials...")
t0 = time.time()
rng2 = np.random.default_rng(42)
K_total = K_pools*len(AMPS)
X = np.zeros((K_total,N)); Xp = np.zeros((K_total,N)); Ie = np.zeros((K_total,N))
k=0
for p in range(K_pools):
    pool = rng2.choice(N, size=M, replace=False)
    for amp in AMPS:
        I_k = np.zeros((T_probe,N)); I_k[:,pool]=amp
        R0 = simulate_rate_hetero(W_norm, G_norm, I_k, T_PROBE_ms, params,
                                   gain_vec, theta_vec)["r"]
        x_acc=np.zeros(N); xp_acc=np.zeros(N)
        for _ in range(N_REPS):
            R = R0 + rng2.normal(0,NOISE,R0.shape); R = np.clip(R,0,1)
            ss = R[SS[0]:SS[1]:SUB_SS]; ssp = R[SS[0]+1:SS[1]+1:SUB_SS]
            x_acc+=ss.mean(0); xp_acc+=ssp.mean(0)
        X[k]=x_acc/N_REPS; Xp[k]=xp_acc/N_REPS; Ie[k]=I_k[SS[0]]; k+=1
print(f"  simulation: {time.time()-t0:.1f}s")

# Regression with per-neuron gain/theta (no gap junctions: I_gap = 0)
valid = Xp>EPS
targ = (Xp-X)*ratio + X
valid &= (targ>-0.95)&(targ<0.95)
x_safe = (X<SAT_HI)&(X>SAT_LO)|(X==0); valid &= x_safe
z = (np.arctanh(np.clip(targ,-0.95,0.95)) / gain_vec[np.newaxis,:]
     + theta_vec[np.newaxis,:] - Ie)
W_hat = np.zeros((N,N))
skipped = 0; skipped_idx = []
for j in range(N):
    sj = np.where(support[:,j])[0]
    if len(sj)==0: continue
    vj = valid[:,j]
    if vj.sum() < 5: skipped += 1; skipped_idx.append(j); continue
    ridge = 0.5 if vj.sum() < len(sj)+3 else 1e-3
    Xs = X[vj][:,sj]; zs = z[vj,j]
    A = Xs.T@Xs + ridge*np.eye(len(sj)); b = Xs.T@zs
    W_hat[sj,j] = np.clip(np.linalg.solve(A,b),0,None)
pr = pearsonr(W_TRUE.flatten()[nz_mask], W_hat.flatten()[nz_mask])[0]
print(f"  skipped: {skipped}/{N}, Pearson r = {pr:.4f}")

# Behavioral verification
ws, we = int(100/params.dt), int(500/params.dt); T_test = 600.0
def cdiv(a,b):
    na,nb=np.linalg.norm(a),np.linalg.norm(b)
    return 1.0-np.dot(a,b)/(na*nb) if na>1e-10 and nb>1e-10 else 1.0
W_hat_sp = sp.csr_matrix(np.clip(W_hat/params.w_chem,0,None))
print(f"\nBehavioral verification (heterogeneous model, 5 stimuli):")
rng_t = np.random.default_rng(99)
divs = []
for t in range(5):
    stim = rng_t.choice(N, size=10, replace=False)
    I_t = np.zeros((int(T_test/params.dt), N)); I_t[:, stim] = 3.0
    r0 = simulate_rate_hetero(W_norm, G_norm, I_t, T_test, params, gain_vec, theta_vec)["r"][ws:we].flatten()
    rh = simulate_rate_hetero(W_hat_sp, G_norm, I_t, T_test, params, gain_vec, theta_vec)["r"][ws:we].flatten()
    d = cdiv(r0, rh); divs.append(d)
    print(f"  stim {t+1}: div = {d:.4f}  [{'PASS' if d<0.05 else 'FAIL'}]")
all_pass = all(d<0.05 for d in divs)
print(f"\n*** {'PASS' if all_pass else 'FAIL'} on FlyWire N={N} (heterogeneous model) ***")

# Diagnostic: is the residual divergence the skipped neurons?
if not all_pass and skipped_idx:
    W_fix = np.clip(W_hat/params.w_chem, 0, None)
    for j in skipped_idx:
        W_fix[:, j] = W_TRUE[:, j] / params.w_chem
    W_fix_sp = sp.csr_matrix(W_fix)
    rng_d = np.random.default_rng(99)
    dd = []
    for t in range(5):
        stim = rng_d.choice(N, size=10, replace=False)
        I_t = np.zeros((int(T_test/params.dt), N)); I_t[:, stim] = 3.0
        r0 = simulate_rate_hetero(W_norm, G_norm, I_t, T_test, params, gain_vec, theta_vec)["r"][ws:we].flatten()
        rh = simulate_rate_hetero(W_fix_sp, G_norm, I_t, T_test, params, gain_vec, theta_vec)["r"][ws:we].flatten()
        dd.append(cdiv(r0, rh))
    print(f"  DIAGNOSTIC: W_TRUE for {len(skipped_idx)} skipped cols -> "
          f"div_mean {np.mean(dd):.4f} [{'PASS' if all(d<0.05 for d in dd) else 'FAIL'}]")

with open("simulation/results/flywire_hetero.txt","w",encoding="utf-8") as f:
    f.write(f"FlyWire heterogeneous-model pool stim, N={N}\n"+"="*50+"\n")
    f.write(f"mean|supp|={indeg.mean():.1f} max={indeg.max()}, norm={NORM}\n")
    f.write(f"gain mean={gain_vec.mean():.2f}, K={K_pools}, skipped={skipped}\n")
    f.write(f"Pearson r = {pr:.4f}\n\n")
    for i,d in enumerate(divs):
        f.write(f"  stim {i+1}: div={d:.4f} [{'PASS' if d<0.05 else 'FAIL'}]\n")
    f.write(f"\nVerdict: {'PASS' if all_pass else 'FAIL'}\n")
print("Saved: simulation/results/flywire_hetero.txt")
