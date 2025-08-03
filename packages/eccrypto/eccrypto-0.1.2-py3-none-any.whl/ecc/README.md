# `ecc` Module: Mathematical Foundations

This document provides a deeper look into the mathematical concepts that power the `ecc` library. While the source code files contain docstrings explaining *what* each function does, this file explains the *why* behind the mathematics.

---
##  Finite Field Arithmetic (`field.py`)

All operations in elliptic curve cryptography occur within a **finite field**, which is a set with a finite number of elements. For our library, we use a prime field, denoted as **F<sub>p</sub>** or **E(Z/pZ)**, where `p` is a large prime number.

This means every calculation is performed "modulo p". The `FieldElement` class encapsulates this behavior.

### Modular Arithmetic Operations

* **Addition**: `(a + b) mod p`
* **Subtraction**: `(a - b) mod p`
* **Multiplication**: `(a * b) mod p`
* **Division**: `a / b` is calculated as `(a * b⁻¹) % p`, where `b⁻¹` is the modular **multiplicative inverse** of `b`.
* **Exponentiation**: `aᵏ` is efficiently calculated as `a^(k % (p-1)) % p` using **Fermat's Little Theorem**.

### Modular Exponentiation and Fermat's Little Theorem

Calculating `aᵏ mod p` for very large `k` is a common requirement. A naive calculation would be too slow. We use a powerful optimization based on **Fermat's Little Theorem**.

The theorem states that for any prime `p` and any integer `a` not divisible by `p`:

```math
a^{p-1} \equiv 1 \pmod p
```

This implies that exponents "wrap around" `mod (p-1)`. Let `k = q(p-1) + r`, where `r = k mod (p-1)`. The derivation is as follows:

```math
\begin{aligned}
a^k & \equiv a^{q(p-1) + r} \\
    & \equiv (a^{p-1})^q \cdot a^r \\
    & \equiv 1^q \cdot a^r \\
    & \equiv a^r \\
    & \equiv a^{k \pmod{p-1}} \pmod p
\end{aligned}
```

This final relationship is implemented in the `__pow__` method of the `FieldElement` class to perform efficient exponentiation.

---
## Elliptic Curve Group Theory (`point.py`)

An elliptic curve is defined by the equation **y² = x³ + ax + b**. The set of points on this curve, along with a special "point at infinity" (O), forms a mathematical group under an operation called "point addition".

The `Point` class implements this group law.

### Geometric Interpretation of Point Addition

The addition of two points, **P** and **Q**, is defined geometrically:

1.  Draw a straight line passing through points **P** and **Q**.
2.  This line will intersect the elliptic curve at exactly one other point (or be tangent to it). Let's call this intersection point **-R**.
3.  The result of the addition, `P + Q`, is defined as the reflection of **-R** across the x-axis, which we call **R**.

### Algebraic Formulas for Point Addition

This geometric rule translates into the following algebraic formulas, which are implemented in the `__add__` method.

#### Case 1: Adding Two Distinct Points (P ≠ Q)

Let `P = (x₁, y₁)` and `Q = (x₂, y₂)`.

1.  **Calculate the slope (s) of the line passing through P and Q:**
    ```math
    s = \frac{y_2 - y_1}{x_2 - x_1}
    ```

2.  **Calculate the coordinates of the resulting point `R = (x₃, y₃)`:**
    ```math
    \begin{aligned}
    x_3 &= s^2 - x_1 - x_2 \\
    y_3 &= s(x_1 - x_3) - y_1
    \end{aligned}
    ```

#### Case 2: Point Doubling (P = Q)

When adding a point to itself (`P + P`), the line becomes the tangent to the curve at point `P`.

1.  **Calculate the slope (s) of the tangent line at `P = (x₁, y₁)`:**
    ```math
    s = \frac{3x_1^2 + a}{2y_1}
    ```
    *(This is derived by taking the derivative of the curve equation.)*

2.  **Calculate the coordinates of the resulting point `R = (x₃, y₃)`:**
    ```math
    \begin{aligned}
    x_3 &= s^2 - 2x_1 \\
    y_3 &= s(x_1 - x_3) - y_1
    \end{aligned}
    ```

