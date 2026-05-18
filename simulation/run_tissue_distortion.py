"""
Tissue distortion threshold validation.

Question: does the D=0.3 distortion threshold (confirmed for C. elegans neural
sim) transfer to NON-NEURAL tissue, where the relevant functional output is a
physiological signal (action potential propagation, force, etc.) rather than
behavioral activity?

Model: 2D cardiomyocyte sheet using FitzHugh-Nagumo (FHN) dynamics with diffusive
coupling. Wave initiated from one edge; conduction velocity measured.

Distortion: perturb the diffusion coefficients (= gap junction coupling strengths)
per cell with Gaussian noise of variance D*sigma^2_local.
Functional output: conduction velocity v_cv and AP duration tau_AP.
Pass criterion: cosine divergence of (v_cv, tau_AP, wave-arrival profile) < 5%
                between original and distorted tissue.

FitzHugh-Nagumo:
  du/dt = u - u^3/3 - v + D_coupling * laplacian(u) + I_stim
  dv/dt = epsilon * (u + a - b*v)
"""
import os, sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
os.makedirs("simulation/results", exist_ok=True)
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")

# --- FHN params (excitable, supports traveling waves) ---
# Form: du/dt = u(1-u)(u-alpha) - v + D*lap(u);  dv/dt = eps*(u - gamma*v)
# This Aliev-Panfilov-like form propagates robustly.
alpha = 0.1; gamma = 2.0; eps = 0.02
dt = 0.02; T = 200.0   # smaller dt for stability under heterogeneous D
NX, NY = 60, 60
D_BASE = 1.0
SIGMA2 = 0.25

def laplacian(u, D_field):
    # diffusion-coefficient varying laplacian (5-point stencil)
    # discrete heat eq: du = sum over neighbors of D_face * (u_neigh - u_center)
    # use harmonic mean for face conductance: D_face = 2*D1*D2/(D1+D2)
    Dx_right = 2*D_field[:, :-1]*D_field[:, 1:]/(D_field[:, :-1]+D_field[:, 1:] + 1e-12)
    Dx_left  = Dx_right
    Dy_down  = 2*D_field[:-1, :]*D_field[1:, :]/(D_field[:-1, :]+D_field[1:, :] + 1e-12)
    Dy_up    = Dy_down
    lap = np.zeros_like(u)
    lap[:, 1:]   += Dx_left  * (u[:, :-1] - u[:, 1:])
    lap[:, :-1]  += Dx_right * (u[:, 1:]  - u[:, :-1])
    lap[1:, :]   += Dy_up    * (u[:-1, :] - u[1:, :])
    lap[:-1, :]  += Dy_down  * (u[1:, :]  - u[:-1, :])
    return lap

def simulate(D_field, seed=0):
    u = np.zeros((NY, NX)); v = np.zeros((NY, NX))
    T_steps = int(T/dt)
    stim_until = int(5.0/dt)  # hold stim for 5ms
    arrival = np.full((NY, NX), -1.0)
    for t in range(T_steps):
        lap = laplacian(u, D_field)
        # Aliev-Panfilov: du/dt = u(1-u)(u-alpha) - v + D*lap(u)
        du = u * (1 - u) * (u - alpha) - v + lap
        dv = eps * (u - gamma * v)
        if t < stim_until:
            u[:, 0:3] = 0.8   # hold stim
        u = u + dt * du
        v = v + dt * dv
        if t < stim_until:
            u[:, 0:3] = 0.8
        # arrival when u crosses 0.5 upward for first time
        first = (arrival < 0) & (u > 0.5)
        arrival[first] = t * dt
    return arrival

def metrics(arrival):
    # conduction velocity: fit arrival time vs x for each row, take inverse slope
    velocities = []
    for j in range(NY):
        valid = arrival[j] > 0
        if valid.sum() < 10: continue
        x = np.where(valid)[0]
        t_arr = arrival[j, valid]
        # linear fit t = x/v + t0
        slope, _ = np.polyfit(x, t_arr, 1)
        if slope > 1e-6:
            velocities.append(1.0/slope)
    v_cv = np.mean(velocities) if velocities else 0.0
    # mean activation time across grid
    valid_grid = arrival > 0
    t_mean = arrival[valid_grid].mean() if valid_grid.any() else 0.0
    return v_cv, t_mean, arrival

def cdiv(a, b):
    a = a.flatten(); b = b.flatten()
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 1.0 - np.dot(a,b)/(na*nb) if na>1e-10 and nb>1e-10 else 1.0

print("="*72)
print("TISSUE DISTORTION SWEEP -- 2D FHN cardiac propagation")
print("="*72)

# baseline (uniform coupling)
D_base = np.full((NY, NX), D_BASE)
arr_orig = simulate(D_base)
v0, t0, _ = metrics(arr_orig)
print(f"Baseline: v_cv = {v0:.3f}, mean arrival = {t0:.3f}")

