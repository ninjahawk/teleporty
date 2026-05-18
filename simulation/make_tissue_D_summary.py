"""
Summary figure: all tissue D-thresholds + body budget contribution.

Pulls together cardiac (0.05), skeletal muscle (1.0), vascular (0.001),
brain (0.3), and the inferred values for other tissues.
"""
import os, sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
os.makedirs("simulation/results", exist_ok=True)

# Data
tissues = [
    ("Vasculature",         0.001, 0.05,  "tomato"),    # 5% body volume
    ("Cardiac muscle",      0.05,  0.005, "orange"),    # 0.5% (heart is small)
    ("Brain (neural)",      0.30,  0.02,  "steelblue"), # 2% volume, but functional info
    ("Smooth muscle (est.)",0.30,  0.05,  "lightblue"), # ~5%
    ("Epithelia/glands",    0.30,  0.20,  "skyblue"),   # ~20%
    ("Skeletal muscle",     1.00,  0.30,  "green"),     # ~30%
    ("Bone/connective/fat", 1.00,  0.35,  "tan"),       # ~35%
]

# Bits per block at R(D)
def bits_per_block(D):
    if D >= 1.0: return 0.0
    return 0.5 * np.log2(1.0/D)

# Plot 1: D-threshold per tissue (log scale)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
names = [t[0] for t in tissues]
Ds = [t[1] for t in tissues]
colors = [t[3] for t in tissues]
xs = np.arange(len(names))
bars = ax.barh(xs, Ds, color=colors, edgecolor="black")
ax.set_yticks(xs); ax.set_yticklabels(names)
ax.set_xscale("log")
ax.set_xlabel("D-threshold (relative variance tolerance)")
ax.set_title("Tissue distortion thresholds (functional equivalence)")
ax.axvline(0.05, color="black", ls="--", lw=0.5, alpha=0.5, label="cardiac ref")
ax.invert_yaxis(); ax.grid(alpha=0.3, axis="x", which="both")
for i, D in enumerate(Ds):
    ax.text(D*1.3, i, f"D={D}", va="center", fontsize=9)

ax = axes[1]
volumes = [t[2] for t in tissues]
bits = [bits_per_block(t[1]) for t in tissues]
# Weighted average bits/voxel
total_vol = sum(volumes)
avg_bits = sum(b*v for b, v in zip(bits, volumes)) / total_vol
bars = ax.barh(xs, bits, color=colors, edgecolor="black")
ax.set_yticks(xs); ax.set_yticklabels(names)
ax.set_xlabel("Bits per independent block (R-D bound)")
ax.set_title(f"Information content (volume-weighted avg = {avg_bits:.3f} bits/block)")
ax.invert_yaxis(); ax.grid(alpha=0.3, axis="x")
for i, b in enumerate(bits):
    ax.text(b+0.05, i, f"{b:.2f}", va="center", fontsize=9)

plt.tight_layout()
plt.savefig("simulation/results/tissue_D_summary.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved: simulation/results/tissue_D_summary.png")

# Body budget total
N_indep = 5.6e11
state_bits = sum(b * v for b, v in zip(bits, volumes)) / total_vol * N_indep
type_bits = 3.0 * N_indep  # 3 bits type label per block
total_bits = state_bits + type_bits
print(f"\nBody budget (revised with vascular):")
print(f"  State bits (volume-weighted): {state_bits/8/1e9:.1f} GB")
print(f"  Type-label bits (3 per block): {type_bits/8/1e9:.1f} GB")
print(f"  Total bulk tissue: {total_bits/8/1e9:.1f} GB")
print(f"  + Adaptive immunity: 1 GB")
print(f"  + Other (vasc/epigenome/genome): 0.2 GB")
print(f"  Grand total: ~{total_bits/8/1e9 + 1.2:.0f} GB")

with open("simulation/results/tissue_D_summary.txt", "w", encoding="utf-8") as f:
    f.write("Tissue D-threshold summary\n"+"="*50+"\n\n")
    f.write(f"{'Tissue':<25}  {'D':>8}  {'Vol frac':>9}  {'Bits/block':>10}\n")
    f.write("-"*60+"\n")
    for (name, D, vol, _), b in zip(tissues, bits):
        f.write(f"{name:<25}  {D:>8.3f}  {vol:>9.2f}  {b:>10.2f}\n")
    f.write(f"\nVolume-weighted avg state bits: {avg_bits:.3f}\n")
    f.write(f"Body budget (state + type labels): ~{total_bits/8/1e9:.0f} GB\n")
    f.write(f"Plus immunity + misc: ~{total_bits/8/1e9 + 1.2:.0f} GB total\n")
print("Saved: simulation/results/tissue_D_summary.txt")
