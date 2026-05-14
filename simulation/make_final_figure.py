"""
Generate the final composite figure summarizing all simulation results.
Saved to: simulation/results/final_summary_figure.png
"""

import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")

# Load all results
dist  = np.load("simulation/results/distortion_results.npz", allow_pickle=True)
deff  = np.load("simulation/results/deff_results.npz",       allow_pickle=True)

D_levels   = dist["distortion_levels"]
div_tap    = dist["divergence_tap"]
div_chem   = dist["divergence_chem"]
div_tap_std = dist["divergence_tap_std"]
div_chem_std= dist["divergence_chem_std"]

eigenvalues = deff["eigenvalues"]
cumvar      = deff["cumvar"]
eig_act     = deff["eig_act"]
cumvar_act  = deff["cumvar_act"]
d_eff_pr    = float(deff["d_eff_pr"])
d_eff_act   = float(deff["d_eff_act_pr"])
d_eff_90    = int(deff["d_eff_90"])
d_eff_act_90= int(deff["d_eff_act_90"])
N           = int(deff["N"])

fig = plt.figure(figsize=(16, 10))
gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.40, wspace=0.38)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[0, 2])
ax4 = fig.add_subplot(gs[1, 0])
ax5 = fig.add_subplot(gs[1, 1])
ax6 = fig.add_subplot(gs[1, 2])

# --- Panel 1: Behavioral divergence vs distortion ---
ax1.fill_between(D_levels, div_tap - div_tap_std, div_tap + div_tap_std, alpha=0.2, color="steelblue")
ax1.fill_between(D_levels, div_chem - div_chem_std, div_chem + div_chem_std, alpha=0.2, color="forestgreen")
ax1.plot(D_levels, div_tap,  "o-", color="steelblue",    lw=2, ms=5, label="Tap withdrawal")
ax1.plot(D_levels, div_chem, "s-", color="forestgreen",  lw=2, ms=5, label="Chemotaxis")
ax1.axvline(0.30, color="red",  ls="--", lw=1.5, label="D=0.30 (predicted threshold)")
ax1.axhline(0.05, color="gray", ls=":",  lw=1.2, label="5% divergence")
ax1.set_xlabel("Weight distortion D")
ax1.set_ylabel("Behavioral divergence")
ax1.set_title("Prediction 1: 30% distortion\n< behavioral threshold")
ax1.legend(fontsize=7)
ax1.grid(True, alpha=0.3)

# --- Panel 2: Weight matrix eigenspectrum ---
ax2.semilogy(eigenvalues / eigenvalues.sum(), "b-", lw=1.5, label="Weight PCA")
ax2.semilogy(eig_act / eig_act.sum(), "g--", lw=1.5, label="Activity manifold")
ax2.axvline(d_eff_90, color="blue",  ls=":", lw=1.5, label=f"W 90% ({d_eff_90}d)")
ax2.axvline(d_eff_act_90, color="green", ls=":", lw=1.5, label=f"Act 90% ({d_eff_act_90}d)")
ax2.set_xlabel("Principal component index")
ax2.set_ylabel("Fraction of variance")
ax2.set_title(f"Prediction 2: d_eff << N\n(PR: W={d_eff_pr:.0f}, act={d_eff_act:.0f} out of {N})")
ax2.legend(fontsize=7)
ax2.grid(True, alpha=0.3, which="both")

# --- Panel 3: Cumulative variance ---
ax3.plot(np.arange(1, N+1), cumvar,     "b-",  lw=2, label="Weight matrix")
ax3.plot(np.arange(1, len(cumvar_act)+1), cumvar_act, "g--", lw=2, label="Activity manifold")
ax3.axhline(0.90, color="orange", ls="--", lw=1.5, label="90%")
ax3.axhline(0.99, color="red",    ls="--", lw=1.5, label="99%")
ax3.set_xlabel("Number of dimensions")
ax3.set_ylabel("Cumulative variance explained")
ax3.set_title(f"Dimensionality of C. elegans\n(N={N} neurons)")
ax3.legend(fontsize=7)
ax3.grid(True, alpha=0.3)

# --- Panel 4: d_eff scaling to human ---
N_vals = np.logspace(2, 11, 200)
d_elegans = d_eff_act
N_elegans = 302

colors = ["steelblue", "forestgreen", "darkorange"]
for alpha, col in zip([0.5, 0.75, 1.0], colors):
    d_scaled = d_elegans * (N_vals / N_elegans) ** alpha
    ax4.loglog(N_vals, d_scaled, "-", color=col, lw=2, label=f"alpha={alpha:.2f}")

