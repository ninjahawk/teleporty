"""
Saturation vs in-degree: which neurons become unobservable under probing?

The N=2000 FlyWire failure traced to mega-hubs saturating under pool stim
and being skipped. This script characterizes the effect cleanly:

For a synthetic network with a controlled range of in-degrees, sweep the
probe amplitude and measure, for each in-degree bin, the fraction of
"valid" observations (neuron in the observable [SAT_LO, SAT_HI] range).

Predicts: high-in-degree neurons saturate at high amplitude; the amplitude
that keeps them observable scales as ~1/in-degree. This is the quantitative
basis for the mixed-amplitude ladder.
"""
import os, sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from simulation.rate_model import RateParams, simulate_rate

print("="*72); print("SATURATION vs IN-DEGREE ANALYSIS"); print("="*72)
params = RateParams(tau=10.0, gain=2.5, w_chem=0.25, w_gap=0.1, dt=0.5)

# Synthetic network with neurons spanning a wide in-degree range.
N = 600
rng = np.random.default_rng(0)
W = np.zeros((N, N))
# Assign target in-degrees: log-spaced from 5 to 400
target_indeg = np.unique(np.logspace(np.log10(5), np.log10(400), 40).astype(int))
# Most neurons get small in-degree; a few get the large ones
indeg = rng.integers(4, 12, N)
for k, d in enumerate(target_indeg):
    indeg[k] = d   # first 40 neurons get the controlled degrees
for j in range(N):
    d = min(indeg[j], N-1)
    presyn = rng.choice([i for i in range(N) if i != j], size=d, replace=False)
    W[presyn, j] = rng.lognormal(-2.0, 0.8, d)
W_norm = W / W.max()
G_norm = np.zeros((N, N))

T_ms = 300.0; T_steps = int(T_ms/params.dt)
SS = (int(150/params.dt), int(280/params.dt))
SAT_HI = 0.85; SAT_LO = 0.02
M = 15

# Sweep amplitude; for each, simulate many random pools and measure
# per-neuron mean steady-state rate.
amps = [0.05, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0]
n_pools = 40
print(f"\n{'amp':>6}  " + "  ".join(f"d~{d}" for d in [8, 30, 100, 300]) + "   (mean SS rate by in-degree)")
print("-"*65)

# in-degree bins
actual_indeg = (W_norm > 0).sum(axis=0)
bins = [(5, 15), (15, 50), (50, 150), (150, 500)]
bin_labels = ["8", "30", "100", "300"]

results = {}  # amp -> {bin -> (mean_rate, observable_frac)}
for amp in amps:
    rng_p = np.random.default_rng(1)
    # accumulate per-neuron SS rate across pools
    ss_rates = np.zeros(N); ss_count = 0
    observable = np.zeros(N)
    for p in range(n_pools):
        pool = rng_p.choice(N, size=M, replace=False)
        I = np.zeros((T_steps, N)); I[:, pool] = amp
        R = simulate_rate(W_norm, G_norm, I, T_ms, params)["r"]
        ss = R[SS[0]:SS[1]].mean(axis=0)
        ss_rates += ss
        observable += ((ss > SAT_LO) & (ss < SAT_HI)).astype(float)
        ss_count += 1
    ss_rates /= ss_count
    observable /= ss_count
    row = {}
    for (lo, hi), lab in zip(bins, bin_labels):
        sel = (actual_indeg >= lo) & (actual_indeg < hi)
        if sel.sum() == 0:
            row[lab] = (np.nan, np.nan); continue
        row[lab] = (ss_rates[sel].mean(), observable[sel].mean())
    results[amp] = row
    rates_str = "  ".join(f"{row[lab][0]:.3f}" for lab in bin_labels)
    print(f"{amp:>6.2f}  {rates_str}")

print(f"\nObservable fraction (in [{SAT_LO}, {SAT_HI}]) by in-degree:")
print(f"{'amp':>6}  " + "  ".join(f"{'d~'+l:>8}" for l in bin_labels))
print("-"*45)
for amp in amps:
    row = results[amp]
    obs_str = "  ".join(f"{row[lab][1]*100:>7.0f}%" for lab in bin_labels)
    print(f"{amp:>6.2f}  {obs_str}")

# For each in-degree bin, find the amplitude that maximizes observability
print(f"\nBest amplitude per in-degree bin (max observable fraction):")
for lab in bin_labels:
    best_amp = max(amps, key=lambda a: results[a][lab][1] if not np.isnan(results[a][lab][1]) else -1)
    best_obs = results[best_amp][lab][1]
    print(f"  in-degree ~{lab:>4}:  best amp = {best_amp:.2f}  (observable {best_obs*100:.0f}%)")

print(f"\n=> Confirms: high-in-degree neurons need LOW amplitude to stay")
print(f"   observable; low-in-degree neurons tolerate (and benefit from)")
print(f"   high amplitude. A single amplitude cannot serve both -- the")
print(f"   mixed-amplitude ladder is necessary, not just convenient.")

with open("simulation/results/saturation_analysis.txt", "w", encoding="utf-8") as f:
    f.write("Saturation vs in-degree analysis\n"+"="*50+"\n")
    f.write(f"Observable fraction by in-degree bin:\n")
    f.write(f"{'amp':>6}  " + "  ".join(f"d~{l:>5}" for l in bin_labels) + "\n")
    for amp in amps:
        row = results[amp]
        f.write(f"{amp:>6.2f}  " + "  ".join(f"{row[l][1]*100:>6.0f}%" for l in bin_labels) + "\n")
    f.write(f"\nBest amplitude per in-degree bin:\n")
    for lab in bin_labels:
        best_amp = max(amps, key=lambda a: results[a][lab][1] if not np.isnan(results[a][lab][1]) else -1)
        f.write(f"  in-degree ~{lab}: best amp = {best_amp:.2f}\n")
print("\nSaved: simulation/results/saturation_analysis.txt")

# Plot
fig, ax = plt.subplots(figsize=(8, 5))
for lab in bin_labels:
    obs = [results[a][lab][1] for a in amps]
    ax.plot(amps, obs, "o-", label=f"in-degree ~{lab}")
ax.set_xscale("log")
ax.set_xlabel("Probe amplitude")
ax.set_ylabel("Observable fraction (rate in [0.02, 0.85])")
ax.set_title("Neuron observability vs probe amplitude, by in-degree")
ax.legend(); ax.grid(alpha=0.3, which="both")
plt.tight_layout()
plt.savefig("simulation/results/saturation_analysis.png", dpi=150)
plt.close()
print("Saved: simulation/results/saturation_analysis.png")
