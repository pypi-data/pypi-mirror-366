"""
Converted from Jupyter notebook: TestHJM.ipynb
"""

# %%
import time
import numpy as np
import matplotlib.pyplot as plt
from itertools import chain
from xsigmamodules.Random import random_enum
from xsigmamodules.Analytics import (
    calibrationIrTargetsConfiguration,
    correlationManager,
    calibrationHjmSettings,
    parameter_markovian_hjm_enum,
    calibrationIrHjm,
    parameterMarkovianHjmId,
    parameterMarkovianHjm,
    dynamicInstructionId,
    dynamicInstructionIrMarkovianHjm,
    simulatedMarketDataIrId,
    correlationManagerId,
    dynamicInstructionIrId,
    measureId,
    measure,
    randomConfig,
    simulationManager,
    randomConfigId,
    calibrationHjmSettingsBuilder,
    randomConfigBuilder
)

from xsigmamodules.Util import dayCountConvention
from xsigmamodules.Vectorization import vector, matrix, tensor, tensor
from xsigmamodules.util.numpy_support import xsigmaToNumpy, numpyToXsigma
from xsigmamodules.common import helper
from xsigmamodules.market import market_data
from xsigmamodules.simulation import simulation
from xsigmamodules.util.misc import xsigmaGetDataRoot, xsigmaGetTempDir
from xsigmamodules.Market import (
    discountCurveInterpolated,
    discountCurveId,
    anyId,
    anyContainer,
    anyObject,
    irVolatilitySabr,
    discountCurveFlat,
)

from xsigmamodules.Math import (
    normalDistribution,
    interpolation_enum,
    solverOptionsCeres,
    solverOptionsLm,
    solverOptionsNlopt,
    solverOptionsLmBuilder,
    levenberg_marquardt_solver_enum
)

# %%
# Markdown cell:
# # Folders

# %%
XSIGMA_DATA_ROOT = xsigmaGetDataRoot()
XSIGMA_TEST_ROOT = xsigmaGetTempDir()

# %%
print(XSIGMA_DATA_ROOT)

# %%
discount_id = discountCurveId("USD", "LIBOR.3M.USD")
diffusion_id = simulatedMarketDataIrId(discount_id)

discount_curve = discountCurveInterpolated.read_from_json(
    XSIGMA_DATA_ROOT + "/Data/discountCurve.json"
)
anyids = [anyId(discount_id)]
anyobject = [anyObject(discount_curve)]

correlation_mgr = correlationManager.read_from_json(
    XSIGMA_DATA_ROOT + "/Data/correlationManager.json"
)
anyids.append(anyId(correlationManagerId()))
anyobject.append(anyObject(correlation_mgr))

valuation_date = discount_curve.valuation_date()

target_config = calibrationIrTargetsConfiguration.read_from_json(
    XSIGMA_DATA_ROOT + "/Data/calibrationIrTargetsConfiguration.json"
)

ir_volatility_surface = irVolatilitySabr.read_from_json(
    XSIGMA_DATA_ROOT + "/Data/irVolatility.json"
)

# %%
diffusion_ids = [diffusion_id]
correlation = correlation_mgr.pair_correlation_matrix(diffusion_ids, diffusion_ids)

# %%
# Markdown cell:
# # Load data

# %%
# M_np = np.array([[1.0,	-0.5,  -0.5,	-0.5],
#                 [-0.5,	 1.0,	-0.5,	-0.5],
#                 [-0.5,	-0.5,	1.0,	-0.5],
#                 [-0.5,	-0.5,	-0.5,	1.0]], "d")
# correlation = numpyToXsigma(M_np)
# correlation_mgr = correlationManager(valuation_date, diffusion_ids, [4], correlation)
solver_opts = (solverOptionsLmBuilder()
                   .with_max_iterations(200)
                   .with_function_tolerance(5.0)
                   .with_aad_jacobian(False)
                   .with_debug(True)
                   .with_lambda(1.0e-02)
                   .with_accept_uphill_step(False)
                   .with_type(levenberg_marquardt_solver_enum.NIELSEN)
                   .with_alpha(0.75)
                   .with_parameter_tolerance(0)
                   .with_gradient_tolerance(0.0)
                   .with_epsilon(0.1)
                   .build())