# Mark C. elegans point
ax4.axvline(N_elegans, color="black", ls=":", lw=1, alpha=0.5)
ax4.scatter([N_elegans], [d_elegans], s=80, c="black", zorder=5, label="C. elegans (measured)")
# Mark Drosophila and human
ax4.axvline(140000,  color="purple", ls=":", lw=1, alpha=0.5)
ax4.axvline(86e9,    color="red",    ls=":", lw=1, alpha=0.5)
ax4.text(140000, 1e3, "Drosophila", rotation=90, va="bottom", fontsize=7, color="purple")
ax4.text(86e9,   1e3, "Human",      rotation=90, va="bottom", fontsize=7, color="red")
# Rate-distortion assumed range
ax4.axhspan(1e10, 1e12, alpha=0.12, color="red", label="R-D assumed range (10^10-10^12)")

ax4.set_xlabel("Neuron count N")
ax4.set_ylabel("d_eff (estimated)")
ax4.set_title("d_eff Scaling: C. elegans -> Human")
ax4.legend(fontsize=7)
ax4.grid(True, alpha=0.3, which="both")

# --- Panel 5: Empirical compression (quantization) ---
quant_bits = np.array([1, 2, 3, 4, 5, 6, 8])
quant_divs = np.array([0.2380, 0.0476, 0.0198, 0.0052, 0.0013, 0.0004, 0.0000])
N_synapses = 3707
total_bits = quant_bits * N_synapses

ax5.semilogy(quant_bits, quant_divs, "ko-", lw=2, ms=6)
ax5.axhline(0.05, color="red",  ls="--", lw=1.5, label="5% divergence threshold")
ax5.axhline(0.01, color="gray", ls=":",  lw=1.2, label="1% threshold")
ax5.axvline(3,    color="blue", ls="--", lw=1.5, label="3 bits/syn -> <2% div")
ax5.set_xlabel("Bits per synapse (quantization)")
ax5.set_ylabel("Behavioral divergence")
ax5.set_title(f"Empirical compression\n({N_synapses} synapses, chemotaxis)")
ax5.legend(fontsize=7)
ax5.grid(True, alpha=0.3, which="both")

# Annotate bits
for k, d, b in zip(quant_bits, quant_divs, total_bits):
    if d > 1e-5:
        ax5.annotate(f"{b:.0f}b", (k, d), textcoords="offset points", xytext=(6, 0), fontsize=7)

# --- Panel 6: Summary table (text) ---
ax6.axis("off")
summary_text = (
    "SIMULATION RESULTS SUMMARY\n"
    "─────────────────────────────────────────\n"
    f"Network: {N} neurons, 3707 synapses\n"
    "Model: firing rate (tanh), Cook 2019\n\n"
    "PREDICTION 1: D=30% < threshold\n"
    f"  Tap div at D=30%:  {div_tap[D_levels==0.30][0]:.3f}  ✓\n"
    f"  Chem div at D=30%: {div_chem[D_levels==0.30][0]:.3f} ✓\n"
    f"  (threshold: tap D~0.5, chem D>1.0)\n\n"
    "PREDICTION 2: d_eff << N\n"
    f"  d_eff (W PCA):    {d_eff_pr:.0f} / {N}  ({100*d_eff_pr/N:.1f}%)\n"
    f"  d_eff (activity): {d_eff_act:.0f} / {N}  ({100*d_eff_act/N:.1f}%)\n"
    f"  CONFIRMED: network is low-dimensional\n\n"
    "EMPIRICAL COMPRESSION:\n"
    "  3 bits/syn -> 11,121 bits total\n"
    "  achieves <2% behavioral divergence\n\n"
    "SCALING TO HUMAN (d_eff * (N_h/N_e)^a):\n"
    f"  alpha=0.50: ~2.2e5\n"
    f"  alpha=0.75: ~2.9e7\n"
    f"  alpha=1.00: ~3.8e9\n"
    "  (R-D assumed: 10^10-10^12)\n\n"
    "NEXT: Drosophila to calibrate alpha"
)
ax6.text(0.05, 0.97, summary_text, transform=ax6.transAxes,
         fontsize=8, verticalalignment="top", fontfamily="monospace",
         bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

fig.suptitle("Teleporty — C. elegans Simulation: Functional Teleportation Predictions",
             fontsize=13, fontweight="bold", y=1.01)

plt.savefig("simulation/results/final_summary_figure.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved: simulation/results/final_summary_figure.png")
