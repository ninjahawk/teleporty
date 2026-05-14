"""
Leaky integrate-and-fire (LIF) network simulation for C. elegans.

Model per neuron i:
    tau * dV_i/dt = -V_i + sum_j W_ij * s_j(t) + G_ij*(V_j - V_i) + I_ext_i(t)

    spike: if V_i >= V_thresh -> emit spike, reset V_i = V_reset, enter refractory for t_ref

Synaptic current s_j(t): exponential decay after spike
    ds_j/dt = -s_j/tau_syn + delta(t - t_spike)

Units: V in mV (normalized), t in ms.

Key C. elegans parameters from Wicks et al. 1996, Karbowski et al. 2008:
- Membrane time constant: ~10 ms
- Synaptic time constant: ~5 ms
- Refractory period: ~2 ms
- Threshold: 1.0 (normalized), reset: 0.0
"""

import numpy as np
from dataclasses import dataclass, field


@dataclass
class LIFParams:
    tau_m: float = 10.0       # membrane time constant (ms)
    tau_syn: float = 5.0      # synaptic time constant (ms)
    tau_gap: float = 0.5      # gap junction coupling time constant (ms) — fast
    V_thresh: float = 1.0     # spike threshold (normalized)
    V_reset: float = 0.0      # post-spike reset
    t_ref: float = 2.0        # absolute refractory period (ms)
    dt: float = 0.1           # integration timestep (ms)
    w_chem_scale: float = 0.05  # scale chemical synapse weights
    w_gap_scale: float = 0.02   # scale gap junction weights


def simulate(
    W_norm: np.ndarray,
    G_norm: np.ndarray,
    I_ext: np.ndarray,
    T_ms: float,
    params: LIFParams = None,
    seed: int = 42,
) -> dict:
    """
    Run LIF simulation.

    Args:
        W_norm  : (N, N) chemical synapse weights, normalized [0,1], W[pre, post]
        G_norm  : (N, N) gap junction weights, normalized [0,1], symmetric
        I_ext   : (T_steps, N) external current array
        T_ms    : simulation duration in ms
        params  : LIFParams instance
        seed    : RNG seed for noise

    Returns dict with:
        V          : (T_steps, N) membrane voltages
        spikes     : (T_steps, N) boolean spike array
        spike_rate : (N,) mean firing rate over full simulation (Hz)
        s          : (T_steps, N) synaptic activation traces
    """
    if params is None:
        params = LIFParams()

    rng = np.random.default_rng(seed)
    N = W_norm.shape[0]
    T_steps = int(T_ms / params.dt)
    dt = params.dt

    W_chem = W_norm * params.w_chem_scale   # (N_pre, N_post)
    W_gap = G_norm * params.w_gap_scale

    V = np.zeros((T_steps, N))
    S = np.zeros((T_steps, N))   # synaptic activation
    spikes = np.zeros((T_steps, N), dtype=bool)

    v = np.zeros(N)   # current membrane voltage
    s = np.zeros(N)   # current synaptic activation
    ref_timer = np.zeros(N)  # refractory countdown

    exp_syn = np.exp(-dt / params.tau_syn)
    exp_mem = np.exp(-dt / params.tau_m)

    for t in range(T_steps):
        # Synaptic input: sum over presynaptic activations
        # W_chem[pre, post] -> post receives sum over pre
        I_chem = s @ W_chem.T    # (N,) — wait, W[pre,post] so post_j = sum_i s_i * W[i,j]
        I_chem = s @ W_chem      # (N,) : I_chem[j] = sum_i s[i] * W[i,j]  ✓

        # Gap junction: bidirectional
        # I_gap[i] = sum_j G[i,j] * (v[j] - v[i])
        I_gap = W_gap @ v - (W_gap.sum(axis=1) * v)

        # External input
        I_in = I_ext[t] if I_ext is not None else np.zeros(N)

        # LIF update (exponential Euler)
        dv = (-v + I_chem + I_gap + I_in) * (1 - exp_mem) / params.tau_m * params.tau_m
        # Simpler forward Euler:
        dv = dt / params.tau_m * (-v + I_chem + I_gap + I_in)
        v_new = v + dv

        # Refractory: clamp to reset if still in refractory
        in_ref = ref_timer > 0
        v_new[in_ref] = params.V_reset
        ref_timer = np.maximum(0, ref_timer - dt)

        # Spike detection
        fired = (v_new >= params.V_thresh) & (~in_ref)
        v_new[fired] = params.V_reset
        ref_timer[fired] = params.t_ref

        # Synaptic activation update (exponential decay + spike input)
        s = s * exp_syn + fired.astype(float)

        v = v_new
        V[t] = v
        S[t] = s
        spikes[t] = fired

    # Mean firing rate in Hz = spikes / (T_ms * 1e-3)
    spike_rate = spikes.sum(axis=0) / (T_ms * 1e-3)

    return {
        "V": V,
        "spikes": spikes,
        "spike_rate": spike_rate,
        "S": S,
    }


def make_tap_stimulus(N: int, neuron_names: list, T_ms: float, dt: float,
                      onset_ms: float = 50.0, duration_ms: float = 10.0,
                      amplitude: float = 2.0) -> np.ndarray:
    """
    Simulate a tap stimulus: strong input to ALM, AVM, PLM mechanosensory neurons.
    These drive the tap-withdrawal reflex (backward locomotion).
    """
    T_steps = int(T_ms / dt)
    I_ext = np.zeros((T_steps, N))

    # Mechanosensory neurons for tap withdrawal (Chalfie et al. 1985)
    tap_neurons = {"ALML", "ALMR", "AVM", "PLML", "PLMR", "PVM"}
    onset_step = int(onset_ms / dt)
    end_step = int((onset_ms + duration_ms) / dt)

    for i, name in enumerate(neuron_names):
        if name in tap_neurons:
            I_ext[onset_step:end_step, i] = amplitude

    return I_ext


def make_chemotaxis_stimulus(N: int, neuron_names: list, T_ms: float, dt: float,
                              amplitude: float = 1.5) -> np.ndarray:
    """
    Simulate chemotaxis: tonic input to AWC (attractive odor ON cell) and ASE neurons.
    """
    T_steps = int(T_ms / dt)
    I_ext = np.zeros((T_steps, N))

    # AWC and ASE are primary chemosensory neurons
    chem_neurons = {"AWCL", "AWCR", "ASEL", "ASER"}
    for i, name in enumerate(neuron_names):
        if name in chem_neurons:
            I_ext[:, i] = amplitude

    return I_ext
