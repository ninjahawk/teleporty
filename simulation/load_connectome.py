"""
Load and clean the Cook et al. 2019 C. elegans connectome.
Returns normalized weight matrix W and neuron names.
"""

import re
import numpy as np
import pandas as pd


def is_neuron(name: str) -> bool:
    if not isinstance(name, str):
        return False
    return bool(re.match(r'^[A-Z][A-Z0-9]{1,6}$', name.strip()))


def load_connectome(data_dir: str = "simulation/data") -> tuple[np.ndarray, list[str], np.ndarray]:
    """
    Returns:
        W_raw   : (N, N) float array — raw synapse section counts, pre->post
        neurons : list of N neuron names
        W_norm  : (N, N) float array — weights normalized to [0, 1] by max weight
    """
    path = f"{data_dir}/SI5_connectome_adjacency.xlsx"
    df = pd.read_excel(path, sheet_name="hermaphrodite chemical", header=None)

    col_names = df.iloc[2, 3:].values
    row_names = df.iloc[3:, 2].values

    valid_col_idx = [i + 3 for i, n in enumerate(col_names) if is_neuron(str(n).strip())]
    valid_col_names = [str(col_names[i - 3]).strip() for i in valid_col_idx]
    valid_row_idx = [i + 3 for i, n in enumerate(row_names) if is_neuron(str(n).strip())]
    valid_row_names = [str(row_names[i - 3]).strip() for i in valid_row_idx]

    data = df.iloc[valid_row_idx, :].iloc[:, valid_col_idx]
    data = data.fillna(0).astype(float)
    data.index = valid_row_names
    data.columns = valid_col_names

    common = sorted(set(valid_row_names) & set(valid_col_names))
    W_raw = data.loc[common, common].values.astype(float)
    W_norm = W_raw / W_raw.max()

    return W_raw, common, W_norm


def load_gap_junctions(data_dir: str = "simulation/data") -> tuple[np.ndarray, list[str]]:
    """
    Returns gap junction weight matrix aligned to the same neuron set as chemical synapses.
    """
    path = f"{data_dir}/SI5_connectome_adjacency.xlsx"
    df = pd.read_excel(path, sheet_name="hermaphrodite gap jn symmetric", header=None)

    col_names = df.iloc[2, 3:].values
    row_names = df.iloc[3:, 2].values

    valid_col_idx = [i + 3 for i, n in enumerate(col_names) if is_neuron(str(n).strip())]
    valid_col_names = [str(col_names[i - 3]).strip() for i in valid_col_idx]
    valid_row_idx = [i + 3 for i, n in enumerate(row_names) if is_neuron(str(n).strip())]
    valid_row_names = [str(row_names[i - 3]).strip() for i in valid_row_idx]

    data = df.iloc[valid_row_idx, :].iloc[:, valid_col_idx]
    data = data.fillna(0).astype(float)
    data.index = valid_row_names
    data.columns = valid_col_names

    common = sorted(set(valid_row_names) & set(valid_col_names))
    G_raw = data.loc[common, common].values.astype(float)
    return G_raw, common


if __name__ == "__main__":
    import os
    os.chdir("C:/Users/jedin/Desktop/teleporty")
    W_raw, neurons, W_norm = load_connectome()
    G_raw, _ = load_gap_junctions()
    print(f"Neurons: {len(neurons)}")
    print(f"Chemical synapses — nonzero: {(W_raw > 0).sum()}, max: {W_raw.max():.0f}, mean(nz): {W_raw[W_raw>0].mean():.2f}")
    print(f"Gap junctions — nonzero: {(G_raw > 0).sum()}, max: {G_raw.max():.0f}")
    print(f"First 5 neurons: {neurons[:5]}")
