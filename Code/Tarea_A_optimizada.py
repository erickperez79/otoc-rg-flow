"""
KAELION — Tarea A OPTIMIZADA: KI chaotic N=20,22,24
====================================================
Optimizaciones vs version original:
  1. D_MAX = 3N (saturacion ocurre antes de 3N en todos los modelos medidos)
  2. Reuso de buffers (reduce copias de vectores)
  3. Checkpoint incremental por N Y por estado aleatorio

Estimaciones (laptop i5 8GB):
  N=20: ~1h,  0.6 GB RAM
  N=22: ~5h,  1.0 GB RAM
  N=24: ~28h, 2.5 GB RAM
  Total: ~34h

W=Z_0, V=Z_1. J=1.0, h=0.5, b=0.5, OBC.

Run: python Tarea_A_optimizada.py
Output: ki_chaotic_large_N_opt.json (saves after each random state)
"""

import numpy as np
from scipy.optimize import curve_fit
import json
import time
import os

# ============================================
# CONFIGURATION
# ============================================
N_VALUES = [20, 22, 24]
N_RANDOM = 10
J, h, b = 1.0, 0.5, 0.5
OUTPUT_FILE = "ki_chaotic_large_N_opt.json"

# ============================================
# FLOQUET OPERATOR (state-vector, no matrices)
# ============================================

def precompute_zz_phases(N, J):
    dim = 2**N
    x = np.arange(dim)
    total_zz = np.zeros(dim, dtype=np.float64)
    for i in range(N - 1):
        bit_i = N - 1 - i
        bit_ip1 = N - 1 - (i + 1)
        zi = 1 - 2 * ((x >> bit_i) & 1)
        zip1 = 1 - 2 * ((x >> bit_ip1) & 1)
        total_zz += zi * zip1
    return np.exp(-1j * J * total_zz)

def precompute_z_phases(N, b):
    dim = 2**N
    x = np.arange(dim)
    total_z = np.zeros(dim, dtype=np.float64)
    for i in range(N):
        bit_i = N - 1 - i
        total_z += 1 - 2 * ((x >> bit_i) & 1)
    return np.exp(-1j * b * total_z)

def apply_x_rotation(psi, N, h):
    """Vectorized single-qubit X rotation — in-place where possible."""
    ch = np.cos(h)
    sh = -1j * np.sin(h)
    result = psi  # work in-place on input
    for i in range(N):
        bit = N - 1 - i
        mask = 1 << bit
        dim = len(result)
        indices = np.arange(dim)
        bit_val = (indices >> bit) & 1
        idx_0 = indices[bit_val == 0]
        idx_1 = idx_0 | mask
        v0 = result[idx_0].copy()
        v1 = result[idx_1].copy()
        result[idx_0] = ch * v0 + sh * v1
        result[idx_1] = sh * v0 + ch * v1
    return result

def apply_floquet(psi, N, zz_phases, z_phases, h, inverse=False):
    if not inverse:
        psi = zz_phases * psi
        psi = apply_x_rotation(psi, N, h)
        psi = z_phases * psi
    else:
        psi = z_phases.conj() * psi
        psi = apply_x_rotation(psi, N, -h)
        psi = zz_phases.conj() * psi
    return psi

def apply_Z_site(psi, N, site):
    bit = N - 1 - site
    dim = len(psi)
    x = np.arange(dim)
    signs = 1 - 2 * ((x >> bit) & 1)
    return signs * psi

# ============================================
# OTOC COMPUTATION (optimized)
# ============================================

