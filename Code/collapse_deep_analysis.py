"""
Análisis profundo del test de colapso.
El resultado anterior muestra algo importante que necesita interpretación correcta.
"""
import numpy as np

print("=" * 70)
print("INTERPRETACIÓN DEL TEST DE COLAPSO")
print("=" * 70)
print()

print("HALLAZGO 1: R² = 0.953 para el colapso beta/c sobre -Omega(1-Omega)")
print("  Esto suena bien, pero es engañoso. La razón:")
print("  Para Omega << 0.1, -Omega(1-Omega) ≈ -Omega.")
print("  Logístico y power-law son INDISTINGUIBLES en ese rango.")
print("  SYK q=4 y q=6 tienen Omega < 0.03 en la mayoría de puntos.")
print("  El R² alto viene de que AMBAS formas ajustan bien ahí.")
print()

print("HALLAZGO 2: Power-law gana 8/12 puntos")
print("  Esto NO refuta el logístico — pero muestra que la discriminación")
print("  entre formas solo ocurre donde Omega > 0.1.")
print("  Solo KI J=1.0 tiene puntos en ese rango (Omega = 0.12-0.28).")
print("  Y ahí el logístico gana 2/3.")
print()

print("HALLAZGO 3: Los residuos del colapso son SISTEMÁTICAMENTE negativos")
print("  para SYK (beta/c más negativo que -Omega(1-Omega)).")
print("  Esto sugiere que para Omega << 0.1, el flujo real es")
print("  MÁS EMPINADO que el logístico — más cercano a power-law.")
print()

# Quantify: where does logistic vs power-law actually differ?
print("=" * 70)
print("DONDE IMPORTA LA DIFERENCIA")
print("=" * 70)
print()
print(f"{'Omega':>10} {'-Ω(1-Ω)':>12} {'-Ω':>12} {'Diferencia':>12} {'%':>8}")
print("-" * 55)
for omega in [0.001, 0.005, 0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]:
    log = -omega*(1-omega)
    pw = -omega
    diff = log - pw  # = omega^2 (siempre positivo)
    pct = abs(diff/pw)*100 if pw != 0 else 0
    print(f"{omega:>10.3f} {log:>12.6f} {pw:>12.6f} {diff:>12.6f} {pct:>7.1f}%")

print()
print("CONCLUSIÓN CLAVE:")
print("  Para Omega < 0.05: diferencia < 5%. Indistinguibles.")
print("  Para Omega > 0.15: diferencia > 15%. Discriminable.")
print("  Para Omega > 0.25: diferencia > 25%. Clara discriminación.")
print()
print("DATOS DE KAELION EN LA ZONA DISCRIMINANTE (Omega > 0.10):")
print("  KI J=1.0: Omega = 0.28, 0.22, 0.16, 0.13, 0.12 (5 puntos)")
print("  KI J=0.7: Omega = 0.17 (1 punto)")
print("  SYK: NINGÚN punto (todos Omega < 0.13)")
print()
print("Resultado: Solo 6 de 24 puntos están en zona discriminante.")
print("Y son todos del mismo modelo (KI) o vecindad (J=0.7).")
print()

print("=" * 70)
print("QUÉ NECESITAMOS PARA RESOLVER ESTO")
print("=" * 70)
print()
print("Opción A: MÁS PUNTOS en Omega > 0.15")
print("  → KI_chaotic N=20-40 baja Omega a ~0.05-0.08 (SALE de la zona)")
print("  → N grande NO ayuda a discriminar — Omega se hace más pequeño")
print("  → Lo que ayuda: OTROS MODELOS con Omega alto y flujo monotónico")
print()
print("Opción B: MODELO CON SCRAMBLING LENTO")
print("  → Un modelo donde Omega(N=12) ≈ 0.3-0.5 daría datos en")
print("    la zona discriminante sin necesitar N grande.")
print("  → Candidatos: KI con J cercano al umbral caótico (J~0.3-0.5)")
print("    ¡Esto es exactamente Tarea D! J=0.3 tiene c=0.36 → Omega alto")
print()
print("Opción C: USAR LA CURVATURA en log-log como discriminante")
print("  → En vez de beta vs Omega, plotear log(Omega) vs log(N)")
print("  → Logístico: curvatura visible (pendiente cambia con N)")
print("  → Power-law: línea recta (pendiente constante)")
print("  → Esto usa TODOS los puntos, no solo los de Omega alto")
print()

# Compute curvature test
print("=" * 70)
print("TEST DE CURVATURA log-log")
print("=" * 70)
print()

models_data = {
    'KI J=1.0': {'N': [4,6,8,10,12,14,16,18], 
                  'Omega': [0.2801, 0.2151, 0.1587, 0.1348, 0.1189, 0.1027, 0.0907, 0.0814]},
    'SYK q=4':  {'N': [4,6,8,10,12],
                  'Omega': [0.07187, 0.01614, 0.00512, 0.00125, 0.00033]},
    'SYK q=6':  {'N': [4,6,8,10,12],
                  'Omega': [0.13101, 0.02662, 0.00661, 0.00181, 0.00050]},
    'KI J=0.7': {'N': [4,6,8,10,12],
                  'Omega': [0.16767, 0.05347, 0.03223, 0.02253, 0.01442]},
}

for name, data in models_data.items():
    N = np.array(data['N'])
    Om = np.array(data['Omega'])
    lnN = np.log(N)
    lnOm = np.log(Om)
    
    # Local slope (gamma) at each interior point
    gammas = []
    for i in range(1, len(N)-1):
        g = (lnOm[i+1] - lnOm[i-1]) / (lnN[i+1] - lnN[i-1])
        gammas.append(g)
    
    # If power-law: gamma = const. If logistic: gamma varies.
    gammas = np.array(gammas)
    if len(gammas) > 1:
        cv_gamma = np.std(gammas) / abs(np.mean(gammas)) * 100
        trend = gammas[-1] - gammas[0]  # negative = steepening (logistic), zero = power-law
        print(f"{name:<15}: gamma = {gammas}")
        print(f"  mean={np.mean(gammas):.3f}, CV={cv_gamma:.1f}%, "
              f"trend={trend:+.3f} ({'steepening→LOG' if trend < -0.05 else 'flat→POW' if abs(trend)<0.05 else 'shallowing'})")
    else:
        print(f"{name:<15}: solo 1 punto interior, no se puede evaluar curvatura")
    print()

print()
print("=" * 70)
print("RECOMENDACIÓN PARA EPIS Y ERICK")
print("=" * 70)
print()
print("1. La discriminación log vs power-law NO se resuelve con N grande.")
print("   N grande lleva Omega → 0, donde ambas convergen.")
print()
print("2. Se resuelve con MODELOS que mantengan Omega en [0.1, 0.5]")
print("   a N=4-12. Tarea D (más valores J) es la prioridad correcta.")
print()
print("3. La curvatura en log-log es un discriminante alternativo")
print("   que usa todos los puntos. Si gamma(N) varía → logístico.")
print("   Si gamma es constante → power-law.")
print()
print("4. Para Paper 3, reformular el claim:")
print("   NO: 'ΔAIC=-3.30 demuestra logístico sobre power-law'")
print("   SÍ: 'La forma logística es la expansión universal con dos")
print("   puntos fijos. Power-law es indistinguible en el IR (Omega<<1).")
print("   La discriminación requiere datos en rango intermedio (Omega~0.2).'")

