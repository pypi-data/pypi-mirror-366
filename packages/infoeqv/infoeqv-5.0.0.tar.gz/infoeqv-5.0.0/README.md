The **Information Equivalent Two-Point Design** (or *information-preserving reduction*) is a concept from **optimal experimental design** and **information theory in statistics**, especially in **design of experiments (DoE)**. Here's a deeper explanation of the **theory behind your function** and where it fits in:

---

## THEORY: Information Equivalent Designs (Two-Point Reduction)

### Objective:

To replace a complex dataset with a **simplified two-point design** that **preserves the same information** about a model parameter, usually the **mean** or **location parameter**, under a linear or polynomial regression framework.

---

### 💡 Context:

Suppose you have a weighted dataset $$(x_i, f_i)$$ where:
 $$x_i$$:design points (levels of a factor)
 $$f_i$$:frequencies or weights (how often that point appears)

Rather than keeping all these points, we want to **approximate** this design with **only two support points**, say:
$$x_A$$ with weight $$r$$
$$x_B$$ with weight $$N - r$$

Such that the **statistical information about the mean** or some parameter is **unchanged**.

---

### Key Concepts Involved:

#### 1. **Information Matrix**

In linear regression $$y = \beta x + \epsilon$$, the **information matrix** of the design is:

$$
I = \sum f_i (x_i - \bar{x})^2
$$

We aim to find two new values $$x_A$$ and $$x_B$$, with appropriate frequencies $$r$$ and $$N - r$$, such that the **information matrix is the same**.

---

#### 2. **Standardized Design**

You normalize the data to make calculations scale-invariant:

$$
d_i = \frac{x_i - \bar{x}}{\max(x) - \bar{x}}
$$

This allows focusing only on the **relative spread** and centrality.

---

#### 3. **Moments of the Design**
* $$\mu_1 = \frac{1}{N} \sum f_i d_i$$:first central moment (mean)
* $$\mu_2 = \frac{1}{N} \sum f_i d_i^2$$:second raw moment
* $$\$mu_{22} = \mu_2 - \mu_1^2$$:central second moment (variance)

These determine the **shape** of the distribution.

---

#### 4. **Finding Bounds (L and U)**

You compute bounds $L$ and $U$ for feasible integer allocations of weight $r$ that will preserve the original information:

$$
L = \frac{N \cdot \mu_{22}}{(1 + \mu_1)^2 + \mu_{22}} \\
U = \frac{N \cdot (1 - \mu_1)^2}{(1 - \mu_1)^2 + \mu_{22}}
$$

Only if, 
$$U - L > 1$$, do feasible two-point equivalents exist.

---

#### 5. **Finding Equivalent Points**

For each valid $$r \in [\lceil L \rceil, \lfloor U \rfloor]$$, calculate:

* Two symmetric points around the mean that match the original design's spread:

$$
x_A = \mu_1 - \sqrt{\frac{N - r}{r} \cdot \mu_{22}} \\
x_B = \mu_1 + \sqrt{\frac{r}{N - r} \cdot \mu_{22}}
$$

These will become the new support points with weights r and N - r

---

## Applications:

* **Reducing design complexity** in regression without losing information.
* **Simplifying optimal designs** in statistics and engineering.
* Used in **experimental planning** when cost or resources are limited.
* Sometimes used in **machine learning** for data reduction or kernel approximation.

---

## Example in Real Life:

If you’re testing 6 drug doses with varying frequencies and want to reduce the testing to just **two key doses** that statistically represent the **same variability and effect**, this method gives you the way to choose those two doses.

---

# 📊 Information Equivalent Design (Two-Point Reduction)

This Python package provides a method for reducing an original frequency distribution to a two-point design with equivalent information. The approach is based on preserving the **first** and **second central moments**, ensuring statistical equivalence in terms of spread and location.

---

## 📦 Installation

To install the package, use:

```bash
pip install infoeqv
```

Or, if you have the source code locally:

```bash
pip install .
```

---

## Usage (How to Use)

```python
from infeqvdesign import info_eqv_design

x = [1, 2, 3, 4, 5, 6]
f = [6, 5, 4, 3, 2, 1]

info_eqv_design(x, f)
```
---

## Example Output

```
[[ 5.  16.  1.49  4.93]
 [ 6.  15.  1.33  5.09]
 [ 7.  14.  1.18  5.24]
 [ 8.  13.  1.04  5.38]
 [ 9.  12.  0.91  5.51]
 [10.  11.  0.79  5.63]]
```

Each row contains:

| r | N - r | x_A | x_B |
|--|--|--|--|
| weight 1 | weight 2 | equivalent point A | equivalent point B |

---

## Requirements

- Python 3.6+
- NumPy

Install dependencies manually with:

```bash
pip install numpy
```

---

## Author

 **Rohit Kumar Behera**
 GitHub: [@muinrohit](https://github.com/muinrohit)

---