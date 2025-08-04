import numpy as np
import matplotlib.pyplot as plt

def info_eqv_design(x, f):
    x = np.array(x, dtype=float)
    f = np.array(f, dtype=float)
    N = sum(f)
    xbar = np.sum(f * x) / N
    xmax = np.max(np.abs(x))

    # Standardized x values
    d = (x - xbar) / (xmax - xbar)

    # Centralized and raw moments
    mu_1 = np.sum(f * d) / N
    mu_2 = np.sum(f * d**2) / N
    mu_22 = mu_2 - mu_1 ** 2  # Central moment
    mu_6 = np.sum(f * d**6) / N
    k = N / 2  # For two-point design

    # Calculate bounds for n1, n2
    L = N * mu_22 / ((1 + mu_1) ** 2 + mu_22)
    U = N * (1 - mu_1) ** 2 / ((1 - mu_1) ** 2 + mu_22)
    S = int(np.ceil(L))
    T = int(np.floor(U))

    # Display descriptive stats
    print(f"\nOriginal x values: {x}")
    print(f"Frequency f values: {f}")
    print(f"\nTotal number of observations (N): {N}")
    print(f"Mean of x (x̄): {xbar:.4f}")
    print(f"Standardized values (d): {np.round(d, 4)}\n")
    print(f"Weighted mean (μ₁): {mu_1:.4f}")
    print(f"Weighted second moment (μ₂): {mu_2:.4f}")
    print(f"Central moment (μ₂₂): {mu_22:.4f}")
    print(f"μ₆: {mu_6:.4f}")
    print(f"\nBounds: L = {L:.4f}, U = {U:.4f}")
    print(f"Ceiling of L (S): {S}, Floor of U (T): {T}\n")

    # Header for designs
    print("✅ Designs satisfying (i) & (ii), but failing ❌ (iii):")
    print(f"{'n1':>4} {'n2':>4} {'d1':>10} {'d2':>10}  Status")

    # Lists for plotting
    d1_list, d2_list, f1_list, f2_list = [], [], [], []

    # Loop through possible n1 values
    for n1 in range(S, T + 1):
        n2 = int(N - n1)
        f_ratio = n2 / n1
        d1 = mu_1 - np.sqrt(f_ratio * mu_22)
        d2 = mu_1 + np.sqrt((1 / f_ratio) * mu_22)

        # ✅ Condition (i): k(1 - μ₂) < n₂ < k
        cond1 = k * (1 - mu_2) < n2 < k

        # ✅ Condition (ii): μ₂ < d₂² < 1
        cond2 = mu_2 < d2 ** 2 < 1

        # ❌ Condition (iii): n₂ * μ₂³ ≥ k * μ₆
        cond3 = (n2 * mu_2 ** 3) >= (k * mu_6)

        # If first two conditions are satisfied
        if cond1 and cond2:
            d1_list.append(d1)
            d2_list.append(d2)
            f1_list.append(n1)
            f2_list.append(n2)
            status = "✅" if cond3 else "❌"
            print(f"{n1:4} {n2:4} {d1:10.4f} {d2:10.4f}   {status} (iii)")

    # Plot designs satisfying condition (i) and (ii)
    if d1_list:
        # Convert to original x scale
        d1_plot = np.array(d1_list) * (xmax - xbar) + xbar
        d2_plot = np.array(d2_list) * (xmax - xbar) + xbar

        plt.figure(figsize=(10, 6))

        # Plot original design
        plt.scatter(x, f, color='blue', label='Original Design')
        for i in range(len(x)):
            plt.text(x[i], f[i] + 0.3, f'{int(f[i])}', ha='center', fontsize=8)

        # Plot two-point designs (i)&(ii)
        for i in range(len(d1_plot)):
            plt.plot([d1_plot[i], d2_plot[i]], [f1_list[i], f2_list[i]], 'r--', alpha=0.7)
            plt.scatter([d1_plot[i], d2_plot[i]], [f1_list[i], f2_list[i]],
                        color='red', marker='x', label='2-point design (i)&(ii)' if i == 0 else "")

        plt.xlabel('x (original scale)')
        plt.ylabel('Frequency')
        plt.title('Two-Point Designs Satisfying Conditions (i) & (ii)')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()
        plt.tight_layout()
        plt.show()
    else:
        print("⚠️ No valid designs found under conditions (i) & (ii).")
