"""
Test de colapso beta_eff/c vs Omega
=============================================
Prioridad 1: Verificar si la forma funcional beta = -c*Omega*(1-Omega)
es universal (misma forma, solo c cambia) o si cada modelo tiene forma diferente.

Si beta_eff/c colapsa sobre Omega*(1-Omega) para todos los modelos,
la autonomia del flujo es robusta.

Datos: STATUS_v18, series autoritativas + KI J intermedios
"""
import numpy as np

# =============================================================
# DATOS AUTORITATIVOS (STATUS v18)
# =============================================================

# KI_chaotic J=1.0 (8 puntos, N=4-18)
ki_chaotic = {
    'name': 'KI J=1.0 (chaotic)',
    'N': np.array([4, 6, 8, 10, 12, 14, 16, 18]),
    'Omega': np.array([0.2801, 0.2151, 0.1587, 0.1348, 0.1189, 0.1027, 0.0907, 0.0814]),
    'c_fit': 0.994
}

# SYK q=4 (5 puntos, N=4-12)
syk_q4 = {
    'name': 'SYK q=4',
    'N': np.array([4, 6, 8, 10, 12]),
    'Omega': np.array([0.07187, 0.01614, 0.00512, 0.00125, 0.00033]),
    'c_fit': 3.901
}

# SYK q=6 (5 puntos, N=4-12)
syk_q6 = {
    'name': 'SYK q=6',
    'N': np.array([4, 6, 8, 10, 12]),
    'Omega': np.array([0.13101, 0.02662, 0.00661, 0.00181, 0.00050]),
    'c_fit': 4.300
}

# KI J=0.7 (5 puntos, N=4-12)
ki_j07 = {
    'name': 'KI J=0.7',
    'N': np.array([4, 6, 8, 10, 12]),
    'Omega': np.array([0.16767, 0.05347, 0.03223, 0.02253, 0.01442]),
    'c_fit': 2.719
}

# KI J=1.0 restricted to N=4-12 for fair comparison
ki_chaotic_12 = {
    'name': 'KI J=1.0 (N≤12)',
    'N': np.array([4, 6, 8, 10, 12]),
    'Omega': np.array([0.2801, 0.2151, 0.1587, 0.1348, 0.1189]),
    'c_fit': 0.994
}

# KI J=0.5 — included but flagged as non-monotonic
ki_j05 = {
    'name': 'KI J=0.5 (non-chaotic)',
    'N': np.array([4, 6, 8, 10, 12]),
    'Omega': np.array([0.06669, 0.05042, 0.05637, 0.04763, 0.04395]),
    'c_fit': 0.356
}

def compute_beta_eff(N, Omega):
    """
    Compute beta_eff = Delta(Omega) / Delta(ln N) using central differences.
    Returns (Omega_mid, beta_eff) arrays with len = len(N) - 2
    """
    beta = []
    omega_mid = []
    for i in range(1, len(N) - 1):
        dOmega = Omega[i+1] - Omega[i-1]
        dlnN = np.log(N[i+1]) - np.log(N[i-1])
        beta.append(dOmega / dlnN)
        omega_mid.append(Omega[i])
    return np.array(omega_mid), np.array(beta)

def logistic_prediction(Omega, c):
    """beta_logistic = -c * Omega * (1 - Omega)"""
    return -c * Omega * (1 - Omega)

def powerlaw_prediction(Omega, alpha):
    """beta_powerlaw = -alpha * Omega"""
    return -alpha * Omega

print("=" * 70)
print("TEST DE COLAPSO: beta_eff / c vs Omega*(1-Omega)")
print("=" * 70)
print()
print("Si beta_eff/c ≈ -Omega*(1-Omega) para todos los modelos,")
print("la forma logistica es universal y solo c varia.")
print()

# Models with monotonic flow (exclude J=0.5)
models = [ki_chaotic_12, ki_j07, syk_q4, syk_q6]

print(f"{'Modelo':<20} {'Omega_mid':>10} {'beta_eff':>10} {'beta/c':>10} "
      f"{'-Ω(1-Ω)':>10} {'Residuo':>10}")
print("-" * 70)

all_residuals = []

for m in models:
    omega_mid, beta_eff = compute_beta_eff(m['N'], m['Omega'])
    c = m['c_fit']
    
    for i in range(len(omega_mid)):
        beta_normalized = beta_eff[i] / c
        logistic_target = -omega_mid[i] * (1 - omega_mid[i])
        residual = beta_normalized - logistic_target
        all_residuals.append(residual)
        
        print(f"{m['name']:<20} {omega_mid[i]:>10.5f} {beta_eff[i]:>10.5f} "
              f"{beta_normalized:>10.5f} {logistic_target:>10.5f} {residual:>10.5f}")
    print()

