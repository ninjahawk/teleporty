"""
Type-based pool scan inverse -- biologically realistic optogenetic addressing.

So far pool stim used RANDOM subsets of M neurons. Real optogenetic
driver lines target CELL TYPES: ASEL (taste left), ASER (taste right),
ALML (touch anterior left), etc. Each "type" = a small group of cells
(in C. elegans most types are singletons or pairs, ~118 distinct types).

This script reorganizes pools to match cell-type structure:
  - Each pool = all cells matching a name prefix (e.g. "ALM" -> ALML, ALMR)
  - Pool count = number of distinct types (~118 in C. elegans)
  - Pool sizes range from 1 to ~6 (most types are pairs)

Question: does the protocol still pass when pools are constrained to
match biological reality?
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

# Build cell-type pools: strip trailing L/R/01/02 etc. from neuron names
import re
def type_of(name):
    # Remove trailing L/R or digit suffixes (common bilateral or row markers)
    m = re.match(r'^([A-Z]+)([A-Z0-9]*)$', name)
    if not m: return name
    prefix = m.group(1)
    return prefix

types = {}
for i, n in enumerate(neurons):
    t = type_of(n)
    types.setdefault(t, []).append(i)

print("="*72); print("TYPE-BASED POOL SCAN INVERSE"); print("="*72)
print(f"Total neurons: {N}; cell types: {len(types)}")
type_sizes = [len(v) for v in types.values()]
print(f"Type sizes: min={min(type_sizes)}, max={max(type_sizes)}, "
      f"mean={np.mean(type_sizes):.1f}, median={int(np.median(type_sizes))}")

# Build stimulus conditions: each type at multiple amplitudes
T_PROBE_ms = 300.0; T_probe = int(T_PROBE_ms/params.dt)
SS = (int(150.0/params.dt), int(280.0/params.dt)); SUB_SS = 2
EPS = 0.001; SAT_HI = 0.85; SAT_LO = 0.02
AMPS = [0.4, 0.8, 1.5]; N_REPS = 10; NOISE = 0.01
ratio = params.tau/params.dt

rng = np.random.default_rng(42)
type_names = list(types.keys())
K_pools = len(type_names)
K_total = K_pools * len(AMPS)
print(f"Type-based pools: {K_pools} types x {len(AMPS)} amplitudes = {K_total} conditions")
print(f"Total trials: {K_total * N_REPS} = {K_total*N_REPS}")

X = np.zeros((K_total, N)); Xp = np.zeros((K_total, N)); Ie = np.zeros((K_total, N))
k = 0
for t_name in type_names:
    pool_idx = types[t_name]
    for amp in AMPS:
        I_k = np.zeros((T_probe, N)); I_k[:, pool_idx] = amp
        R0 = simulate_rate(W_norm, G_norm, I_k, T_PROBE_ms, params)["r"]
        x_acc = np.zeros(N); xp_acc = np.zeros(N)
        for _ in range(N_REPS):
            R = R0 + rng.normal(0, NOISE, R0.shape); R = np.clip(R, 0, 1)
            ss = R[SS[0]:SS[1]:SUB_SS]; ssp = R[SS[0]+1:SS[1]+1:SUB_SS]
            x_acc += ss.mean(0); xp_acc += ssp.mean(0)
        X[k] = x_acc/N_REPS; Xp[k] = xp_acc/N_REPS; Ie[k] = I_k[SS[0]]; k += 1

# Fit
valid = Xp > EPS
targ = (Xp - X)*ratio + X
valid &= (targ>-0.95)&(targ<0.95)
x_safe = (X<SAT_HI)&(X>SAT_LO)|(X==0); valid &= x_safe
I_gap = X @ G.T - X * G_rowsum[np.newaxis,:]
z = np.arctanh(np.clip(targ,-0.95,0.95))/params.gain - I_gap - Ie

W_hat = np.zeros((N,N))
for j in range(N):
    sj = np.where(support[:,j])[0]
    if len(sj)==0: continue
    vj = valid[:,j]
    if vj.sum() < len(sj)+3: continue
    Xs = X[vj][:,sj]; zs = z[vj,j]
    A = Xs.T @ Xs + 1e-3*np.eye(len(sj)); b = Xs.T @ zs
    W_hat[sj,j] = np.clip(np.linalg.solve(A,b), 0, None)

pr = pearsonr(W_TRUE.flatten()[nz_mask], W_hat.flatten()[nz_mask])[0]
print(f"\nRecovery: Pearson r = {pr:.4f}")

# Verify
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

print(f"\nVerify across 4 stimuli (2 held out):")
Wn = np.clip(W_hat/params.w_chem,0,None)
all_pass = True
divs_out = {}
for name,(I_t,r0) in test_stims.items():
    rh = simulate_rate(Wn,G_norm,I_t,T_test,params)["r"][ws:we].flatten()
    d = cdiv(r0,rh); divs_out[name] = d
    p = d < 0.05
    all_pass = all_pass and p
    print(f"  {name:>12s}  div = {d:.4f}  [{'PASS' if p else 'FAIL'}]")

print(f"\n*** Type-based pool: {'PASS' if all_pass else 'FAIL'} ***")
print(f"This is the biologically realistic configuration: ~118 cell-type drivers.")

with open("simulation/results/scan_inverse_type_pools.txt","w",encoding="utf-8") as f:
    f.write("Type-based pool scan inverse (biological cell-type-driver match)\n"+"="*65+"\n")
    f.write(f"Cell types: {len(types)}, total conditions: {K_total}\n")
    f.write(f"Type size dist: min={min(type_sizes)}, max={max(type_sizes)}, mean={np.mean(type_sizes):.1f}\n")
    f.write(f"Total trials: {K_total*N_REPS}\n")
    f.write(f"Pearson r (W recovery): {pr:.4f}\n\n")
    for name, d in divs_out.items():
        f.write(f"  {name:>12s}  div = {d:.4f}  [{'PASS' if d<0.05 else 'FAIL'}]\n")
    f.write(f"\nVerdict: {'PASS' if all_pass else 'FAIL'}\n")
print("\nSaved: simulation/results/scan_inverse_type_pools.txt")
