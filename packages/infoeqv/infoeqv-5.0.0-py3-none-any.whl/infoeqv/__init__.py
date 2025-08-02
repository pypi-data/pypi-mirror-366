import numpy as np
import math

def info_eqv_design(x, f):
    x = np.array(x, dtype=float)
    f = np.array(f, dtype=float)
    
    N = sum(f)  # Total number of observations
    xbar = np.mean(x)  # Mean of x
    xmax = np.max(x)   # Maximum of x
    d = (x - xbar) / (xmax - xbar)  # Standardized values of x
    
    print("Original x values:", x)
    print("Frequency f values:", f)
    print(f"\nTotal number of observations (N): {N}")
    print(f"Mean of x (x̄): {xbar:.4f}")
    print(f"Maximum of x: {xmax}")
    print("Standardized values (d):", np.round(d, 4))

    dsqr = d**2
    M = sum(f * d)  # Weighted sum for mean
    mu_1 = M / N
    P = sum(f * dsqr)
    mu_2 = P / N
    mu_22 = mu_2 - mu_1**2  # Central moment
    
    print(f"\nWeighted mean of d (μ₁): {mu_1:.4f}")
    print(f"Weighted second moment (μ₂): {mu_2:.4f}")
    print(f"Central moment (μ₂₂): {mu_22:.4f}")

    # Lower and upper bounds
    Y = N * mu_22
    Z = (1 + mu_1)**2 + mu_22
    L = Y / Z
    
    Y1 = N * (1 - mu_1)**2
    Z1 = (1 - mu_1)**2 + mu_22
    U = Y1 / Z1

    print(f"\nLower bound (L): {L:.4f}")
    print(f"Upper bound (U): {U:.4f}")
    
    S = math.ceil(L)
    T = math.floor(U)

    print(f"Ceiling of L (S): {S}")
    print(f"Floor of U (T): {T}")

    if (U - L) <= 1:
        print("\n❌ Alternative two-point information equivalent design doesn't exist.")
        return

    # Generate range of n1 and compute matrix
    R = list(range(S, T + 1))
    b = N - np.array(R)
    Z3 = len(R)
    mdat = np.zeros((Z3, 4))

    print("\n✅ Alternative Two-Point Information Equivalent Designs:")
    print(f"{'n1':>5} {'n2':>5} {'d1':>10} {'d2':>10}")
    print("-" * 35)

    for i in range(Z3):
        n1 = R[i]
        n2 = b[i]
        d1 = mu_1 - np.sqrt((n2 / n1) * mu_22)
        d2 = mu_1 + np.sqrt((n1 / n2) * mu_22)
        mdat[i] = [n1, n2, d1, d2]
        print(f"{int(n1):>5} {int(n2):>5} {d1:>10.4f} {d2:>10.4f}")
    
    return mdat
