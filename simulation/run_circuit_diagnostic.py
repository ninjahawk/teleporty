"""
Circuit diagnostic: is the tap circuit gap-junction dominated?

Hypothesis: tap withdrawal in C. elegans is primarily mediated by gap junctions
(ALM/PLM -> AVD/PVC). If so, W_true for tap-relevant chemical synapses is small,
making them impossible to recover from activity when mixed with larger chem signals.

Test 1: run tap simulation with G=0 (chemical only). If behavior changes drastically,
gap junctions are load-bearing for tap.

Test 2: compare tap neuron contribution via chemical vs gap junction current during
a tap event.

Test 3: directly check W_true column norms for tap vs chem neurons.
"""

import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")

from simulation.load_connectome import load_connectome, load_gap_junctions
from simulation.rate_model import RateParams, simulate_rate, make_tap_input, make_chem_input

os.makedirs("simulation/results", exist_ok=True)

print("Loading connectome...")
W_raw, neurons, W_norm = load_connectome()
G_raw, g_neurons = load_gap_junctions()
N = len(neurons)

g_idx = {n: i for i, n in enumerate(g_neurons)}
g_set = set(g_neurons)
G_aligned = np.zeros((N, N))
for i, ni in enumerate(neurons):
    for j, nj in enumerate(neurons):
        if ni in g_set and nj in g_set:
            G_aligned[i, j] = G_raw[g_idx[ni], g_idx[nj]]
G_norm = G_aligned / (G_aligned.max() or 1.0)

params = RateParams(tau=10.0, gain=2.5, w_chem=0.25, w_gap=0.1, dt=0.5)
W = W_norm * params.w_chem
G = G_norm * params.w_gap
G_zero = np.zeros_like(G_norm)

tap_neurons  = {"ALML", "ALMR", "AVM", "PLML", "PLMR", "PVM"}
chem_neurons = {"AWCL", "AWCR", "ASEL", "ASER"}
# Key interneurons downstream of tap
tap_interneurons = {"AVDL", "AVDR", "PVCL", "PVCR", "AVAL", "AVAR"}
tap_idx  = [i for i, n in enumerate(neurons) if n in tap_neurons]
chem_idx = [i for i, n in enumerate(neurons) if n in chem_neurons]
ti_idx   = [i for i, n in enumerate(neurons) if n in tap_interneurons]

T_test = 600.0
I_tap  = make_tap_input(N, neurons, T_test, params.dt,
                         onset_ms=50.0, duration_ms=30.0, amplitude=4.0)
I_chem = make_chem_input(N, neurons, T_test, params.dt, amplitude=3.0)
ws, we = int(100/params.dt), int(500/params.dt)


