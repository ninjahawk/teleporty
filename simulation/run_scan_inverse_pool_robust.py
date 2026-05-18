"""
Pool-based scan inverse -- robustness check.

Test the K=100, M=15 config (best from run_scan_inverse_pool.py) across:
  - 5 seeds
  - 3 noise levels (0.5%, 1%, 2%)

Single-seed result was r=0.99. Need to confirm it's not a lucky seed.
"""
import os, sys, numpy as np
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from simulation.load_connectome import load_connectome, load_gap_junctions
from simulation.rate_model import RateParams, simulate_rate, make_tap_input, make_chem_input
from scipy.stats import pearsonr

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
W_TRUE = W_norm*params.w_chem; G = G_norm*params.w_gap
G_rowsum = G.sum(axis=1); support = (W_TRUE>0); nz_mask = W_TRUE.flatten()>1e-6

T_PROBE_ms = 300.0; T_probe = int(T_PROBE_ms/params.dt)
SS = (int(150.0/params.dt), int(280.0/params.dt)); SUB_SS = 2
EPS = 0.001; SAT_HI = 0.85; SAT_LO = 0.02
AMPS = [0.4, 0.8, 1.5]; N_REPS = 10
ratio = params.tau/params.dt

def build_and_fit(K_pools, M_pool, noise, seed):
    rng = np.random.default_rng(seed)
    K_total = K_pools*len(AMPS)
    X = np.zeros((K_total,N)); Xp = np.zeros((K_total,N)); Ie = np.zeros((K_total,N))
    k=0
    for p in range(K_pools):
        pool = rng.choice(N, size=M_pool, replace=False)
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

ws, we = int(100/params.dt), int(500/params.dt); T_test = 600.0
def cdiv(a,b):
    na,nb=np.linalg.norm(a),np.linalg.norm(b)
    return 1.0-np.dot(a,b)/(na*nb) if na>1e-10 and nb>1e-10 else 1.0

test_stims = {}
I = make_tap_input(N,neurons,T_test,params.dt,50.0,30.0,4.0)
test_stims["tap"] = (I, simulate_rate(W_norm,G_norm,I,T_test,params)["r"][ws:we].flatten())
I = make_chem_input(N,neurons,T_test,params.dt,3.0)
test_stims["chem"] = (I, simulate_rate(W_norm,G_norm,I,T_test,params)["r"][ws:we].flatten())
I = np.zeros((int(T_test/params.dt),N))
for ii,n in enumerate(neurons):
    if n in {"AFDL","AFDR","ASJL","ASJR"}: I[:,ii]=2.0
test_stims["thermo"] = (I, simulate_rate(W_norm,G_norm,I,T_test,params)["r"][ws:we].flatten())
I = np.zeros((int(T_test/params.dt),N))
for ii,n in enumerate(neurons):
    if n in {"ASHL","ASHR"}: I[:,ii]=2.5
test_stims["nociception"] = (I, simulate_rate(W_norm,G_norm,I,T_test,params)["r"][ws:we].flatten())

def eval_W(W_hat):
    Wn = np.clip(W_hat/params.w_chem,0,None)
    r = pearsonr(W_TRUE.flatten()[nz_mask], W_hat.flatten()[nz_mask])[0]
    divs = {}
    for name,(I_t,r0) in test_stims.items():
        rh = simulate_rate(Wn,G_norm,I_t,T_test,params)["r"][ws:we].flatten()
        divs[name] = cdiv(r0,rh)
    return r, divs

print("="*72); print("POOL ROBUSTNESS -- K=100, M=15, 3 noise x 5 seeds"); print("="*72)
NOISES = [0.005, 0.01, 0.02]; SEEDS = [11, 23, 42, 777, 9999]
print(f"\n{'noise':>6}  {'seed':>5}  {'pearson':>8}  {'tap':>7}  {'chem':>7}  {'thermo':>7}  {'noci':>7}  verdict")
print("-"*70)
lines=[]
pass_count = {nl: 0 for nl in NOISES}
for nl in NOISES:
    for sd in SEEDS:
        W_hat = build_and_fit(100, 15, nl, sd)
        r, divs = eval_W(W_hat)
        p = all(d<0.05 for d in divs.values())
        pass_count[nl] += int(p)
        line = (f"{nl:>6.3f}  {sd:>5}  {r:>8.3f}  "
                f"{divs['tap']:>7.4f}  {divs['chem']:>7.4f}  "
                f"{divs['thermo']:>7.4f}  {divs['nociception']:>7.4f}  "
                f"{'PASS' if p else 'FAIL'}")
        print(line); lines.append(line)

print(f"\nPass rate by noise:")
for nl in NOISES:
    print(f"  noise={nl:.3f}:  {pass_count[nl]}/{len(SEEDS)}")

with open("simulation/results/scan_inverse_pool_robust.txt","w",encoding="utf-8") as f:
    f.write("Pool stim robustness (K=100, M=15, n_reps=10)\n"+"="*55+"\n")
    f.write(f"{'noise':>6}  {'seed':>5}  {'pearson':>8}  {'tap':>7}  {'chem':>7}  {'thermo':>7}  {'noci':>7}  verdict\n")
    f.write("-"*70+"\n"+"\n".join(lines)+"\n\nPass rate by noise:\n")
    for nl in NOISES:
        f.write(f"  noise={nl:.3f}:  {pass_count[nl]}/{len(SEEDS)}\n")
print("\nSaved: simulation/results/scan_inverse_pool_robust.txt")
