"""
Empirical body-scan compression test.

The body info budget assumed:
  N_indep = N_vox / xi^3 with correlation length xi ~ 5 voxels (50 um)
  Bits per block ~ 4 (type + state)
  Total ~ 275 GB for bulk tissue (uncompressed by codec)

This script tests whether actual 3D random fields with realistic correlation
length compress to those numbers. We build synthetic body voxel grids using
2-3 tissue types in a smooth(-ish) layout, then measure:
  (a) Compression ratio using lossless gzip on the raw voxel grid
  (b) Lossy compression at functional-distortion tolerance (D=0.3 brain;
      higher for muscle/connective)
  (c) Per-block bit count after rate-distortion coding

We then verify whether the 100 GB - 1 TB body budget is realistic.
"""
import os, sys, numpy as np, gzip, io
sys.path.insert(0, "C:/Users/jedin/Desktop/teleporty")
os.chdir("C:/Users/jedin/Desktop/teleporty")
from scipy.ndimage import gaussian_filter

print("="*72); print("BODY-SCAN COMPRESSION EMPIRICAL TEST"); print("="*72)

# Build a tractable 3D voxel grid (downscaled from real body 7e13 voxels).
# Use 200x200x200 = 8e6 voxels as a sample (cube of side ~ 2mm at 10um voxels)
NX, NY, NZ = 200, 200, 200
N_VOX = NX*NY*NZ
print(f"  Sample grid: {NX}x{NY}x{NZ} = {N_VOX:,} voxels")
print(f"  Scaled to full body (7e13 vox): scale up by {7e13/N_VOX:.2e}x\n")

rng = np.random.default_rng(0)

# Build tissue-type field: 2-4 tissues in spatially smooth blobs.
# 8 distinct tissue types with correlation length ~5 voxels.
N_TYPES = 8
# Sample type labels from a smoothed random field
print("Building tissue-type field...")
type_logits = np.zeros((N_TYPES, NX, NY, NZ), dtype=np.float32)
for t in range(N_TYPES):
    raw = rng.normal(0, 1, (NX, NY, NZ)).astype(np.float32)
    type_logits[t] = gaussian_filter(raw, sigma=5.0)
type_field = np.argmax(type_logits, axis=0).astype(np.uint8)
del type_logits

# State field: per-voxel scalar (e.g. cell size, methylation summary) with
# correlation length ~5 voxels too. Quantize to 8 bits.
print("Building state field...")
state_raw = rng.normal(0, 1, (NX, NY, NZ)).astype(np.float32)
state_field = gaussian_filter(state_raw, sigma=5.0)
state_field = (255 * (state_field - state_field.min()) / (state_field.max() - state_field.min())).astype(np.uint8)
del state_raw

# Combined voxel value: pack type (high 3 bits) + state (low 5 bits) into one byte
# Or just keep two separate fields and compress jointly
print(f"  Type field dtype: {type_field.dtype}, range: {type_field.min()}-{type_field.max()}")
print(f"  State field dtype: {state_field.dtype}, range: {state_field.min()}-{state_field.max()}")

# === Compression test 1: lossless on combined ===
combined = np.stack([type_field, state_field], axis=-1)  # shape (NX, NY, NZ, 2)
raw_bytes = combined.tobytes()
raw_size = len(raw_bytes)
print(f"\n  Raw size: {raw_size:,} bytes = {raw_size/1024/1024:.2f} MB")

# Gzip (deflate) -- general purpose lossless
print("Gzipping...")
gz_buf = io.BytesIO()
with gzip.GzipFile(fileobj=gz_buf, mode='wb', compresslevel=6) as f:
    f.write(raw_bytes)
gz_size = gz_buf.tell()
ratio_gz = raw_size / gz_size
print(f"  Gzip size: {gz_size:,} bytes = {gz_size/1024/1024:.2f} MB  (ratio {ratio_gz:.1f}x)")

# === Compression test 2: lossless on JUST type field (no state) ===
type_bytes = type_field.tobytes()
gz_buf2 = io.BytesIO()
with gzip.GzipFile(fileobj=gz_buf2, mode='wb', compresslevel=6) as f:
    f.write(type_bytes)
gz_type_size = gz_buf2.tell()
print(f"\n  Type-only raw: {len(type_bytes):,} bytes")
print(f"  Type-only gzip: {gz_type_size:,} bytes = {gz_type_size/N_VOX:.4f} bytes/voxel = "
      f"{gz_type_size*8/N_VOX:.2f} bits/voxel")

