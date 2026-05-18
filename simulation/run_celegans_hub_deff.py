"""
C. elegans command-neuron d_eff analysis.

The Drosophila hub test (run_hub_deff_flywire.py) showed d_eff << |supp|
for top-1% in-degree neurons. Now check C. elegans command interneurons
(AVA, AVD, AVE, AVB, PVC) which are the locomotion command system.

These are the highest-in-degree neurons in C. elegans and the closest
analog to a hub. Question: does their incoming weight space show low
d_eff (consistent with the multi-task fit hypothesis)?
"""
import os, sys, numpy as np
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from simulation.load_connectome import load_connectome

W_raw, neurons, W_norm = load_connectome()
N = len(neurons)
print("="*72); print("C. ELEGANS COMMAND-NEURON d_eff"); print("="*72)

# In-degree per neuron
in_deg = (W_raw > 0).sum(axis=0)
print(f"\nIn-degree distribution:")
print(f"  median = {int(np.median(in_deg))}, max = {int(in_deg.max())}, "
      f"95th = {int(np.percentile(in_deg, 95))}")

# Identify the command neurons by name
cmd_names = ["AVAL","AVAR","AVDL","AVDR","AVEL","AVER","AVBL","AVBR","PVCL","PVCR"]
cmd_idx = [i for i, n in enumerate(neurons) if n in cmd_names]
print(f"\nCommand neurons (n={len(cmd_idx)}):")
for i in cmd_idx:
    print(f"  {neurons[i]:>6s}  in-degree = {int(in_deg[i])}")

# Top-10 by in-degree (regardless of identity)
top_idx = np.argsort(-in_deg)[:10]
print(f"\nTop 10 by in-degree:")
for i in top_idx:
    print(f"  {neurons[i]:>6s}  in-degree = {int(in_deg[i])}")

# d_eff of command-neuron input weight matrix
W_cmd = W_norm[:, cmd_idx]  # (N, n_cmd) -- incoming weights to each command neuron
print(f"\nCommand-neuron incoming weight matrix shape: {W_cmd.shape}")
print(f"  Nonzeros: {(W_cmd > 0).sum()}")
print(f"  Mean |supp| (per command): {(W_cmd > 0).sum() / W_cmd.shape[1]:.1f}")

u, s, vt = np.linalg.svd(W_cmd, full_matrices=False)
print(f"  Singular values: {s[:5]}")
s2 = s**2; d_eff = (s2.sum()**2) / (s2**2).sum()
print(f"  Participation ratio d_eff = {d_eff:.2f}")
print(f"  Ratio d_eff / mean(|supp|) = {d_eff / ((W_cmd > 0).sum() / W_cmd.shape[1]):.3f}")

# Same for top-10 hubs
W_top = W_norm[:, top_idx]
u2, s2, _ = np.linalg.svd(W_top, full_matrices=False)
s2_sq = s2**2; d_eff_top = (s2_sq.sum()**2) / (s2_sq**2).sum()
print(f"\nTop-10 hub d_eff: {d_eff_top:.2f}")

# Compare to random control: 10 random columns
rng = np.random.default_rng(0)
rand_idx = rng.choice(N, size=10, replace=False)
W_rand = W_norm[:, rand_idx]
ur, sr, _ = np.linalg.svd(W_rand, full_matrices=False)
sr2 = sr**2; d_eff_rand = (sr2.sum()**2) / (sr2**2).sum()
print(f"Random-10 control d_eff: {d_eff_rand:.2f}")

# Verdict
print(f"\n=== VERDICT ===")
print(f"Command neurons d_eff: {d_eff:.2f}")
print(f"Mean |supp| per command: {(W_cmd > 0).sum() / W_cmd.shape[1]:.1f}")
if d_eff < 0.5 * (W_cmd > 0).sum() / W_cmd.shape[1]:
    print("=> d_eff < 0.5x mean(|supp|): command-neuron inputs are LOW-RANK.")
    print("   Multi-task fit at K ~ d_eff is feasible.")
else:
    print("=> d_eff ~ mean(|supp|): command-neuron inputs are NOT particularly low-rank.")
    print("   Multi-task fit may not help in this case.")

with open("simulation/results/celegans_hub_deff.txt", "w", encoding="utf-8") as f:
    f.write("C. elegans command-neuron d_eff\n"+"="*45+"\n")
    f.write(f"Command neurons (n={len(cmd_idx)}): {[neurons[i] for i in cmd_idx]}\n")
    f.write(f"In-degrees: {[int(in_deg[i]) for i in cmd_idx]}\n")
    f.write(f"Mean |supp|: {(W_cmd > 0).sum() / W_cmd.shape[1]:.1f}\n")
    f.write(f"Participation ratio d_eff: {d_eff:.2f}\n")
    f.write(f"\nTop-10 hub d_eff: {d_eff_top:.2f}\n")
    f.write(f"Random-10 control d_eff: {d_eff_rand:.2f}\n")
print(f"\nSaved: simulation/results/celegans_hub_deff.txt")
