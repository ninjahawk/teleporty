"""
Firing rate model for C. elegans connectome.

Standard continuous rate model (Wilson-Cowan style):
    tau * dr_i/dt = -r_i + tanh( gain * (sum_j W_ij * r_j + I_ext_i) )

This model:
- Does not require excitatory/inhibitory sign classification (tanh bounds output)
- Is the standard approach for C. elegans circuit analysis (Kato et al. 2015,
  Iino & Yoshida 2009, Kunert et al. 2014)
- Sufficient for distortion experiments: behavioral metric is population activity

Gap junctions contribute bidirectional coupling:
    I_gap_i = g * sum_j G_ij * (r_j - r_i)

Units: dimensionless (r in [0,1] via tanh, t in ms).
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class RateParams:
    tau: float = 10.0         # time constant (ms)
    gain: float = 1.5         # sigmoid gain
    bias: float = 0.0         # neuron bias (threshold shift)
    w_chem: float = 1.0       # chemical synapse global scale
    w_gap: float = 0.3        # gap junction global scale
    dt: float = 0.5           # integration timestep (ms)


def simulate_rate(
    W_norm: np.ndarray,
    G_norm: np.ndarray,
    I_ext: np.ndarray,
    T_ms: float,
    params: RateParams = None,
) -> dict:
    """
    Run rate model simulation.

    Args:
        W_norm  : (N, N) chemical synapse weights, normalized, W[pre, post]
        G_norm  : (N, N) gap junction weights, normalized, symmetric
        I_ext   : (T_steps, N) external current; T_steps = int(T_ms / params.dt)
        T_ms    : simulation duration in ms
        params  : RateParams

    Returns dict:
        r       : (T_steps, N) firing rate traces (in [0, 1])
        r_mean  : (N,) time-averaged firing rate
    """
    if params is None:
        params = RateParams()

    N = W_norm.shape[0]
    T_steps = int(T_ms / params.dt)
    dt = params.dt

    W = W_norm * params.w_chem    # (N_pre, N_post)
    G = G_norm * params.w_gap

    R = np.zeros((T_steps, N))
    r = np.zeros(N)

    for t in range(T_steps):
        # Chemical synaptic input to each neuron: sum over presynaptic rates
        I_chem = W.T @ r           # I_chem[j] = sum_i r[i] * W[i,j]

        # Gap junction: bidirectional current proportional to rate difference
        I_gap = G @ r - G.sum(axis=1) * r  # sum_j G[i,j]*(r[j]-r[i])

        # External input
        I_in = I_ext[t] if I_ext is not None else 0.0

        # Total drive
        h = I_chem + I_gap + I_in + params.bias

        # Forward Euler update
        dr = dt / params.tau * (-r + np.tanh(params.gain * h))
        r = np.clip(r + dr, 0.0, 1.0)

        R[t] = r

    return {
        "r": R,
        "r_mean": R.mean(axis=0),
    }


def simulate_rate_sparse(
    W_norm,
    G_norm,
    I_ext: np.ndarray,
    T_ms: float,
    params: RateParams = None,
) -> dict:
    """
    Sparse-matrix version of simulate_rate. Identical dynamics, but the
    chemical/gap matmuls use scipy.sparse, giving ~1/density speedup on the
    per-timestep W.T @ r product.

    For a connectome with density d, the dense matmul is O(N^2); the sparse
    version is O(d*N^2) = O(nnz). FlyWire neuropils have d ~ 0.004, a ~250x
    speedup. This makes N >= 10^4 simulations tractable.

    Args:
        W_norm  : (N, N) scipy.sparse or dense — chemical weights, W[pre, post]
        G_norm  : (N, N) scipy.sparse or dense — gap junctions, symmetric
        I_ext   : (T_steps, N) external current
        T_ms    : duration in ms
        params  : RateParams

    Returns dict: r (T_steps, N), r_mean (N,)
    """
    import scipy.sparse as sp
    if params is None:
        params = RateParams()

    N = W_norm.shape[0]
    T_steps = int(T_ms / params.dt)
    dt = params.dt

    # Scale; keep sparse if input is sparse
    W = (W_norm * params.w_chem)
    G = (G_norm * params.w_gap)
    W = sp.csr_matrix(W) if not sp.issparse(W) else W.tocsr()
    G = sp.csr_matrix(G) if not sp.issparse(G) else G.tocsr()
    # W.T @ r needs W transposed in CSR for fast matvec
    Wt = W.T.tocsr()
    G_rowsum = np.asarray(G.sum(axis=1)).flatten()

    R = np.zeros((T_steps, N))
    r = np.zeros(N)
    gain = params.gain
    inv_tau = dt / params.tau

    for t in range(T_steps):
        I_chem = Wt @ r                          # sum_i r[i] * W[i,j]
        I_gap = (G @ r) - G_rowsum * r           # sum_j G[i,j]*(r[j]-r[i])
        I_in = I_ext[t] if I_ext is not None else 0.0
        h = I_chem + I_gap + I_in + params.bias
        dr = inv_tau * (-r + np.tanh(gain * h))
        r = np.clip(r + dr, 0.0, 1.0)
        R[t] = r

    return {"r": R, "r_mean": R.mean(axis=0)}


def make_tap_input(N: int, neuron_names: list, T_ms: float, dt: float,
                   onset_ms: float = 50.0, duration_ms: float = 20.0,
                   amplitude: float = 3.0) -> np.ndarray:
    T_steps = int(T_ms / dt)
    I = np.zeros((T_steps, N))
    tap_neurons = {"ALML", "ALMR", "AVM", "PLML", "PLMR", "PVM"}
    onset = int(onset_ms / dt)
    end = int((onset_ms + duration_ms) / dt)
    for i, n in enumerate(neuron_names):
        if n in tap_neurons:
            I[onset:end, i] = amplitude
    return I


def make_chem_input(N: int, neuron_names: list, T_ms: float, dt: float,
                    amplitude: float = 2.0) -> np.ndarray:
    T_steps = int(T_ms / dt)
    I = np.zeros((T_steps, N))
    chem_neurons = {"AWCL", "AWCR", "ASEL", "ASER"}
    for i, n in enumerate(neuron_names):
        if n in chem_neurons:
            I[:, i] = amplitude
    return I


def behavioral_vector(result: dict, neuron_names: list) -> np.ndarray:
    """
    Extract a low-dimensional behavioral summary from a simulation result.

    Returns a 4-element vector:
      [mean_backward_rate, mean_forward_rate, mean_turn_rate, mean_sensory_rate]

    Locomotion circuit assignments (Chalfie & White 1988, Gray et al. 2005):
      Backward drive:  AVA, AVD, AVE (command interneurons, drive backward motor neurons)
      Forward drive:   AVB, PVC      (command interneurons, drive forward motor neurons)
      Turn / omega:    RIV, RIB, AIB (omega bends and turns)
      Sensory:         AWC, ASE, AFD (sensory integration)
    """
    backward_n = {"AVAL", "AVAR", "AVDL", "AVDR", "AVEL", "AVER"}
    forward_n  = {"AVBL", "AVBR", "PVCL", "PVCR"}
    turn_n     = {"RIVL", "RIVR", "AIBL", "AIBR", "RIBL", "RIBR"}
    sensory_n  = {"AWCL", "AWCR", "ASEL", "ASER", "AFDL", "AFDR"}

    r_mean = result["r_mean"]

    def group_rate(group):
        idx = [i for i, n in enumerate(neuron_names) if n in group]
        return r_mean[idx].mean() if idx else 0.0

    return np.array([
        group_rate(backward_n),
        group_rate(forward_n),
        group_rate(turn_n),
        group_rate(sensory_n),
    ])


def locomotion_direction(bvec: np.ndarray) -> str:
    bwd, fwd = bvec[0], bvec[1]
    if bwd > fwd * 1.2:
        return "backward"
    if fwd > bwd * 1.2:
        return "forward"
    return "neutral"