def cdiv(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 1.0 - np.dot(a, b)/(na*nb) if na > 1e-10 and nb > 1e-10 else 1.0


# -------------------------------------------------------------------
# Test 1: tap behavior with full model vs. G=0
# -------------------------------------------------------------------
print("\n--- Test 1: gap junction ablation ---")
r_tap_full  = simulate_rate(W_norm, G_norm,  I_tap, T_test, params)["r"]
r_tap_noG   = simulate_rate(W_norm, G_zero,  I_tap, T_test, params)["r"]
r_chem_full = simulate_rate(W_norm, G_norm,  I_chem, T_test, params)["r"]
r_chem_noG  = simulate_rate(W_norm, G_zero,  I_chem, T_test, params)["r"]

r_tap_bv  = r_tap_full[ws:we].flatten()
r_tap_noG_bv = r_tap_noG[ws:we].flatten()
r_chem_bv = r_chem_full[ws:we].flatten()
r_chem_noG_bv = r_chem_noG[ws:we].flatten()

div_tap_noG  = cdiv(r_tap_bv,  r_tap_noG_bv)
div_chem_noG = cdiv(r_chem_bv, r_chem_noG_bv)
print(f"Tap  divergence (full vs G=0):  {div_tap_noG:.4f}  {'[gap junctions critical]' if div_tap_noG > 0.1 else '[gap junctions minor]'}")
print(f"Chem divergence (full vs G=0):  {div_chem_noG:.4f}  {'[gap junctions critical]' if div_chem_noG > 0.1 else '[gap junctions minor]'}")

# -------------------------------------------------------------------
# Test 2: chemical vs gap junction current magnitudes at tap interneurons
# during a tap event
# -------------------------------------------------------------------
print("\n--- Test 2: current decomposition at tap interneurons during tap event ---")
onset_step = int(50.0 / params.dt)
end_step   = int(80.0 / params.dt)   # 30ms tap window

r_during = r_tap_full[onset_step:end_step]     # (60, N) during tap
r_before = r_tap_full[max(0,onset_step-20):onset_step]  # baseline

for name, i_list in [("Tap sensors (ALM/PLM/AVM)", tap_idx),
                      ("Tap interneurons (AVD/PVC/AVA)", ti_idx)]:
    if not i_list:
        print(f"  {name}: not found")
        continue
    I_chem_j  = (r_during @ W)[:, i_list].mean()        # chem input to j
    I_gap_j   = (r_during @ G.T - r_during * G.sum(axis=1))[:, i_list].mean()
    ratio_txt = f"chem/gap = {abs(I_chem_j)/max(abs(I_gap_j),1e-10):.2f}"
    print(f"  {name}: I_chem={I_chem_j:.4f}, I_gap={I_gap_j:.4f}  [{ratio_txt}]")

# -------------------------------------------------------------------
# Test 3: weight matrix properties for tap vs chem neurons
# -------------------------------------------------------------------
print("\n--- Test 3: weight matrix properties ---")
# Chemical output from tap vs chem neurons (row norms of W)
tap_out_chem  = np.linalg.norm(W[tap_idx, :], axis=1)   # chemical output weights
tap_out_gap   = np.linalg.norm(G[tap_idx, :], axis=1)   # gap output weights
chem_out_chem = np.linalg.norm(W[chem_idx, :], axis=1)
chem_out_gap  = np.linalg.norm(G[chem_idx, :], axis=1)

print(f"Tap sensor chemical output weights (row norms):  mean={tap_out_chem.mean():.4f}, max={tap_out_chem.max():.4f}")
print(f"Tap sensor gap output weights (row norms):       mean={tap_out_gap.mean():.4f}, max={tap_out_gap.max():.4f}")
print(f"Chem sensor chemical output weights (row norms): mean={chem_out_chem.mean():.4f}, max={chem_out_chem.max():.4f}")
print(f"Chem sensor gap output weights (row norms):      mean={chem_out_gap.mean():.4f}, max={chem_out_gap.max():.4f}")
print(f"\nGlobal mean chemical weight: {W[W>0].mean():.4f}")
print(f"Global mean gap weight:      {G[G>0].mean():.4f}")

# Signal-to-noise check: how recoverable are tap-related weights?
# Effective SNR for regression: variance of W * var(X) / noise
# Approximated as: mean(W[tap,:]) / mean(W_all)
tap_w_mean  = W[tap_idx, :].mean()
chem_w_mean = W[chem_idx, :].mean()
all_w_mean  = W[W>0].mean()
print(f"\nMean chemical weight FROM tap sensors:  {tap_w_mean:.4f} (vs global mean {all_w_mean:.4f})")
print(f"Mean chemical weight FROM chem sensors: {chem_w_mean:.4f} (vs global mean {all_w_mean:.4f})")

# Number of chemical vs gap connections FROM tap neurons
tap_chem_nnz = (W[tap_idx, :] > 1e-6).sum()
tap_gap_nnz  = (G[tap_idx, :] > 1e-6).sum()
print(f"\nChemical connections FROM tap sensors: {tap_chem_nnz}")
print(f"Gap connections FROM tap sensors:      {tap_gap_nnz}")
print(f"Gap/(Chem+Gap) ratio for tap sensors:  {tap_gap_nnz/(tap_chem_nnz+tap_gap_nnz+1e-10):.3f}")

chem_chem_nnz = (W[chem_idx, :] > 1e-6).sum()
chem_gap_nnz  = (G[chem_idx, :] > 1e-6).sum()
print(f"\nChemical connections FROM chem sensors: {chem_chem_nnz}")
print(f"Gap connections FROM chem sensors:      {chem_gap_nnz}")
print(f"Gap/(Chem+Gap) ratio for chem sensors:  {chem_gap_nnz/(chem_chem_nnz+chem_gap_nnz+1e-10):.3f}")

# -------------------------------------------------------------------
# Plot: tap response with and without gap junctions
# -------------------------------------------------------------------
t_ax = np.arange(r_tap_full.shape[0]) * params.dt

fig, axes = plt.subplots(2, 2, figsize=(14, 8))
fig.suptitle("Circuit Diagnostic: Is Tap Withdrawal Gap-Junction Dominated?", fontsize=12)

ax = axes[0,0]
for idx in tap_idx:
    ax.plot(t_ax, r_tap_full[:, idx], lw=1.5, alpha=0.8, label=neurons[idx])
ax.set_title("Tap sensors — full model"); ax.set_xlabel("t (ms)"); ax.set_ylabel("r")
ax.axvline(50, color="k", ls="--", lw=1); ax.axvline(80, color="k", ls="--", lw=1)
ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

ax = axes[0,1]
for idx in tap_idx:
    ax.plot(t_ax, r_tap_noG[:, idx], lw=1.5, alpha=0.8, label=neurons[idx])
ax.set_title(f"Tap sensors — G=0 (div={div_tap_noG:.3f})"); ax.set_xlabel("t (ms)")
ax.axvline(50, color="k", ls="--", lw=1); ax.axvline(80, color="k", ls="--", lw=1)
ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

ax = axes[1,0]
for idx in ti_idx:
    ax.plot(t_ax, r_tap_full[:, idx], lw=1.5, alpha=0.8, label=neurons[idx])
ax.set_title("Tap interneurons — full model"); ax.set_xlabel("t (ms)")
ax.axvline(50, color="k", ls="--", lw=1); ax.axvline(80, color="k", ls="--", lw=1)
ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

ax = axes[1,1]
for idx in ti_idx:
    ax.plot(t_ax, r_tap_noG[:, idx], lw=1.5, alpha=0.8, label=neurons[idx])
ax.set_title(f"Tap interneurons — G=0 (div={div_tap_noG:.3f})"); ax.set_xlabel("t (ms)")
ax.axvline(50, color="k", ls="--", lw=1); ax.axvline(80, color="k", ls="--", lw=1)
ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("simulation/results/circuit_diagnostic.png", dpi=150)
plt.close()
print("\nSaved: simulation/results/circuit_diagnostic.png")
print("Done.")
