"""
Converted from Jupyter notebook: hartman watson distribution.ipynb
"""

# %%
import numpy as np
from xsigmamodules.Math import (
    hartmanWatsonDistribution,
    gaussianQuadrature,
    hartman_watson_distribution_enum,
)
from xsigmamodules.Vectorization import vector, matrix, tensor
from xsigma.util.numpy_support import xsigmaToNumpy, numpyToXsigma
from matplotlib import pyplot as plt

# %%
n = 64
t = 0.5
size_roots = 32
x_0 = -5
x_n = 3.1

roots = vector["double"](size_roots)
w1 = vector["double"](size_roots)
w2 = vector["double"](size_roots)

# %%
gaussianQuadrature.gauss_kronrod(size_roots, roots, w1, w2)

# %%
a = np.linspace(x_0, x_n, n)
print(a)

# %%
r = numpyToXsigma(a)
b = np.zeros(n)
print(b)
result = numpyToXsigma(b)

# %%
hartmanWatsonDistribution.distribution(
    result, t, r, roots, w1, hartman_watson_distribution_enum.MIXTURE
)

# %%
plt.plot(a, b)
plt.show()
