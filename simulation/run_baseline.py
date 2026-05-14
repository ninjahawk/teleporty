"""
Phase 7A: Baseline C. elegans simulation.

Verifies the LIF model produces plausible activity for two stimuli:
1. Tap-withdrawal reflex (backward locomotion circuit)
2. Chemotaxis (AWC/ASE sensory input)

Outputs:
- simulation/results/baseline_tap.npz
- simulation/results/baseline_chem.npz
- simulation/results/baseline_summary.txt
- simulation/results/baseline_raster.png
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")

from simulation.load_connectome import load_connectome, load_gap_junctions
from simulation.lif_model import LIFParams, simulate, make_tap_stimulus, make_chemotaxis_stimulus

os.makedirs("simulation/results", exist_ok=True)

print("Loading connectome...")
W_raw, neurons, W_norm = load_connectome()
G_raw, _ = load_gap_junctions()

# Align gap junctions to same neuron set (they may have different coverage)
N = len(neurons)
# G_raw already aligned by load_gap_junctions using the same 'common' set
# But load_gap_junctions uses its own common set — need to align
from simulation.load_connectome import load_gap_junctions
import re

def is_neuron(name):
    if not isinstance(name, str): return False
    return bool(re.match(r'^[A-Z][A-Z0-9]{1,6}$', name.strip()))

import pandas as pd
path = "simulation/data/SI5_connectome_adjacency.xlsx"
df_gap = pd.read_excel(path, sheet_name="hermaphrodite gap jn symmetric", header=None)
col_names = df_gap.iloc[2, 3:].values
row_names = df_gap.iloc[3:, 2].values
valid_col_idx = [i+3 for i, n in enumerate(col_names) if is_neuron(str(n).strip())]
valid_col_names = [str(col_names[i-3]).strip() for i in valid_col_idx]
valid_row_idx = [i+3 for i, n in enumerate(row_names) if is_neuron(str(n).strip())]
valid_row_names = [str(row_names[i-3]).strip() for i in valid_row_idx]
data_gap = df_gap.iloc[valid_row_idx, :].iloc[:, valid_col_idx]
data_gap = data_gap.fillna(0).astype(float)
data_gap.index = valid_row_names
data_gap.columns = valid_col_names
gap_common = sorted(set(valid_row_names) & set(valid_col_names))
G_full = data_gap.loc[gap_common, gap_common].values.astype(float)

# Build gap matrix aligned to W neuron set
neuron_set = set(neurons)
gap_set = set(gap_common)
G_aligned = np.zeros((N, N))
for i, ni in enumerate(neurons):
    for j, nj in enumerate(neurons):
        if ni in gap_set and nj in gap_set:
            gi = gap_common.index(ni)
            gj = gap_common.index(nj)
            G_aligned[i, j] = G_full[gi, gj]

G_norm = G_aligned / (G_aligned.max() if G_aligned.max() > 0 else 1.0)

print(f"Network: {N} neurons, {(W_norm>0).sum()} chemical connections, {(G_norm>0).sum()} gap junctions")

params = LIFParams(
    tau_m=10.0, tau_syn=5.0, V_thresh=1.0, V_reset=0.0,
    t_ref=2.0, dt=0.1, w_chem_scale=0.06, w_gap_scale=0.03
)

T_ms = 500.0  # 500 ms simulation

# --- Simulation 1: Tap withdrawal ---
print("Running tap-withdrawal simulation...")
I_tap = make_tap_stimulus(N, neurons, T_ms, params.dt, onset_ms=50.0, duration_ms=20.0, amplitude=3.0)
result_tap = simulate(W_norm, G_norm, I_tap, T_ms, params, seed=42)
np.savez("simulation/results/baseline_tap.npz",
         V=result_tap["V"], spikes=result_tap["spikes"],
         spike_rate=result_tap["spike_rate"], neurons=neurons, T_ms=T_ms, dt=params.dt)

tap_active = (result_tap["spike_rate"] > 0.5).sum()
tap_total_spikes = result_tap["spikes"].sum()
print(f"  Active neurons (>0.5 Hz): {tap_active}/{N}")
print(f"  Total spikes: {tap_total_spikes}")
print(f"  Mean rate (active): {result_tap['spike_rate'][result_tap['spike_rate']>0.5].mean():.1f} Hz")

# --- Simulation 2: Chemotaxis ---
print("Running chemotaxis simulation...")
I_chem = make_chemotaxis_stimulus(N, neurons, T_ms, params.dt, amplitude=2.0)
result_chem = simulate(W_norm, G_norm, I_chem, T_ms, params, seed=42)
np.savez("simulation/results/baseline_chem.npz",
         V=result_chem["V"], spikes=result_chem["spikes"],
         spike_rate=result_chem["spike_rate"], neurons=neurons, T_ms=T_ms, dt=params.dt)

chem_active = (result_chem["spike_rate"] > 0.5).sum()
print(f"  Active neurons (>0.5 Hz): {chem_active}/{N}")
print(f"  Total spikes: {result_chem['spikes'].sum()}")

# --- Motor output: locomotion proxy ---
# Locomotion circuit: AVA/AVB/AVD/AVE drive backward/forward locomotion
backward_neurons = {"AVAL", "AVAR", "AVDL", "AVDR", "AVEL", "AVER"}
forward_neurons  = {"AVBL", "AVBR", "PVCL", "PVCR"}

def motor_output(result, neurons):
    bwd_idx = [i for i, n in enumerate(neurons) if n in backward_neurons]
    fwd_idx = [i for i, n in enumerate(neurons) if n in forward_neurons]
    bwd_rate = result["spike_rate"][bwd_idx].mean() if bwd_idx else 0
    fwd_rate = result["spike_rate"][fwd_idx].mean() if fwd_idx else 0
    return bwd_rate, fwd_rate

tap_bwd, tap_fwd = motor_output(result_tap, neurons)
chem_bwd, chem_fwd = motor_output(result_chem, neurons)

# --- Raster plot ---
fig, axes = plt.subplots(2, 1, figsize=(12, 8))
T_steps = int(T_ms / params.dt)
t_axis = np.arange(T_steps) * params.dt

for ax, result, title in [(axes[0], result_tap, "Tap Withdrawal Stimulus"),
                           (axes[1], result_chem, "Chemotaxis Stimulus")]:
    spike_mat = result["spikes"]
    for i in range(N):
        ts = t_axis[spike_mat[:, i]]
        if len(ts) > 0:
            ax.scatter(ts, np.full_like(ts, i), s=0.5, c="black", linewidths=0)
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Neuron index")
    ax.set_title(title)
    ax.set_xlim(0, T_ms)

plt.tight_layout()
plt.savefig("simulation/results/baseline_raster.png", dpi=150)
plt.close()

# --- Summary ---
summary = f"""C. elegans LIF Baseline Simulation — Cook et al. 2019 Connectome
================================================================
Network: {N} neurons, {(W_norm>0).sum()} chemical synapses, {(G_norm>0).sum()} gap junctions

