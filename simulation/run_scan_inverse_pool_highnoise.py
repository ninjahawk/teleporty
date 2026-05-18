"""
Pool stim at 5% rate noise (where v4 per-neuron failed).

v4 per-neuron at 5% rate noise: plateaued at div_tap ~ 0.78 regardless
of n_reps -- clipping bias on saturated rates dominates.

Question: does pool stim avoid this saturation regime and thus tolerate
higher noise?

Setup: K=100, M=15 pool config; sweep noise from 1% to 10%.
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
AMPS = [0.4, 0.8, 1.5]
ratio = params.tau/params.dt

def run(noise, n_reps, seed):
    rng = np.random.default_rng(seed)
    K_pools, M = 100, 15
    K_total = K_pools*len(AMPS)
    X = np.zeros((K_total,N)); Xp = np.zeros((K_total,N)); Ie = np.zeros((K_total,N))
    k=0
    for p in range(K_pools):
        pool = rng.choice(N, size=M, replace=False)
        for amp in AMPS:
            I_k = np.zeros((T_probe,N)); I_k[:,pool]=amp
            R0 = simulate_rate(W_norm, G_norm, I_k, T_PROBE_ms, params)["r"]
            x_acc=np.zeros(N); xp_acc=np.zeros(N)
            for _ in range(n_reps):
                R = R0 + rng.normal(0,noise,R0.shape); R = np.clip(R,0,1)
                ss = R[SS[0]:SS[1]:SUB_SS]; ssp = R[SS[0]+1:SS[1]+1:SUB_SS]
                x_acc+=ss.mean(0); xp_acc+=ssp.mean(0)
            X[k]=x_acc/n_reps; Xp[k]=xp_acc/n_reps; Ie[k]=I_k[SS[0]]; k+=1
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

def eval_W(W_hat):
    Wn = np.clip(W_hat/params.w_chem,0,None)
    pr = pearsonr(W_TRUE.flatten()[nz_mask], W_hat.flatten()[nz_mask])[0]
    divs = {}
    for name,(I_t,r0) in test_stims.items():
        rh = simulate_rate(Wn,G_norm,I_t,T_test,params)["r"][ws:we].flatten()
        divs[name] = cdiv(r0,rh)
    return pr, divs

print("="*72); print("POOL STIM AT HIGH NOISE (pool K=100,M=15)"); print("="*72)
print(f"\n{'noise':>6}  {'n_reps':>7}  {'pearson':>8}  {'div_tap':>8}  {'div_chem':>9}  verdict")
print("-"*55)
lines = []
for noise in [0.01, 0.02, 0.03, 0.05, 0.08, 0.10]:
    for nr in [10, 30] if noise <= 0.05 else [10, 30, 100]:
        W_hat = run(noise, nr, seed=42)
        pr, divs = eval_W(W_hat)
        passed = (divs["tap"] < 0.05) and (divs["chem"] < 0.05)
        line = f"{noise:>6.2f}  {nr:>7}  {pr:>8.3f}  {divs['tap']:>8.4f}  {divs['chem']:>9.4f}  {'PASS' if passed else 'FAIL'}"
        print(line); lines.append(line)

with open("simulation/results/scan_inverse_pool_highnoise.txt","w",encoding="utf-8") as f:
    f.write("Pool stim at high rate noise (K=100, M=15)\n"+"="*55+"\n")
    f.write(f"{'noise':>6}  {'n_reps':>7}  {'pearson':>8}  {'div_tap':>8}  {'div_chem':>9}  verdict\n")
    f.write("\n".join(lines)+"\n")
print("\nSaved: simulation/results/scan_inverse_pool_highnoise.txt")