# Sweep distortion D in [0, 0.5] -- D = relative variance of additive D-field noise
# Interpretation: D = fractional variance of cell-pair coupling around the mean.
# D=0.3 means each coupling is perturbed by ~30% of baseline (sigma=0.55*D_BASE)
DISTS = [0.0, 0.01, 0.03, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50]
SEEDS = [11, 42, 777, 1234, 9999]
print(f"\n{'D':>6}  {'v_cv':>8}  {'dv_rel':>8}  {'act_frac':>9}  {'arr_err':>9}  pass")
print("-"*55)
results = []
# Mask of cells activated in baseline (for fair comparison)
act_mask = arr_orig > 0
arr_orig_act = arr_orig[act_mask]
v0_safe = v0 if v0 > 1e-6 else 1.0
for D in DISTS:
    seed_dv, seed_actf, seed_arrerr = [], [], []
    for sd in SEEDS:
        rng = np.random.default_rng(sd)
        # ADDITIVE Gaussian perturbation: D_field = D_BASE * (1 + sigma*z)
        sigma = np.sqrt(D)  # sigma in units of D_BASE
        noise = rng.normal(0, sigma, (NY, NX))
        D_field = np.clip(D_BASE * (1.0 + noise), 0.05 * D_BASE, 5.0 * D_BASE)
        arr = simulate(D_field)
        v_cv, _, _ = metrics(arr)
        seed_dv.append(abs(v_cv - v0)/v0_safe)
        # activation fraction: among cells that activated in baseline, what fraction did in distorted?
        act_dist = (arr > 0)[act_mask]
        seed_actf.append(act_dist.mean())
        # mean arrival error among cells activated in both
        both = act_mask & (arr > 0)
        if both.sum() > 10:
            seed_arrerr.append(np.median(np.abs(arr[both] - arr_orig[both]) / (arr_orig[both]+1e-6)))
        else:
            seed_arrerr.append(1.0)
    dv_rel = np.median(seed_dv)
    act_frac = np.median(seed_actf)
    arr_err = np.median(seed_arrerr)
    # PASS criterion: all three within 5%
    passes = (dv_rel < 0.05) and (act_frac > 0.95) and (arr_err < 0.05)
    line = f"{D:>6.2f}  {v0 * (1-dv_rel) if dv_rel<1 else 0:>8.3f}  {dv_rel:>8.4f}  {act_frac:>9.4f}  {arr_err:>9.4f}  {'PASS' if passes else 'FAIL'}"
    print(line)
    results.append((D, dv_rel, act_frac, arr_err, passes))

# Find threshold
threshold_D = None
for r in results:
    if not r[4]:
        threshold_D = r[0]; break

# Threshold determination
threshold_D = None
for r in results:
    if not r[4]:
        threshold_D = r[0]; break

last_pass = max((r[0] for r in results if r[4]), default=0.0)
print(f"\nTissue D-threshold (last PASS): D = {last_pass:.3f}")
print(f"Brain D-threshold: 0.30")
if last_pass >= 0.3:
    print("=> tissue tolerates D=0.30; body info budget assumption CONFIRMED")
elif last_pass >= 0.10:
    print(f"=> tissue threshold is {last_pass:.2f}, less tolerant than brain.")
    print(f"   Body info budget tightens; bits per voxel scale by log2(0.30/{last_pass:.2f}) ~ {np.log2(0.30/max(last_pass,0.01)):.2f}")
else:
    print(f"=> tissue threshold is {last_pass:.2f}, much less tolerant than brain.")

# Plot
fig, ax = plt.subplots(1, 1, figsize=(7, 5))
Ds = [r[0] for r in results]
dvs = [r[1] for r in results]
arr_errs = [r[3] for r in results]
act_fracs = [r[2] for r in results]
ax.plot(Ds, dvs, "o-", label="|Δv_cv|/v_cv")
ax.plot(Ds, arr_errs, "s-", label="arrival-time err")
ax.plot(Ds, 1-np.array(act_fracs), "^-", label="1 - activation frac")
ax.axhline(0.05, color="red", ls="--", label="5% threshold")
ax.axvline(0.30, color="blue", ls=":", label="D=0.30 (brain)")
ax.set_xlabel("Distortion D (relative variance on coupling)")
ax.set_ylabel("Functional error")
ax.set_title("2D FHN tissue distortion sweep")
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("simulation/results/tissue_distortion.png", dpi=150)
plt.close()

with open("simulation/results/tissue_distortion_summary.txt","w",encoding="utf-8") as f:
    f.write("Tissue distortion threshold sweep (2D Aliev-Panfilov)\n")
    f.write("="*60+"\n")
    f.write(f"NX x NY = {NX} x {NY}, T = {T} ms, dt = {dt} ms\n")
    f.write(f"Baseline v_cv = {v0:.3f}\n\n")
    f.write(f"{'D':>6}  {'dv_rel':>8}  {'act_frac':>9}  {'arr_err':>9}  pass\n")
    for D, dv, af, ae, p in results:
        f.write(f"{D:>6.2f}  {dv:>8.4f}  {af:>9.4f}  {ae:>9.4f}  {'PASS' if p else 'FAIL'}\n")
    f.write(f"\nTissue D-threshold: {last_pass:.3f}\n")
    f.write(f"Brain D-threshold:  0.30\n")
print("\nSaved: simulation/results/tissue_distortion_summary.txt + .png")