all_residuals = np.array(all_residuals)
print("=" * 70)
print(f"RESIDUOS del colapso beta/c + Omega*(1-Omega):")
print(f"  Media:   {np.mean(all_residuals):>+.6f}")
print(f"  Std:     {np.std(all_residuals):>.6f}")
print(f"  Max|res|: {np.max(np.abs(all_residuals)):>.6f}")
print(f"  RMS:     {np.sqrt(np.mean(all_residuals**2)):>.6f}")
print()

# Also compute R^2 of the collapse
target = np.array([])
observed = np.array([])
for m in models:
    omega_mid, beta_eff = compute_beta_eff(m['N'], m['Omega'])
    c = m['c_fit']
    target = np.append(target, -omega_mid * (1 - omega_mid))
    observed = np.append(observed, beta_eff / c)

ss_res = np.sum((observed - target)**2)
ss_tot = np.sum((observed - np.mean(observed))**2)
r2 = 1 - ss_res / ss_tot
print(f"R² del colapso beta_eff/c sobre -Omega*(1-Omega): {r2:.6f}")
print()

# Now test: what if we DON'T use the individual c_fit but 
# fit a SINGLE c to all models? This would be the strong universality claim.
# (We expect this to fail — c is model-dependent. But documenting it.)
print("=" * 70)
print("TEST ALTERNATIVO: ¿Existe un c unico para todos los modelos?")
print("=" * 70)
print()

# Collect all (Omega_mid, beta_eff) pairs
all_omega = np.array([])
all_beta = np.array([])
for m in models:
    omega_mid, beta_eff = compute_beta_eff(m['N'], m['Omega'])
    all_omega = np.append(all_omega, omega_mid)
    all_beta = np.append(all_beta, beta_eff)

# Fit single c: beta = -c * Omega * (1-Omega) → c = -beta / (Omega*(1-Omega))
c_estimates = -all_beta / (all_omega * (1 - all_omega))
print(f"c estimado por punto:")
idx = 0
for m in models:
    omega_mid, beta_eff = compute_beta_eff(m['N'], m['Omega'])
    for i in range(len(omega_mid)):
        print(f"  {m['name']:<20} Ω={omega_mid[i]:.4f}  c_local={c_estimates[idx]:.3f}")
        idx += 1
    print()

print(f"  c global medio: {np.mean(c_estimates):.3f} ± {np.std(c_estimates):.3f}")
print(f"  CV(c): {np.std(c_estimates)/np.mean(c_estimates)*100:.1f}%")
print()
print("Si CV(c) >> 20%, c NO es universal entre modelos (esperado).")
print("Lo que es universal es la FORMA, no el valor de c.")

print()
print("=" * 70)
print("COMPARACION: LOGISTICO vs POWER-LAW como forma universal")
print("=" * 70)
print()

# For power-law: beta = -alpha * Omega → beta/alpha = -Omega
# Compute alpha for each model from fit
# For logistic Omega = 1/(1+A*N^c), the corresponding power-law alpha
# is approximately c (leading term)

print(f"{'Modelo':<20} {'Omega_mid':>10} {'beta/c':>10} {'-Ω(1-Ω)':>10} "
      f"{'-Ω':>10} {'|res_log|':>10} {'|res_pow|':>10}")
print("-" * 80)

n_log_wins = 0
n_pow_wins = 0

for m in models:
    omega_mid, beta_eff = compute_beta_eff(m['N'], m['Omega'])
    c = m['c_fit']
    
    for i in range(len(omega_mid)):
        bn = beta_eff[i] / c
        log_pred = -omega_mid[i] * (1 - omega_mid[i])
        pow_pred = -omega_mid[i]
        res_log = abs(bn - log_pred)
        res_pow = abs(bn - pow_pred)
        
        winner = "LOG" if res_log < res_pow else "POW"
        if res_log < res_pow:
            n_log_wins += 1
        else:
            n_pow_wins += 1
        
        print(f"{m['name']:<20} {omega_mid[i]:>10.5f} {bn:>10.5f} "
              f"{log_pred:>10.5f} {pow_pred:>10.5f} "
              f"{res_log:>10.5f} {res_pow:>10.5f}  {winner}")
    print()

print(f"Logistico gana: {n_log_wins}/{n_log_wins+n_pow_wins}")
print(f"Power-law gana: {n_pow_wins}/{n_log_wins+n_pow_wins}")
print()
print("NOTA: La diferencia log vs pow solo es visible cuando Omega")
print("esta en rango intermedio [0.1, 0.4]. Para Omega << 0.1,")
print("ambas predicciones convergen (-Omega*(1-Omega) ≈ -Omega).")