def compute_otoc_single_state(psi, N, D_MAX, zz_phases, z_phases, h):
    """
    Compute C(d) for a single state.
    C(d) = <psi| (U^-d Z_0 U^d) Z_1 (U^-d Z_0 U^d) Z_1 |psi>
    
    Optimized: reuse buffers, minimal copies.
    """
    dim = 2**N
    C_vals = np.zeros(D_MAX + 1, dtype=complex)
    
    # |a> = Z_1 |psi>
    a_d = apply_Z_site(psi, N, 1).copy()  # a_0; will be evolved incrementally
    
    for d in range(D_MAX + 1):
        if d > 0:
            a_d = apply_floquet(a_d, N, zz_phases, z_phases, h)
        
        # |b> = Z_0 |a_d>
        buf = apply_Z_site(a_d, N, 0)
        
        # backward d steps
        for _ in range(d):
            buf = apply_floquet(buf, N, zz_phases, z_phases, h, inverse=True)
        
        # Z_1
        buf = apply_Z_site(buf, N, 1)
        
        # forward d steps
        for _ in range(d):
            buf = apply_floquet(buf, N, zz_phases, z_phases, h)
        
        # Z_0
        buf = apply_Z_site(buf, N, 0)
        
        # backward d steps
        for _ in range(d):
            buf = apply_floquet(buf, N, zz_phases, z_phases, h, inverse=True)
        
        C_vals[d] = np.vdot(psi, buf)
    
    return C_vals

def compute_omega_from_C(C_values):
    C_abs = np.abs(C_values)
    C0 = C_abs[0]
    if C0 < 1e-15:
        return 1.0
    late = C_abs[len(C_abs) // 2:]
    return float(np.mean(late) / C0)

# ============================================
# CHECKPOINT
# ============================================

def load_checkpoint():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE) as f:
            return json.load(f)
    return {"existing": {
        "4": 0.2801, "6": 0.2151, "8": 0.1587, "10": 0.1348,
        "12": 0.1189, "14": 0.1027, "16": 0.0907, "18": 0.0814
    }, "new": {}}

def save_checkpoint(results):
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

# ============================================
# MAIN
# ============================================

results = load_checkpoint()
total_start = time.time()

for N in N_VALUES:
    N_str = str(N)
    D_MAX = 3 * N  # OPTIMIZED: 3N instead of 5N
    dim = 2**N
    mem_mb = dim * 16 / 1e6
    
    # Check if already completed
    if N_str in results["new"] and results["new"][N_str].get("complete", False):
        print(f"\nN={N}: already completed (checkpoint). Skipping.")
        continue
    
    print(f"\n{'='*60}")
    print(f"KI chaotic N={N}, dim={dim:,}, D_MAX={D_MAX} (3N)")
    print(f"Memory per vector: {mem_mb:.0f} MB")
    print(f"Estimated time: see header")
    print(f"{'='*60}")
    
    t0 = time.time()
    
    # Precompute phases
    print("  Precomputing phases...", flush=True)
    zz_phases = precompute_zz_phases(N, J)
    z_phases = precompute_z_phases(N, b)
    print(f"  Phases done ({time.time()-t0:.0f}s)", flush=True)
    
    # Load partial results for this N
    n_completed = 0
    C_accumulated = np.zeros(D_MAX + 1, dtype=complex)
    if N_str in results["new"] and "partial_C_real" in results["new"][N_str]:
        partial = results["new"][N_str]
        n_completed = partial["states_completed"]
        C_accumulated = np.array(partial["partial_C_real"]) + 1j * np.array(partial["partial_C_imag"])
        print(f"  Resuming from state {n_completed}/{N_RANDOM}")
    
    np.random.seed(42)
    # Skip already-computed states
    for _ in range(n_completed):
        _ = np.random.randn(dim) + 1j * np.random.randn(dim)
    
    for k in range(n_completed, N_RANDOM):
        t_state = time.time()
        
        psi = np.random.randn(dim) + 1j * np.random.randn(dim)
        psi /= np.linalg.norm(psi)
        
        C_k = compute_otoc_single_state(psi, N, D_MAX, zz_phases, z_phases, h)
        C_accumulated += C_k
        
        elapsed_state = time.time() - t_state
        elapsed_total = time.time() - t0
        
        # Current estimate
        C_avg_so_far = C_accumulated / (k + 1)
        omega_so_far = compute_omega_from_C(C_avg_so_far)
        
        remaining = (N_RANDOM - k - 1) * elapsed_state
        print(f"  state {k+1}/{N_RANDOM}: Omega={omega_so_far:.8f} "
              f"({elapsed_state:.0f}s this state, {elapsed_total/60:.0f}min total, "
              f"~{remaining/60:.0f}min remaining)", flush=True)
        
        # Save checkpoint after each state
        results["new"][N_str] = {
            "N": N, "D_MAX": D_MAX, "n_random": N_RANDOM,
            "states_completed": k + 1,
            "omega_current": omega_so_far,
            "partial_C_real": C_accumulated.real.tolist(),
            "partial_C_imag": C_accumulated.imag.tolist(),
            "time_so_far_s": elapsed_total,
            "complete": False,
        }
        save_checkpoint(results)
    
    # Final result
    C_avg = C_accumulated / N_RANDOM
    omega = compute_omega_from_C(C_avg)
    elapsed = time.time() - t0
    
    print(f"\n  N={N}: Omega_late = {omega:.8f} ({elapsed:.0f}s = {elapsed/3600:.1f}h)")
    
    results["new"][N_str] = {
        "N": N, "D_MAX": D_MAX, "n_random": N_RANDOM,
        "omega_late": omega, "time_s": elapsed,
        "complete": True,
    }
    save_checkpoint(results)