### Scalar Multiplication

Scalar multiplication, `k * P`, is simply the operation of adding the point **P** to itself `k` times.

```math
k \cdot P = \underbrace{P + P + \dots + P}_{k \text{ times}}
```

A naive implementation of this would be too slow and vulnerable to side-channel attacks. Therefore, this library uses the **Montgomery Ladder** algorithm, a constant-time method that protects against timing attacks by performing the same sequence of operations for every bit of the scalar `k`.
---
## Elliptic Curve Definitions (`curve.py`)

This section covers the properties that define a valid, cryptographically secure elliptic curve.

### Non-Singular Curves and the Discriminant

For a curve to be suitable for cryptography, it must be **non-singular**. A singular curve has cusps or self-intersections, which breaks the group law.

We verify this by checking the curve's **discriminant (∆)**. For a curve in the short Weierstrass form `y² = x³ + ax + b`, the discriminant is:

```math
\Delta = -16(4a^3 + 27b^2)
```

A curve is non-singular if and only if **∆ ≠ 0**. Our library ensures this condition is met.

### The Elliptic Curve Discrete Logarithm Problem (ECDLP)

The security of all elliptic curve cryptography is based on the difficulty of the **Elliptic Curve Discrete Logarithm Problem (ECDLP)**.

The problem is: Given two points, **P** and **Q**, where **Q** is a multiple of **P** (`Q = k * P`), it is computationally infeasible to find the integer `k`.

* **Scalar Multiplication (`k * P`)**: Easy (a one-way function).
* **Discrete Logarithm (`find k`)**: Extremely hard.

### Domain Parameters

A specific elliptic curve is defined by a set of public **domain parameters**: `{P, a, b, G, n, h}`.

* **`P`**: The prime modulus defining the finite field **F<sub>p</sub>**.
* **`a`, `b`**: The coefficients of the curve equation `y² = x³ + ax + b`.
* **`G`**: A chosen base point on the curve, called the **generator point**.
* **`n`**: The **order** of the generator point `G`. This is the smallest positive integer such that `n * G` results in the point at infinity.
* **`h`**: The **cofactor**, which relates the order of `G` to the total number of points on the curve. It is calculated as `h = |E(F_p)| / n`. For security, a cofactor of `h=1` is strongly preferred.
---
## Elliptic Curve Definitions (`curve.py`)

This section covers the properties that define a valid, cryptographically secure elliptic curve.

### Non-Singular Curves and the Discriminant

For a curve to be suitable for cryptography, it must be **non-singular**. A singular curve has cusps or self-intersections, which breaks the group law.

We verify this by checking the curve's **discriminant**. For a curve in the short Weierstrass form $y^2 = x^3 + ax + b$, the discriminant is:

```math
\Delta = -16(4a^3 + 27b^2)
```

A curve is non-singular if and only if $\Delta \neq 0$. Our library ensures this condition is met.

### The Elliptic Curve Discrete Logarithm Problem (ECDLP)

The security of all elliptic curve cryptography is based on the difficulty of the **Elliptic Curve Discrete Logarithm Problem (ECDLP)**.

The problem is: Given two points, **P** and **Q**, where $Q = k \cdot P$, it is computationally infeasible to find the integer `k`.

* **Scalar Multiplication** (`k • P`): Easy (a one-way function).
* **Discrete Logarithm** (`find k`): Extremely hard.

### Domain Parameters

A specific elliptic curve is defined by a set of public **domain parameters**: $\{P, a, b, G, n, h\}$.

* **`P`**: The prime modulus defining the finite field $F_p$.
* **`a`, `b`**: The coefficients of the curve equation $y^2 = x^3 + ax + b$.
* **`G`**: A chosen base point on the curve, called the **generator point**.
* **`n`**: The **order** of the generator point `G`. This is the smallest positive integer such that $n \cdot G$ results in the point at infinity.
* **`h`**: The **cofactor**, which relates the order of `G` to the total number of points on the curve. It is calculated as $h = |E(F_p)| / n$. For security, a cofactor of $h=1$ is strongly preferred.