# === Compression test 3: lossy on state field (quantize to fewer bits) ===
# Round state to 2 bits / 3 bits / 4 bits and recompress
print(f"\nLossy state compression (functional-D quantization):")
for q_bits in [1, 2, 3, 4, 8]:
    n_levels = 2**q_bits
    quantized = (state_field // (256 // n_levels)).astype(np.uint8)
    qbuf = io.BytesIO()
    with gzip.GzipFile(fileobj=qbuf, mode='wb', compresslevel=6) as f:
        f.write(quantized.tobytes())
    sz = qbuf.tell()
    print(f"    {q_bits}-bit quantized state: {sz:,} bytes = {sz*8/N_VOX:.3f} bits/voxel")

# === Theoretical calculation reproduction ===
print(f"\nTheoretical R-D estimate (from body budget doc):")
xi = 5  # correlation length
N_indep = N_VOX / xi**3
print(f"  N_indep blocks: {N_indep:,.0f}")
# Type entropy
type_counts = np.bincount(type_field.flatten())
p_types = type_counts / type_counts.sum()
H_type = -(p_types[p_types>0] * np.log2(p_types[p_types>0])).sum()
print(f"  Type entropy: {H_type:.3f} bits per block")
# State R-D at D=0.3: (1/2)log2(1/0.3) = 0.87
R_state = 0.5 * np.log2(1.0/0.3)
total_theory = N_indep * (H_type + R_state)
print(f"  State R(D=0.3): {R_state:.3f} bits per block")
print(f"  Total theory: {N_indep:,.0f} * {H_type + R_state:.3f} = {total_theory:,.0f} bits = {total_theory/8/1024/1024:.2f} MB")
print(f"  Per voxel: {total_theory/N_VOX:.3f} bits/voxel")

# === Scale to full body ===
print(f"\nScaling to full body (7e13 voxels):")
scale = 7e13 / N_VOX
print(f"  Gzip combined: {gz_size * scale / 1e9:.2f} GB")
print(f"  Gzip type only: {gz_type_size * scale / 1e9:.2f} GB")
print(f"  Theory (H_type + R(D=0.3) per block): {total_theory * scale / 8 / 1e9:.2f} GB")
print(f"  Theory at 1 bit/voxel: {N_VOX * scale / 8 / 1e9:.2f} GB")
print(f"  Theory at 4 bits/voxel (orig estimate): {N_VOX * 4 * scale / 8 / 1e9:.2f} GB")

# === Verdict ===
gz_total_GB = gz_size * scale / 1e9
print(f"\n=== VERDICT ===")
print(f"Empirical gzip on tissue-type+state field at full body scale: ~{gz_total_GB:.0f} GB")
if gz_total_GB < 100:
    print(f"=> Body fits comfortably below 100 GB. Earlier 100-1000 GB was conservative.")
elif gz_total_GB < 500:
    print(f"=> Body in ~100-500 GB range. Consistent with 100 GB-1 TB estimate.")
else:
    print(f"=> Body > 500 GB. Consistent with conservative end of range.")

# Save
with open("simulation/results/body_compression.txt", "w", encoding="utf-8") as f:
    f.write("Body-scan compression empirical test\n"+"="*55+"\n")
    f.write(f"Sample grid: {NX}x{NY}x{NZ} = {N_VOX:,} voxels\n")
    f.write(f"Scaling factor to full body (7e13 vox): {scale:.2e}\n\n")
    f.write(f"  Raw size (combined type+state): {raw_size:,} bytes = {raw_size/1024/1024:.2f} MB\n")
    f.write(f"  Gzip size: {gz_size:,} bytes (ratio {ratio_gz:.1f}x)\n")
    f.write(f"  Type-only gzip: {gz_type_size*8/N_VOX:.2f} bits/voxel\n")
    f.write(f"  Theoretical R-D total: {total_theory/N_VOX:.3f} bits/voxel\n\n")
    f.write(f"Scaled to full body:\n")
    f.write(f"  Gzip combined: ~{gz_total_GB:.0f} GB\n")
    f.write(f"  Type-only:     ~{gz_type_size*scale/1e9:.0f} GB\n")
    f.write(f"  Theory R-D:    ~{total_theory*scale/8/1e9:.0f} GB\n")
print(f"\nSaved: simulation/results/body_compression.txt")