Parameters: tau_m={params.tau_m}ms, tau_syn={params.tau_syn}ms, V_thresh={params.V_thresh}
            w_chem={params.w_chem_scale}, w_gap={params.w_gap_scale}, dt={params.dt}ms

Simulation duration: {T_ms} ms

TAP WITHDRAWAL (tap at t=50ms, 20ms duration):
  Active neurons (>0.5 Hz): {tap_active}/{N} ({100*tap_active/N:.1f}%)
  Total spikes: {tap_total_spikes}
  Backward locomotion circuit (AVA/AVD/AVE) mean rate: {tap_bwd:.2f} Hz
  Forward locomotion circuit (AVB/PVC) mean rate: {tap_fwd:.2f} Hz
  Expected: tap -> backward locomotion -> AVA/AVD/AVE dominant ✓ if tap_bwd > tap_fwd

CHEMOTAXIS (tonic AWC/ASE input):
  Active neurons (>0.5 Hz): {chem_active}/{N} ({100*chem_active/N:.1f}%)
  Total spikes: {result_chem['spikes'].sum()}
  Backward locomotion circuit mean rate: {chem_bwd:.2f} Hz
  Forward locomotion circuit mean rate: {chem_fwd:.2f} Hz
  Expected: attractive odor -> forward locomotion -> AVB/PVC dominant ✓ if chem_fwd > chem_bwd

LOCOMOTION PREDICTION (tap_bwd > tap_fwd AND chem_fwd > chem_bwd):
  Tap: bwd={tap_bwd:.2f} vs fwd={tap_fwd:.2f} -> {'✓ BACKWARD (correct)' if tap_bwd > tap_fwd else '✗ FORWARD (unexpected)'}
  Chem: fwd={chem_fwd:.2f} vs bwd={chem_bwd:.2f} -> {'✓ FORWARD (correct)' if chem_fwd > chem_bwd else '✗ BACKWARD (unexpected)'}
"""

print(summary)
with open("simulation/results/baseline_summary.txt", "w") as f:
    f.write(summary)

print("Saved: simulation/results/baseline_raster.png")
print("Saved: simulation/results/baseline_summary.txt")
