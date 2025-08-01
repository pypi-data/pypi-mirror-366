import numpy as np

def brnldist(a, c, x0, m, p, n):
    """
    Generate Bernoulli distributed values using Linear Congruential Generator (LCG).

    Parameters:
        a (int): LCG multiplier
        c (int): LCG increment
        x0 (int): Seed value
        m (int): LCG modulus
        p (float): Bernoulli threshold (0 to 1)
        n (int): Number of values to generate

    Returns:
        tuple: (y, u, x)
            y = raw LCG values
            u = normalized values (0 to 1)
            x = Bernoulli distribution (0 or 1)
    """
    # Step 1: Initialize LCG list
    z = [[x0] + [0] * (n - 1)]  # Placeholder values after x0
    y = z[0]

    # Step 2: Generate values using LCG
    for i in range(n - 1):
        y[i + 1] = (a * y[i] + c) % m

    # Step 3: Normalize values
    u = np.divide(y, m)

    # Step 4: Apply Bernoulli threshold
    x = np.zeros(n)
    for i in range(n):
        x[i] = 1 if u[i] < p else 0

    
    return y, u, x  # Return for further use if needed