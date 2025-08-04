"""
Converted from Jupyter notebook: zabr_variables_impact.ipynb
"""

# %%
# Markdown cell:
# # ZABR and SABR PDE Interactive Models
# 
# This notebook provides interactive visualizations for ZABR Classic, ZABR Mixture, and SABR PDE models.

# %%
import common.sabrHelper as sabr
import numpy as np
from xsigmamodules.Market import (
    volatilityModelSabr,
    volatilityModelPdeClassic,
    volatilityModelZabrClassic,
    volatilityModelZabrMixture,
    volatility_model_output_enum,
)

%matplotlib inline

# %%
# Markdown cell:
# 
# ZABR SDE: $$dF_t=z_t\sigma(F_t)dW^{s}_t, \quad \textrm{and} \quad dz_t=\varepsilon(z) z_tdW^{z}_t, \quad \textrm{with} \quad dW^{s}_t.dW^{z}_t=\rho dt$$
# the voltility function: $$\sigma(F_t)$$ $$\varepsilon(z_t)=\nu z_t^{\gamma-1}$$
# $$z_0:\quad \textrm{initial vol we set }z_0 = 1 \quad $$
# $$\nu:\quad \textrm{vol of volatilty,} \quad $$
# $$\rho:\quad \textrm{correlation,} \quad $$

# %%
# Markdown cell:
# ## ZABR Classic

# %%
# Markdown cell:
# $$\sigma(F_t)=\alpha F_t^\beta$$

# %%
zabr_classic_params = {
    "expiry": 10.0,
    "forward": 0.0325,
    "alpha": 0.0873,
    "beta": 0.7,
    "nu": 0.47,
    "rho": -0.48,
    "shift": 0.0,
    "gamma": 1.0,
    "use_vol_adjustement": True,
}
n = 100
zabr_classic_x = np.linspace(0.0, 0.2, n)
sabr.create_volatility_plotter(
    volatilityModelZabrClassic,
    zabr_classic_params,
    zabr_classic_x,
    n,
    zabr_classic_x[0],
    zabr_classic_x[-1],
    "ZABR Classic",
)

# %%
# Markdown cell:
# ## SABR PDE

# %%
sabr_pde_params = {
    "expiry": 30.0,
    "forward": 0.02,
    "alpha": 0.035,
    "beta": 0.25,
    "nu": 1.0,
    "rho": -0.1,
    "shift": 0.0,
    "N": 100,
    "timesteps": 5,
    "nd": 5,
}
n = 100
sabr_pde_x = np.linspace(0.0, 0.2, n)
sabr.create_volatility_plotter(
    volatilityModelPdeClassic, sabr_pde_params, sabr_pde_x, n, 0.001, 0.2, "SABR PDE"
)

# %%
# Markdown cell:
# ## ZABR Mixture

# %%
# Markdown cell:
# 
#  The volatility function is defined as:
#  $$\sigma(x) =
#  \begin{cases}
#  \alpha \left(\omega \tanh(x) + (1 - \omega) \tanh(x)^{\beta_2}\right)^{\beta_1}, & \text{if } x \geq x_0 \\
#  v_1 + p \exp\left(\frac{d_1}{p}(x - x_0) + \frac{1}{2}\left(\frac{d_2}{p} - \left(\frac{d_1}{p}\right)^2\right)(x - x_0)^2\right), & \text{if } x < x_0
#  \end{cases}$$
# 
#  Where:
#  $\alpha$ controls the overall smile level,
#  $\beta_1$ controls ATM skew,
#  $\beta_2$ is the High Strike skew,
#  $\omega$ (Effective Speed) controls the speed of transition from $\beta_1$ to $\beta_2$,
#  $v_1$ is the volatility level on the left part of the strike $x_0$,
#  $x_0$ is a strike level where $x_0 > 0$, and
#  $p = \sigma(x_0) - v_1$.
# 
#  For the case with a local volatility cap:
#  $$\sigma(x) =
#  \begin{cases}
#  \sigma(x_U), & \text{if } x \geq x_U, \\
#  \sigma(x), & \text{if } x \leq x_U - S, \\
#  \sigma(x)(1 - K(\frac{x_U - x}{S})) + \sigma(x_U)K(\frac{x_U - x}{S}), & \text{else}
#  \end{cases}$$
# 
#  Where:
#  $x_U$ is the strike threshold.
#  $S$ is the smoothing parameter.
#  $K(x)$ is the smooth step function.

# %%
zabr_mixture_params = {
    "expiry": 30,
    "forward": -0.0007,
    "alpha": 0.0132,
    "beta1": 0.2,
    "beta2": 1.25,
    "d": 0.2,
    "nu": 0.1978,
    "rho": -0.444,
    "gamma": 1.0,
    "use_vol_adjustement": True,
    "high_strike": 0.1,
    "vol_low": 0.0001,
    "low_strike": 0.02,
    "forward_cut_off": 0.02,
    "smothing_factor": 0.001,
}
n = 401
zabr_mixture_x = np.linspace(-0.15, 0.3, n)
sabr.create_volatility_plotter(
    volatilityModelZabrMixture,
    zabr_mixture_params,
    zabr_mixture_x,
    n,
    -0.15,
    0.3,
    "ZABR Mixture",
)
