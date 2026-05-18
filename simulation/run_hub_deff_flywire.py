"""
Hub-neuron d_eff empirical test on Drosophila (FlyWire) connectome.

The pool-stim protocol assumes K_pools > d_eff(input vector) per neuron,
not K > |supp|. Rate-distortion conjecture: even for high-|supp| neurons,
the input vector lives in a much lower-dimensional effective subspace.

If this conjecture holds: pool stim scales to mammalian cortex hubs.
If it fails: hub neurons need sparse-prior reconstruction.

Drosophila has Kenyon cells (mushroom body) that receive ~1000+ convergent
inputs from PNs -- analogous to mammalian Purkinje convergence. Real-data test.

For each high-|supp| neuron j:
  1. Extract the column W[:, j] (incoming weights)
  2. The "input direction" is the unit vector formed by this column
  3. But d_eff of a single column doesn't make sense
  4. Instead: group neurons by cell-type and ask -- across all neurons of
     the same type, what's the d_eff of the COLLECTION of incoming vectors?

That is: stack the columns of all neurons in a type T into a matrix
  M_T = (N x n_T) where n_T = # neurons of type T
Compute participation ratio of singular values of M_T. This is the
d_eff of the "input space" sampled by that type.

If d_eff(M_T) << max(|supp_j| for j in type T), the type's input weights
are highly redundant, and pool stim with K ~ d_eff is enough to recover
each neuron's weights as a linear combination of basis weight-patterns.
"""
import os, sys, numpy as np, pandas as pd, time
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")

print("="*72); print("HUB NEURON d_eff -- FlyWire (Drosophila)"); print("="*72)

t0 = time.time()
print("Loading flywire connection table...")
df = pd.read_feather('simulation/data/flywire_connections_783.feather')
print(f"  {len(df)} synapse rows loaded in {time.time()-t0:.1f}s")

# Build a sparse-friendly view
# Filter to synapses with syn_count >= 5 (strong connections only) to limit memory
df_strong = df[df['syn_count'] >= 5][['pre_pt_root_id','post_pt_root_id','syn_count']]
print(f"  syn_count>=5: {len(df_strong)} edges")

# Build incoming-degree distribution (|supp_j|)
in_deg = df_strong.groupby('post_pt_root_id').size()
print(f"  Neurons with incoming edges: {len(in_deg)}")
print(f"  |supp| distribution: median={int(in_deg.median())}, "
      f"95th={int(in_deg.quantile(0.95))}, max={int(in_deg.max())}")

# Identify hub neurons: top 1% by in-degree
hub_threshold = int(in_deg.quantile(0.99))
print(f"  Hub threshold (99th %ile in-degree): {hub_threshold}")
hubs = in_deg[in_deg >= hub_threshold].index.values
print(f"  Hub neurons: {len(hubs)}")

# For each hub, get its column W[:, j] = incoming weights
# Use full edges (syn_count any) for the actual weight vectors
df_full = df[['pre_pt_root_id','post_pt_root_id','syn_count']]
print(f"\nBuilding hub incoming-weight vectors...")

# Group all incoming edges for hub neurons
hub_set = set(hubs.tolist())
mask = df_full['post_pt_root_id'].isin(hub_set)
df_hubs = df_full[mask]
print(f"  Edges to hubs: {len(df_hubs)}")

# We need an index for presynaptic neurons. Use all unique pre IDs that connect to hubs.
unique_pre = df_hubs['pre_pt_root_id'].unique()
pre_id_to_idx = {pid: i for i, pid in enumerate(unique_pre)}
N_pre = len(unique_pre)
print(f"  Unique presynaptic neurons (basis): {N_pre}")

# Build sparse incoming-weight matrix M (N_pre x n_hubs)
# Scale up: take all hubs (1257) to make sure d_eff doesn't grow with sample
sample_size = min(1000, len(hubs))
sample_hubs = hubs[:sample_size]
print(f"  Sampling {sample_size} hubs for d_eff calc")

from scipy.sparse import lil_matrix
M = lil_matrix((N_pre, sample_size))
for col, h in enumerate(sample_hubs):
    rows = df_hubs[df_hubs['post_pt_root_id'] == h]
    for _, row in rows.iterrows():
        pre_idx = pre_id_to_idx[row['pre_pt_root_id']]
        M[pre_idx, col] = row['syn_count']
M = M.tocsr()
print(f"  M shape: {M.shape}, nnz: {M.nnz}")

# Compute d_eff via SVD (truncated for efficiency)
print(f"\nComputing SVD of M...")
from scipy.sparse.linalg import svds
n_sv = min(sample_size - 1, 300)  # top 300 singular values for larger sample
u, s, vt = svds(M.astype(np.float64), k=n_sv)
s = np.sort(s)[::-1]
print(f"  Top 5 singular values: {s[:5]}")
print(f"  Top 10 fraction of total variance: {(s[:10]**2).sum() / (s**2).sum():.4f}")

# Participation ratio
s2 = s**2
d_eff = (s2.sum()**2) / (s2**2).sum()
print(f"\n  Participation ratio d_eff = {d_eff:.1f}")
print(f"  Compare to: sample size n_hubs = {sample_size}")
print(f"  Compare to: median |supp_j| in hubs = {int(np.median([in_deg[h] for h in sample_hubs]))}")
print(f"  Compare to: max |supp_j| in hubs    = {int(np.max([in_deg[h] for h in sample_hubs]))}")

ratio_to_supp = d_eff / np.median([in_deg[h] for h in sample_hubs])
print(f"\n  d_eff / median(|supp_hub|) = {ratio_to_supp:.3f}")

if d_eff < np.median([in_deg[h] for h in sample_hubs]) / 5:
    print("\n=> d_eff << |supp_j|. Rate-distortion conjecture HOLDS.")
    print("   Pool stim with K ~ d_eff recovers hub weights.")
    print("   Human-scale Purkinje scaling: tractable.")
elif d_eff < np.median([in_deg[h] for h in sample_hubs]):
    print("\n=> d_eff modestly smaller than |supp_j|. Conjecture WEAK.")
    print("   Some redundancy but not the order-of-magnitude saving needed.")
else:
    print("\n=> d_eff ~ |supp_j|. Conjecture FAILS for this hub class.")
    print("   Pool stim needs sparse priors / group-LASSO for hubs.")

with open("simulation/results/hub_deff_flywire.txt", "w", encoding="utf-8") as f:
    f.write("FlyWire hub-neuron d_eff test\n"+"="*45+"\n")
    f.write(f"Hub threshold (99th %ile in-degree): {hub_threshold}\n")
    f.write(f"Sample size: {sample_size} hubs\n")
    f.write(f"Median |supp|:    {int(np.median([in_deg[h] for h in sample_hubs]))}\n")
    f.write(f"Max |supp|:       {int(np.max([in_deg[h] for h in sample_hubs]))}\n")
    f.write(f"Participation d_eff = {d_eff:.1f}\n")
    f.write(f"d_eff / median(|supp|) = {ratio_to_supp:.3f}\n")
    f.write(f"\nTop singular values (first 10): {list(s[:10])}\n")
print("\nSaved: simulation/results/hub_deff_flywire.txt")
print(f"\nTotal time: {time.time()-t0:.1f}s")