# ============================================
# FITS (all points: existing + new)
# ============================================

def algebraic(N, A, c):
    return 1.0 / (1.0 + A * N**c)
def powerlaw(N, B, alpha):
    return B * N**(-alpha)

all_N = []
all_Om = []
for n_str, om in sorted(results["existing"].items(), key=lambda x: int(x[0])):
    all_N.append(int(n_str))
    all_Om.append(om)
for n_str, data in sorted(results["new"].items(), key=lambda x: int(x[0])):
    if data.get("complete"):
        all_N.append(int(n_str))
        all_Om.append(data["omega_late"])

Ns = np.array(all_N, dtype=float)
Om = np.array(all_Om)

print(f"\n{'='*60}")
print(f"FITS ({len(Ns)} points, N={int(Ns[0])}-{int(Ns[-1])})")
print(f"{'='*60}")
for n_val, o in zip(Ns, Om):
    print(f"  N={int(n_val):2d}: {o:.8f}")

n_pts = len(Ns)
try:
    pa, _ = curve_fit(algebraic, Ns, Om, p0=[0.6, 1.0], maxfev=10000)
    pp, _ = curve_fit(powerlaw, Ns, Om, p0=[0.9, 0.8], maxfev=10000)
    ss_a = np.sum((Om - algebraic(Ns, *pa))**2)
    ss_p = np.sum((Om - powerlaw(Ns, *pp))**2)
    ss_tot = np.sum((Om - np.mean(Om))**2)
    aic_a = n_pts * np.log(ss_a / n_pts) + 4
    aic_p = n_pts * np.log(ss_p / n_pts) + 4
    
    print(f"\n  Algebraic: c={pa[1]:.4f}, A={pa[0]:.4f}, R2={1-ss_a/ss_tot:.6f}")
    print(f"  Power-law: alpha={pp[1]:.4f}, R2={1-ss_p/ss_tot:.6f}")
    print(f"  dAIC = {aic_a - aic_p:.2f} (prev with N<=18: -3.30)")
    print(f"  Points: {n_pts} (prev: 8)")
    
    results["fits"] = {
        "algebraic": {"A": float(pa[0]), "c": float(pa[1]), "R2": float(1-ss_a/ss_tot)},
        "powerlaw": {"B": float(pp[0]), "alpha": float(pp[1]), "R2": float(1-ss_p/ss_tot)},
        "delta_AIC": float(aic_a - aic_p),
        "n_points": n_pts,
    }
    save_checkpoint(results)
except Exception as e:
    print(f"\n  Fit error: {e}")

total_time = time.time() - total_start
print(f"\nTotal time: {total_time/3600:.1f}h")
print(f"Saved: {OUTPUT_FILE}")
