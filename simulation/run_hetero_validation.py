"""
Validate the heterogeneous-excitability model on C. elegans.

Must-pass check (math/direction1_heterogeneous_model.md validation plan
step 2): the heterogeneous model + homeostatic calibration must still
recover the C. elegans connectome at Pearson ~0.99 and pass behavioral
verification. If it does not, the calibration is wrong.
"""
import os, sys, numpy as np
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from simulation.load_connectome import load_connectome, load_gap_junctions
from simulation.rate_model import (RateParams, simulate_rate_hetero,
                                    calibrate_homeostatic, make_tap_input,
                                    make_chem_input)
from scipy.stats import pearsonr

print("="*72); print("HETEROGENEOUS MODEL VALIDATION -- C. elegans"); print("="*72)

W_raw, neurons, W_norm = load_connectome()
G_raw, g_neurons = load_gap_junctions()
N = len(neurons)
g_idx = {n:i for i,n in enumerate(g_neurons)}; g_set = set(g_neurons)
G_aligned = np.zeros((N, N))
for i, ni in enumerate(neurons):
    for j, nj in enumerate(neurons):
        if ni in g_set and nj in g_set:
            G_aligned[i,j] = G_raw[g_idx[ni], g_idx[nj]]
G_norm = G_aligned/(G_aligned.max() or 1.0)

params = RateParams(tau=10.0, gain=2.5, w_chem=0.25, w_gap=0.1, dt=0.5)
W_TRUE = W_norm*params.w_chem
G = G_norm*params.w_gap
G_rowsum = G.sum(axis=1)
support = (W_TRUE>0); nz_mask = W_TRUE.flatten()>1e-6

T_PROBE_ms = 300.0; T_probe = int(T_PROBE_ms/params.dt)
SS = (int(150/params.dt), int(280/params.dt)); SUB_SS = 2
EPS = 0.001; SAT_HI = 0.85; SAT_LO = 0.02
AMPS = [0.4, 0.8, 1.5]; N_REPS = 10; NOISE = 0.01
ratio = params.tau/params.dt
M = 15; K_POOLS = 100

# Reference ensemble for calibration: 20 random pools
rng = np.random.default_rng(7)
ref_inputs = []
for _ in range(20):
    pool = rng.choice(N, size=M, replace=False)
    I_r = np.zeros((T_probe, N)); I_r[:, pool] = 0.8
    ref_inputs.append(I_r)

print("Calibrating homeostatic gain/theta...")
gain_vec, theta_vec = calibrate_homeostatic(W_norm, G_norm, params, ref_inputs,
                                             c=1.5, n_rounds=5)
print(f"  gain_i:  mean={gain_vec.mean():.3f}, range=[{gain_vec.min():.3f}, {gain_vec.max():.3f}]")
print(f"  theta_i: mean={theta_vec.mean():.3f}, range=[{theta_vec.min():.3f}, {theta_vec.max():.3f}]")

# Pool stim with the heterogeneous model
print(f"\nPool stim (K={K_POOLS}, M={M}) with heterogeneous model...")
rng2 = np.random.default_rng(42)
K_total = K_POOLS*len(AMPS)
X = np.zeros((K_total,N)); Xp = np.zeros((K_total,N)); Ie = np.zeros((K_total,N))
k=0
for p in range(K_POOLS):
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

# Regression: per-neuron gain/theta
# z_j = arctanh(targ)/gain_j + theta_j - I_gap_j - I_ext_j = sum_i W_ij r_i
valid = Xp>EPS
targ = (Xp-X)*ratio + X
valid &= (targ>-0.95)&(targ<0.95)
x_safe = (X<SAT_HI)&(X>SAT_LO)|(X==0); valid &= x_safe
I_gap = X@G.T - X*G_rowsum[np.newaxis,:]
z = (np.arctanh(np.clip(targ,-0.95,0.95)) / gain_vec[np.newaxis,:]
     + theta_vec[np.newaxis,:] - I_gap - Ie)

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
print(f"  skipped: {skipped}/{N}")
print(f"  Pearson r = {pr:.4f}")

# Behavioral verification with the heterogeneous model
ws, we = int(100/params.dt), int(500/params.dt); T_test = 600.0
def cdiv(a,b):
    na,nb=np.linalg.norm(a),np.linalg.norm(b)
    return 1.0-np.dot(a,b)/(na*nb) if na>1e-10 and nb>1e-10 else 1.0

tests = {}
I = make_tap_input(N, neurons, T_test, params.dt, 50.0, 30.0, 4.0)
tests["tap"] = I
I = make_chem_input(N, neurons, T_test, params.dt, 3.0)
tests["chem"] = I

print(f"\nBehavioral verification (heterogeneous model):")
all_pass = True
for name, I_t in tests.items():
    r0 = simulate_rate_hetero(W_norm, G_norm, I_t, T_test, params,
                               gain_vec, theta_vec)["r"][ws:we].flatten()
    rh = simulate_rate_hetero(np.clip(W_hat/params.w_chem,0,None), G_norm, I_t,
                               T_test, params, gain_vec, theta_vec)["r"][ws:we].flatten()
    d = cdiv(r0, rh)
    p = d < 0.05; all_pass = all_pass and p
    print(f"  {name:>6}: div = {d:.4f}  [{'PASS' if p else 'FAIL'}]")

print(f"\n{'='*72}")
verdict = "PASS" if (pr > 0.9 and all_pass) else "FAIL"
print(f"VALIDATION {verdict}: heterogeneous model "
      f"{'reproduces' if verdict=='PASS' else 'does NOT reproduce'} the C. elegans result")
if verdict == "PASS":
    print("=> Heterogeneous model validated. Ready to re-test FlyWire.")
else:
    print(f"=> Pearson {pr:.3f} (need >0.9), behavioral {'PASS' if all_pass else 'FAIL'}.")
    print("   Calibration or regression needs debugging before FlyWire test.")

with open("simulation/results/hetero_validation.txt", "w", encoding="utf-8") as f:
    f.write("Heterogeneous model validation -- C. elegans\n"+"="*50+"\n")
    f.write(f"gain_i:  mean={gain_vec.mean():.3f} range=[{gain_vec.min():.3f},{gain_vec.max():.3f}]\n")
    f.write(f"theta_i: mean={theta_vec.mean():.3f} range=[{theta_vec.min():.3f},{theta_vec.max():.3f}]\n")
    f.write(f"skipped: {skipped}/{N}\n")
    f.write(f"Pearson r = {pr:.4f}\n")
    f.write(f"Verdict: {verdict}\n")
print("\nSaved: simulation/results/hetero_validation.txt")