volatility_bounds = [0.0001, 0.1]
decay_bounds = [0.0001, 1.0]
calibration_settings =( calibrationHjmSettingsBuilder()
                .with_solver_options(solver_opts)
                .with_type(parameter_markovian_hjm_enum.PICEWISE_CONSTANT)
                .with_number_of_factors(correlation.rows())
                .with_volatility_bounds(volatility_bounds)
                .with_decay_bounds(decay_bounds)
                .with_calibrate_correlation_flag(False)
                .with_calibrate_to_all_target_flag(False)
                .with_regularization_factor(0.00001)
                .with_regularization_flag(False)
                .build())

solver_opts =( solverOptionsLmBuilder()
                       .with_max_iterations(200)
                       .with_function_tolerance(5.0)
                       .with_aad_jacobian(True)
                       .with_debug(True)
                       .with_lambda(1.0e-02)
                       .with_accept_uphill_step(False)
                       .with_type(levenberg_marquardt_solver_enum.NIELSEN)
                       .with_alpha(0.75)
                       .with_parameter_tolerance(0)
                       .with_gradient_tolerance(0.0)
                       .with_epsilon(0.1)
                       .build())

calibration_settings_aad =(calibrationHjmSettingsBuilder()
                .with_solver_options(solver_opts)
                .with_type(parameter_markovian_hjm_enum.PICEWISE_CONSTANT)
                .with_number_of_factors(correlation.rows())
                .with_volatility_bounds(volatility_bounds)
                .with_decay_bounds(decay_bounds)
                .with_calibrate_correlation_flag(False)
                .with_calibrate_to_all_target_flag(False)
                .with_regularization_factor(0.00001)
                .with_regularization_flag(False)
                .build())

convention = dayCountConvention()

# %%
# print(target_config)

# %%
# Markdown cell:
# # Static data

# %%
mkt_data_obj = market_data.market_data(XSIGMA_DATA_ROOT)

# %%
calibrator = calibrationIrHjm(valuation_date, target_config)

# %%
# Markdown cell:
# # Run calibration

# %%
start = time.time()
parameter = calibrator.calibrate(
    parameterMarkovianHjmId(diffusion_id),
    calibration_settings_aad,
    discount_curve,
    ir_volatility_surface,
    correlation_mgr,
)
end = time.time()
m1 = end - start
print(end - start)

# %%
start = time.time()
parameter = calibrator.calibrate(
    parameterMarkovianHjmId(diffusion_id),
    calibration_settings,
    discount_curve,
    ir_volatility_surface,
    correlation_mgr,
)
end = time.time()
m2 = end - start
print(end - start)

# %%
m2 / m1

# %%
# Markdown cell:
# # Simulation

# %%
anyids.append(anyId(parameterMarkovianHjmId(diffusion_id)))
anyobject.append(anyObject(parameter))

anyids.append(anyId(dynamicInstructionIrId(diffusion_id)))
anyobject.append(anyObject(dynamicInstructionIrMarkovianHjm()))

anyids.append(anyId(measureId()))
anyobject.append(anyObject(measure(discount_id)))

num_of_paths = 262144
config = randomConfigBuilder().with_main_generator_type(random_enum.SOBOL_BROWNIAN_BRIDGE).with_seed(12765793).with_number_of_paths_per_batch(num_of_paths).build()

anyids.append(anyId(randomConfigId()))
anyobject.append(anyObject(config))

market = anyContainer(anyids, anyobject)

simulation_dates = helper.simulation_dates(valuation_date, "3M", 120)

maturity = max(simulation_dates)

sim = simulation.Simulation(
    mkt_data_obj,
    num_of_paths,
    target_config.frequency(),
    target_config.expiries(),
    target_config.cms_tenors(),
    target_config.coterminal(),
    maturity,
    simulation_dates,
)

sim.run_simulation(diffusion_ids, market, simulation_dates)

# %%
sim.plot(simulation_dates)
