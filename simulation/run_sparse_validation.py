"""
Validate simulate_rate_sparse against the dense simulate_rate.

The sparse version must produce identical trajectories (to numerical
precision) on the C. elegans connectome, then we measure the speedup
on a larger synthetic sparse network.
"""
import os, sys, time, numpy as np
import scipy.sparse as sp
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from simulation.load_connectome import load_connectome, load_gap_junctions
from simulation.rate_model import RateParams, simulate_rate, simulate_rate_sparse, make_tap_input

print("="*72); print("SPARSE SIMULATOR VALIDATION"); print("="*72)

# --- C. elegans correctness check ---
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
I = make_tap_input(N, neurons, 600.0, params.dt, 50.0, 30.0, 4.0)

print(f"\nC. elegans (N={N}): comparing dense vs sparse trajectory...")
t0 = time.time(); R_dense = simulate_rate(W_norm, G_norm, I, 600.0, params)["r"]; t_dense = time.time()-t0
t0 = time.time(); R_sparse = simulate_rate_sparse(W_norm, G_norm, I, 600.0, params)["r"]; t_sparse = time.time()-t0

max_diff = np.abs(R_dense - R_sparse).max()
print(f"  Dense time:  {t_dense*1000:.1f} ms")
print(f"  Sparse time: {t_sparse*1000:.1f} ms")
print(f"  Max abs trajectory difference: {max_diff:.2e}")
if max_diff < 1e-9:
    print("  => IDENTICAL (within numerical precision). Sparse path validated.")
else:
    print(f"  => WARNING: difference {max_diff:.2e} exceeds tolerance!")

# --- Speedup at larger N ---
print(f"\nSpeedup benchmark on synthetic sparse networks:")
print(f"{'N':>6}  {'density':>8}  {'dense (s)':>10}  {'sparse (s)':>11}  {'speedup':>8}")
print("-"*52)
for N_test, dens in [(500, 0.02), (1000, 0.01), (2000, 0.005), (4000, 0.0025)]:
    rng = np.random.default_rng(0)
    mask = rng.random((N_test, N_test)) < dens
    np.fill_diagonal(mask, False)
    Wn = np.zeros((N_test, N_test))
    Wn[mask] = rng.lognormal(-2, 1, mask.sum())
    Wn /= Wn.max()
    Gn = np.zeros((N_test, N_test))
    I_t = np.zeros((int(300/params.dt), N_test)); I_t[:, :10] = 2.0

    t0 = time.time(); simulate_rate(Wn, Gn, I_t, 300.0, params); td = time.time()-t0
    Wsp = sp.csr_matrix(Wn); Gsp = sp.csr_matrix(Gn)
    t0 = time.time(); simulate_rate_sparse(Wsp, Gsp, I_t, 300.0, params); ts = time.time()-t0
    print(f"{N_test:>6}  {dens:>8.4f}  {td:>10.2f}  {ts:>11.2f}  {td/ts:>7.1f}x")

print(f"\n=> Sparse simulator enables N >= 10^4 connectome simulations that")
print(f"   are intractable with the dense O(N^2) version.")

with open("simulation/results/sparse_validation.txt", "w", encoding="utf-8") as f:
    f.write("Sparse simulator validation\n"+"="*40+"\n")
    f.write(f"C. elegans dense-vs-sparse max trajectory diff: {max_diff:.2e}\n")
    f.write(f"{'verdict':>10}: {'IDENTICAL' if max_diff < 1e-9 else 'MISMATCH'}\n")
print("\nSaved: simulation/results/sparse_validation.txt")
