"""
Support-error robustness test for pool-stim scan inverse.

All recovery methods to this point assume the structural support (binary
connectome from EM) is KNOWN EXACTLY. Real EM has:
  - false positives: spurious synapse calls (often touching but not
    connected cells, or vesicle-free contacts)
  - false negatives: missed synapses (small en passant boutons, sectioning
    artifacts)
Typical reported error rates: 5-10% FP, 5-15% FN (Helmstaedter 2013).

This script perturbs the support before regression and measures the impact
on recovered W quality, using the K=100, M=15 pool config at 1% noise.

We test:
  - 5% FP only
  - 5% FN only
  - 5% FP + 5% FN
  - 10% FP + 10% FN
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
G_rowsum = G.sum(axis=1); support_true = (W_TRUE>0); nz_mask = W_TRUE.flatten()>1e-6

T_PROBE_ms = 300.0; T_probe = int(T_PROBE_ms/params.dt)
SS = (int(150.0/params.dt), int(280.0/params.dt)); SUB_SS = 2
EPS = 0.001; SAT_HI = 0.85; SAT_LO = 0.02
AMPS = [0.4, 0.8, 1.5]; N_REPS = 10
ratio = params.tau/params.dt

def perturb_support(support_true, fp_rate, fn_rate, seed):
    """Return a perturbed support matrix with given FP/FN rates."""
    rng = np.random.default_rng(seed)
    s = support_true.copy()
    # false negatives: remove some true edges
    if fn_rate > 0:
        true_edges = np.where(support_true)
        n_true = len(true_edges[0])
        n_remove = int(fn_rate * n_true)
        drop_idx = rng.choice(n_true, size=n_remove, replace=False)
        for k in drop_idx:
            s[true_edges[0][k], true_edges[1][k]] = False
    # false positives: add spurious edges
    if fp_rate > 0:
        false_pos_pool = np.where(~support_true & ~np.eye(N, dtype=bool))
        n_neg = len(false_pos_pool[0])
        n_add = int(fp_rate * support_true.sum())   # proportional to true count
        add_idx = rng.choice(n_neg, size=n_add, replace=False)
        for k in add_idx:
            s[false_pos_pool[0][k], false_pos_pool[1][k]] = True
    return s

def build_data(K_pools, M_pool, seed):
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
                R = R0 + rng.normal(0,0.01,R0.shape); R = np.clip(R,0,1)
                ss = R[SS[0]:SS[1]:SUB_SS]; ssp = R[SS[0]+1:SS[1]+1:SUB_SS]
                x_acc+=ss.mean(0); xp_acc+=ssp.mean(0)
            X[k]=x_acc/N_REPS; Xp[k]=xp_acc/N_REPS; Ie[k]=I_k[SS[0]]; k+=1
    return X, Xp, Ie

def fit_with_support(X, Xp, Ie, support):
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
    pr = pearsonr(W_TRUE.flatten()[nz_mask], W_hat.flatten()[nz_mask])[0]
    divs = {}
    for name,(I_t,r0) in test_stims.items():
        rh = simulate_rate(Wn,G_norm,I_t,T_test,params)["r"][ws:we].flatten()
        divs[name] = cdiv(r0,rh)
    return pr, divs

print("="*72); print("SUPPORT-ERROR ROBUSTNESS (pool K=100, M=15)"); print("="*72)
X, Xp, Ie = build_data(K_pools=100, M_pool=15, seed=42)

configs = [
    ("exact support",       0.00, 0.00),
    ("5% FP",               0.05, 0.00),
    ("5% FN",               0.00, 0.05),
    ("5% FP + 5% FN",       0.05, 0.05),
    ("10% FP + 10% FN",     0.10, 0.10),
    ("20% FP + 20% FN",     0.20, 0.20),
]
print(f"\n{'condition':>20}  {'pearson':>8}  {'tap':>7}  {'chem':>7}  {'thermo':>7}  {'noci':>7}  verdict")
print("-"*80)
lines = []
for name, fp, fn in configs:
    sup = perturb_support(support_true, fp, fn, seed=123)
    W_hat = fit_with_support(X, Xp, Ie, sup)
    pr, divs = eval_W(W_hat)
    passed = all(d<0.05 for d in divs.values())
    line = (f"{name:>20}  {pr:>8.3f}  {divs['tap']:>7.4f}  {divs['chem']:>7.4f}  "
            f"{divs['thermo']:>7.4f}  {divs['nociception']:>7.4f}  {'PASS' if passed else 'FAIL'}")
    print(line); lines.append(line)

with open("simulation/results/scan_inverse_support_errors.txt","w",encoding="utf-8") as f:
    f.write("Support-error robustness test (pool K=100, M=15)\n"+"="*60+"\n")
    f.write(f"{'condition':>20}  {'pearson':>8}  {'tap':>7}  {'chem':>7}  {'thermo':>7}  {'noci':>7}  verdict\n")
    f.write("\n".join(lines)+"\n")
print("\nSaved: simulation/results/scan_inverse_support_errors.txt")
