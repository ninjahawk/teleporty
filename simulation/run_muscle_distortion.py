"""
Muscle distortion threshold.

Cardiac tissue D-threshold was 0.05 (cardiac is electrically excitable
and propagates waves; sensitive to coupling heterogeneity). Skeletal
muscle has a different functional output: FORCE PRODUCTION, which is a
parallel sum across fibers. Hypothesis: muscle is much more tolerant
to distortion than cardiac.

Model: a parallel bundle of N_fibers myosin/actin units. Each fiber produces
force F_i = f_max * activation(t) * alignment_i * cross_section_i.
Total force F(t) = sum_i F_i(t) (parallel bundle).

Distortion: perturb (f_max, alignment, cross_section) for each fiber.
Functional output: peak force production and force-time profile.
PASS: |F_peak - F0_peak|/F0_peak < 5% AND time-profile cos-divergence < 5%.
"""
import os, sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")

print("="*72); print("MUSCLE DISTORTION THRESHOLD"); print("="*72)
np.random.seed(0)
N_FIBERS = 1000  # ~ a small motor unit
T_MS = 200.0; DT = 1.0
T_STEPS = int(T_MS/DT)
t = np.arange(T_STEPS)*DT

# Activation curve: ramp up + plateau + relax
def activation(t):
    a = np.zeros_like(t, dtype=float)
    a[(t>=10) & (t<60)]  = (t[(t>=10)&(t<60)] - 10)/50.0       # ramp
    a[(t>=60) & (t<120)] = 1.0                                 # plateau
    a[(t>=120)& (t<180)] = 1.0 - (t[(t>=120)&(t<180)] - 120)/60.0
    return a
act = activation(t)

def fiber_params(seed, D):
    """Return f_max, alignment_cos, cross_section per fiber.
    D = relative variance applied multiplicatively.
    """
    rng = np.random.default_rng(seed)
    f_max = 1.0 + rng.normal(0, np.sqrt(D), N_FIBERS)
    f_max = np.clip(f_max, 0.1, 3.0)
    # alignment angle: distribution around 0 (perfectly aligned)
    angle_var = D * (np.pi/8)**2  # max ~22.5deg sigma at D=1
    angles = rng.normal(0, np.sqrt(angle_var), N_FIBERS)
    align = np.cos(angles)
    cs = 1.0 + rng.normal(0, np.sqrt(D)*0.5, N_FIBERS)
    cs = np.clip(cs, 0.1, 3.0)
    return f_max, align, cs

def total_force(f_max, align, cs):
    # F(t) = sum_i f_max_i * align_i * cs_i * act(t)
    per_fiber = f_max * align * cs   # (N_FIBERS,) baseline per-fiber force
    return act * per_fiber.sum()

f0, a0, c0 = fiber_params(0, 0.0)
F0 = total_force(f0, a0, c0)
F0_peak = F0.max()
print(f"Baseline peak force: {F0_peak:.3f}  (sum of {N_FIBERS} fibers)")

def cdiv(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 1.0 - np.dot(a,b)/(na*nb) if na>1e-10 and nb>1e-10 else 1.0

DISTS = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50, 1.00, 2.00]
SEEDS = [11, 42, 777, 1234, 9999]
print(f"\n{'D':>6}  {'F_peak':>9}  {'dF_rel':>9}  {'div_t':>9}  verdict")
print("-"*48)
results = []
for D in DISTS:
    dF_list, div_list = [], []
    for sd in SEEDS:
        f, a, c = fiber_params(sd, D)
        F = total_force(f, a, c)
        dF_list.append(abs(F.max() - F0_peak)/F0_peak)
        div_list.append(cdiv(F0, F))
    dF_med = np.median(dF_list)
    div_med = np.median(div_list)
    passes = (dF_med < 0.05) and (div_med < 0.05)
    line = f"{D:>6.2f}  {F0_peak*(1-dF_med):>9.2f}  {dF_med:>9.4f}  {div_med:>9.4f}  {'PASS' if passes else 'FAIL'}"
    print(line); results.append((D, dF_med, div_med, passes))

# Threshold
last_pass = max((r[0] for r in results if r[3]), default=0.0)
first_fail = next((r[0] for r in results if not r[3]), None)
print(f"\nMuscle D-threshold (last PASS): {last_pass:.2f}")
print(f"Cardiac D-threshold: 0.05")
if last_pass >= 0.3:
    print(f"=> muscle tolerates >= 6x MORE distortion than cardiac.")
    print(f"   Body budget can use D=0.30 for muscle voxels.")
    print(f"   Bits per muscle voxel: (1/2)log2(1/0.30) = 0.87, vs 2.16 (cardiac).")
    print(f"   Compression gain: 2.5x on muscle (largest non-fat body component).")

with open("simulation/results/muscle_distortion_summary.txt","w",encoding="utf-8") as f:
    f.write("Muscle distortion sweep (parallel fiber bundle, N=1000)\n"+"="*55+"\n")
    f.write(f"{'D':>6}  {'dF_rel':>9}  {'div_t':>9}  verdict\n")
    for D, df, dv, p in results:
        f.write(f"{D:>6.2f}  {df:>9.4f}  {dv:>9.4f}  {'PASS' if p else 'FAIL'}\n")
    f.write(f"\nMuscle D-threshold: {last_pass:.2f}\nCardiac D-threshold: 0.05\n")

# Plot
fig, ax = plt.subplots(figsize=(7, 5))
Ds = [r[0] for r in results]
dFs = [r[1] for r in results]
divs = [r[2] for r in results]
ax.plot(Ds, dFs, "o-", label="|ΔF_peak|/F_peak")
ax.plot(Ds, divs, "s-", label="cos div F(t)")
ax.axhline(0.05, color="red", ls="--", label="5% threshold")
ax.axvline(0.05, color="blue", ls=":", label="cardiac D=0.05")
ax.axvline(0.30, color="green", ls=":", label="brain D=0.30")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Distortion D"); ax.set_ylabel("Functional error")
ax.set_title("Muscle force production vs distortion")
ax.legend(); ax.grid(alpha=0.3, which="both")
plt.tight_layout()
plt.savefig("simulation/results/muscle_distortion.png", dpi=150)
plt.close()
print(f"\nSaved: simulation/results/muscle_distortion_summary.txt + .png")
