"""
Converted from Jupyter notebook: CurveCalibration.ipynb
"""

# %%
import sys
import os.path

from datetime import date
from xsigmamodules.Core import timerLog
from xsigmamodules.test import Testing
from xsigmamodules.Engine import (
    curveCalibration,
    curveCalibrationDataRatesId,
    curveCalibrationDataInflationId,
    curveCalibrationData,
    curveCalibrationDataArray,
    curveCalibrationConfigId,
    curveCalibrationConfig,
    curveCalibrationConfigBuilder,
    curveCalibrationDatesConfigId,
    curveCalibrationDatesConfig,
    curveCalibrationDatesConfigBuilder,
    curveCalibrationInstrumentConfig,
    calibration_grid_enum,
)

from xsigmamodules.Math import (
    interpolation_enum,
    solver_enum,
    solverOptionsLmBuilder,
    solverOptionsCeresBuilder,
)

from xsigmamodules.Market import (
    currencyMappingConfig,
    discountDefinition,
    discountCurveId,
    discountCurve,
    forecastCurveId,
    forecastCurve,
    inflationCurveId,
    inflationCurve,
    swapDefaultConventionConfigId,
    swapDefaultConventionConfig,
    futureDefaultConventionConfig,
    futureDefaultConventionConfigId,
    xccyDefaultConventionConfig,
    xccyDefaultConventionConfigId,
    calendarId,
    currencyCalendarMappingId,
    currencyRfrMappingId,
    currencyIborMappingId,
    fxSpotMarket,
    fxSpotId,
    anyContainer,
    anyId,
    anyObject,
    valuationDatetime,
    valuationDatetimeId,
    discountCurveFlat,
    forecastCurveFlat,
    inflationDefaultConventionConfig,
    inflationDefaultConventionConfigBuilder,
    inflationDefaultConventionConfigId,
    inflationFixingBuilder,
    inflationFixingId,
    inflationSeasonalityBuilder,
    inflationSeasonalityId,
)

from xsigmamodules.Util import (
    currency,
    calendar,
    dayCountConvention,
    day_count_convention_enum,
    option_output_enum,
    yearMonthDay,
    tenor,
    key,
    business_day_convention_enum,
    future_type_enum,
    scheduleParametersBuilder,
)
from xsigmamodules.Instrument import (
    tradeInfoData,
    portfolio,
    deposit,
    future,
    irBasisSwap,
    irFly,
    irSpread,
    irSwap,
    irTermDeposit,
    fixedLeg,
    floatLeg,
)
from xsigmamodules.TestingUtil import TestingDataSerializer
from xsigmamodules.util.misc import xsigmaGetDataRoot, xsigmaGetTempDir
from xsigmamodules.market import market_data
from xsigmamodules.instrument.rates import IRSwap, IRBasisSwap, IRTermDeposit

# %%
DAYS_IN_YEAR = 365

# %%
def CurveCalibrationDatesConfig():
    # OIS dates and values
    ois_dates = [
        "19Mar2025",
        "07May2025",
        "18Jun2025",
        "30Jul2025",
        "17Sep2025",
        "29Oct2025",
        "10Dec2025",
        "28Jan2026",
        "18Mar2026",
        "29Apr2026",
        "17Jun2026",
        "29Jul2026",
        "16Sep2026",
        "28Oct2026",
        "09Dec2026",
        "27Jan2027",
        "17Mar2027",
        "28Apr2027",
        "16Jun2027",
        "28Jul2027",
        "15Sep2027",
        "27Oct2027",
        "15Dec2027",
    ]

    # Initialize ois_values with zeros, matching the length of ois_dates
    ois_values = [0.0] * len(ois_dates)

    # Return the curve calibration dates configuration
    return curveCalibrationDatesConfigBuilder().with_tenors_and_values(ois_dates, ois_values).build()

# %%
def curveCalibrationInstrumentsMarketRates(valuation_date, ccy, market):
    instruments = []
    # 1. Deposit instruments
    cash_tenor = [
        "DEPOSIT_1b",
        "DEPOSIT_1m",
        "DEPOSIT_2m",
        "DEPOSIT_3m",
        "DEPOSIT_6m",
        "DEPOSIT_12m",
    ]
    cash_implied = [4.3077, 4.4294, 4.5083, 4.5878, 4.7241, 4.9393]

    # Convert percentages to decimals
    cash_implied = [value / 100.0 for value in cash_implied]

    instruments.append(
        curveCalibrationData("RFR",
            "DEPOSIT_RFR", option_output_enum.PV, cash_tenor, cash_implied
        )
    )

    # 2. Future instruments
    fut_tenors = [
        "Mar25",
        "Apr25",
        "May25",
        "Jun25",
        "Jul25",
        "Aug25",
        "Sep25",
        "Oct25",
        "Nov25",
        "Dec25",
        "Jan26",
        "Feb26",
        "Mar26",
        "Apr26",
        "May26",
        "Jun26",
        "Jul26",
        "Aug26",
        "Sep26",
        "Oct26",
        "Nov26",
        "Dec26",
        "Jan27",
        "Feb27",
        "Mar27",
        "Apr27",
        "May27",
        "Jun27",
        "Jul27",
    ]

    # Add FUTURE_ prefix to each tenor
    fut_tenors = ["FUTURE_" + tenor for tenor in fut_tenors]

    fut_prices = [
        95.4296,
        95.4672,
        95.5208,
        95.5579,
        95.5936,
        95.6411,
        95.6836,
        95.7145,
        95.7495,
        95.7680,
        95.7887,
        95.8024,
        95.8132,
        95.8212,
        95.8295,
        95.8362,
        95.8399,
        95.8443,
        95.8481,
        95.8492,
        95.8492,
        95.8499,
        95.8479,
        95.8461,
        95.8461,
        95.8308,
        95.8493,
        95.8493,
        95.8378,
    ]

    instruments.append(
        curveCalibrationData("RFR",
            "FUTURE_RFR_1M", option_output_enum.PV, fut_tenors, fut_prices
        )
    )

    # 3. Swap instruments
    swap_ois_tenors = [
        "1y",
        "2y",
        "3y",
        "4y",
        "5y",
        "6y",
        "7y",
        "8y",
        "9y",
        "10y",
        "11y",
        "12y",
        "15y",
        "20y",
        "25y",
        "30y",
        "35y",
        "40y",
        "50y",
        "60y",
        "70y",
    ]

    # Add IRSWAP_ prefix to each tenor
    swap_ois_tenors = ["IRSWAP_" + tenor for tenor in swap_ois_tenors]

    swap_ois_par = [
        4.2199,
        4.0944,
        4.0508,
        4.0349,
        4.0309,
        4.0365,
        4.0448,
        4.0536,
        4.0633,
        4.0744,
        4.0869,
        4.1002,
        4.1322,
        4.1317,
        4.0663,
        3.9819,
        3.8831,
        3.7869,
        3.6019,
        3.4620,
        3.3604,
    ]

    # Convert percentages to decimals
    swap_ois_par = [value / 100.0 for value in swap_ois_par]

    instruments.append(
        curveCalibrationData("RFR",
            "IRSWAP_RFR_3M", option_output_enum.PAR, swap_ois_tenors, swap_ois_par
        )
    )

    # 4. Basis swap instruments
    basis_swap_ois_tenors = [
        "1y",
        "2y",
        "3y",
        "4y",
        "5y",
        "6y",
        "7y",
        "8y",
        "9y",
        "10y",
        "11y",
        "12y",
        "15y",
        "20y",
        "25y",
        "30y",
        "35y",
        "40y",
        "50y",
        "60y",
        "70y",
    ]

    # Add IRSWAP_ prefix to each tenor
    basis_swap_ois_tenors = ["IRBASISSWAP_" + tenor for tenor in basis_swap_ois_tenors]

    basis_swap_ois_par = [
        4.2199,
        4.0944,
        4.0508,
        4.0349,
        4.0309,
        4.0365,
        4.0448,
        4.0536,
        4.0633,
        4.0744,
        4.0869,
        4.1002,
        4.1322,
        4.1317,
        4.0663,
        3.9819,
        3.8831,
        3.7869,
        3.6019,
        3.4620,
        3.3604,
    ]

    # Convert percentages to decimals
    basis_swap_ois_par = [value / 10000.0 for value in basis_swap_ois_par]

    # instruments.append(curveCalibrationData("IRBASISSWAP_RFR_3M_IBOR3M_3M", option_output_enum.PAR, basis_swap_ois_tenors, basis_swap_ois_par))

    return curveCalibrationDataArray(valuation_date, instruments)

# %%
def curveCalibrationInstrumentsMarketFX(valuation_date, ccy, ccy_base, market):
    instruments = []
    # Cross-currency basis swap instruments
    ccbs_tenors = ["1y", "2y", "3y", "4y", "5y", "6y", "7y", "8y"]

    # Add CROSSCURRENCYBASISSWAP_ prefix to each tenor
    ccbs_tenors = ["CROSSCURRENCYBASISSWAP_" + tenor for tenor in ccbs_tenors]

    ccbs_rates = [2.2966, 2.3700, 2.1825, 2.1900, 2.2375, 2.1938, 2.1888, 2.0800]

    # Convert basis points to decimals (divide by 10000)
    ccbs_rates = [value / 10000.0 for value in ccbs_rates]

    # Create and add the cross-currency basis swap instrument
    instruments.append(
        curveCalibrationData("RFR",
            "CROSSCURRENCYBASISSWAP_RFR_3M_RFR_3M",
            option_output_enum.PAR,
            ccbs_tenors,
            ccbs_rates,
        )
    )

    # Return the curve calibration instruments market
    return curveCalibrationDataArray(valuation_date, instruments)

# %%
def curveCalibrationInstrumentsMarketInflation(
    valuation_date, ccy, inflation_index, market
):
    instruments = []
    # Inflation zero-coupon swap instruments
    inflation_tenors = [
        "1y",
        "2y",
        "3y",
        "4y",
        "5y",
        "6y",
        "7y",
        "8y",
        "9y",
        "10y",
        "12y",
        "15y",
        "20y",
        "25y",
        "30y",
    ]

    # Add INFLATIONZEROCOUPONSWAP_ prefix to each tenor
    inflation_tenors = [
        "INFLATIONZEROCOUPONSWAP_" + tenor for tenor in inflation_tenors
    ]

    inflation_rates = [
        2.2966,
        2.3700,
        2.1825,
        2.1900,
        2.2375,
        2.1938,
        2.1888,
        2.0800,
        2.1588,
        2.2738,
        2.0913,
        2.1578,
        1.9063,
        1.8713,
        1.8812,
    ]

    # Convert percentages to decimals (divide by 100)
    inflation_rates = [value / 100.0 for value in inflation_rates]

    # Create and add the inflation zero-coupon swap instrument
    instruments.append(
        curveCalibrationData("RFR",
            "INFLATIONZEROCOUPONSWAP_RFR_3M",
            option_output_enum.PAR,
            inflation_tenors,
            inflation_rates,
        )
    )

    # Return the curve calibration instruments market
    return curveCalibrationDataArray(valuation_date, instruments)

# %%
fromYear = 2025
valuationDate = yearMonthDay(fromYear, 2, 18).to_datetime()

# %%
def calibrate_rates(marketContainer, id, ccyBase, useBootstraping, useCeres, useAad):
    if id.ccy() == ccyBase:
        marketContainer.insert(
            anyId(
                curveCalibrationDataRatesId(
                    id.ccy(), ccyBase
                )
            ),
            anyObject(
                curveCalibrationInstrumentsMarketRates(
                    valuationDate, id.ccy(), marketContainer
                )
            ),
        )
    else:
        marketContainer.insert(
            anyId(fxSpotId(ccyBase, id.ccy())),
            anyObject(fxSpotMarket(valuationDate, 1.1)),
        )
        marketContainer.insert(
            anyId(
                curveCalibrationDataRatesId(
                    id.ccy(), ccyBase
                )
            ),
            anyObject(
                curveCalibrationInstrumentsMarketFX(
                    valuationDate, id.ccy(), ccyBase, marketContainer
                )
            ),
        )
    if useCeres:
        option = (
            solverOptionsCeresBuilder()
            .with_function_tolerance(1.0e-8)
            .with_gradient_tolerance(1.0e-8)
            .with_parameter_tolerance(1.0e-8)
            .with_max_iterations(25)
            .with_aad_jacobian(useAad)
            .build()
        )
    else:
        option = (
            solverOptionsLmBuilder()
            .with_function_tolerance(1.0e-8)
            .with_gradient_tolerance(1.0e-8)
            .with_parameter_tolerance(1.0e-8)
            .with_max_iterations(25)
            .with_aad_jacobian(useAad)
            .build()
        )

    marketContainer.insert(
        anyId(curveCalibrationConfigId(id.ccy(), id.index_name())),
        anyObject(
             curveCalibrationConfigBuilder()
            .with_bootstrap_stdev(2.0)
            .with_solver_options(option)
            .with_smoothing_weight(0.0001)
            .with_parameter_lower_bound(-3.0)
            .with_parameter_upper_bound(3.0)
            .with_date_mode(calibration_grid_enum.INSTRUMENT)
            .with_interpolation1(interpolation_enum.LINEAR)
            .with_interpolation2(interpolation_enum.CUBIC_SPLINE)
            .with_use_bootstrapping(useBootstraping)
            .build()
        ),
    )
    marketContainer.insert(
        anyId(curveCalibrationDatesConfigId(id.ccy())),
        anyObject(CurveCalibrationDatesConfig()),
    )

    market_data.discover(marketContainer, [anyId(id)])
    result = forecastCurve.static_cast(marketContainer.get(anyId(id)))

# %%
def calibrate_inflation(marketContainer, id, useBootstraping, useCeres, useAad):
    marketContainer.insert(
        anyId(inflationDefaultConventionConfigId(id)),
        anyObject(
            inflationDefaultConventionConfigBuilder()
                .with_observation_lag("1M")
                .with_business_day_convention(business_day_convention_enum.MODIFIED_FOLLOWING)
                .with_basis(day_count_convention_enum.ACT_360)
                .with_settlement_days(2)
                .with_interpolation_type(interpolation_enum.LINEAR)
                .with_day_of_the_month(1)
                .build()
        ),
    )

    marketContainer.insert(
        anyId(inflationFixingId(id)),
        anyObject(
            inflationFixingBuilder()
                .with_base_date(valuationDate)
                .with_historical_data([valuationDate], [1.0])
                .build()
        ),
    )

    marketContainer.insert(
        anyId(inflationSeasonalityId(id)),
        anyObject(
            inflationSeasonalityBuilder()
                .with_seasonality([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
                .build()
        ),
    )

    marketContainer.insert(
        anyId(curveCalibrationDataInflationId(id, id.ccy())),
        anyObject(
            curveCalibrationInstrumentsMarketInflation(
                valuationDate, id.ccy(), id.index_name(), marketContainer
            )
        ),
    )
    if useCeres:
        option = (
            solverOptionsCeresBuilder()
            .with_function_tolerance(1.0e-8)
            .with_gradient_tolerance(1.0e-8)
            .with_parameter_tolerance(1.0e-8)
            .with_max_iterations(25)
            .with_aad_jacobian(useAad)
            .build()
        )
    else:
        option = (
            solverOptionsLmBuilder()
            .with_function_tolerance(1.0e-8)
            .with_gradient_tolerance(1.0e-8)
            .with_parameter_tolerance(1.0e-8)
            .with_max_iterations(25)
            .with_aad_jacobian(useAad)
            .build()
        )  
    marketContainer.insert(
        anyId(curveCalibrationConfigId(id.ccy(), id.index_name())),
        anyObject(
            curveCalibrationConfigBuilder()
            .with_bootstrap_stdev(2.0)
            .with_solver_options(option)
            .with_smoothing_weight(0.0001)
            .with_parameter_lower_bound(-3.0)
            .with_parameter_upper_bound(3.0)
            .with_date_mode(calibration_grid_enum.INSTRUMENT)
            .with_interpolation1(interpolation_enum.LINEAR_EXPONENTIAL)
            .with_interpolation2(interpolation_enum.CUBIC_SPLINE)
            .with_use_bootstrapping(useBootstraping)
            .build()
        ),
    )

    result = inflationCurve.static_cast(marketContainer.get(anyId(id)))

# %%
def testVariations(useBootstraping, useCeres=True, useAad=True):
    timer = timerLog()
    timer.StartTimer()

    ccyEur = "EUR"
    ccyUsd = "USD"

    marketContainer = anyContainer()
    marketContainer.insert(
        anyId(valuationDatetimeId()), anyObject(valuationDatetime(valuationDate))
    )
    calibrate_rates(
        marketContainer,
        forecastCurveId(ccyUsd, "SOFR", "1b"),
        ccyUsd,
        useBootstraping,
        useCeres,
        useAad,
    )

    calibrate_rates(
        marketContainer,
        forecastCurveId(ccyEur, "ESTR", "1b"),
        ccyEur,
        useBootstraping,
        useCeres,
        useAad,
    )

    calibrate_rates(
        marketContainer,
        forecastCurveId(ccyUsd, "SOFR", "3m"),
        ccyUsd,
        useBootstraping,
        useCeres,
        useAad,
    )

    calibrate_rates(
        marketContainer,
        forecastCurveId(
            ccyEur, discountDefinition.xccy_discount_definition("USD.SOFR.1b"), "1b"
        ),
        ccyUsd,
        useBootstraping,
        useCeres,
        useAad,
    )

    calibrate_inflation(
        marketContainer,
        inflationCurveId(ccyUsd, "US.CPI"),
        useBootstraping,
        useCeres,
        useAad,
    )
    timer.StopTimer()
    time = timer.GetElapsedTime()
    print("Curve calibrration timer: {0}".format(time))

# %%
def testCurveCalibration():
    # Run tests with different combinations of parameters
    testVariations(False, False, True)
    testVariations(False, False, False)
    testVariations(False, True, True)
    testVariations(False, True, False)
    testVariations(True)

# %%
testCurveCalibration()

# %%
marketContainer = anyContainer()
ccyUsd = "USD"

swap_id = swapDefaultConventionConfigId(ccyUsd, "RFR")
calendar_id = calendarId("NYSE")
future_id = futureDefaultConventionConfigId(ccyUsd, "SOFR", "1m")
market_data.discover(
    marketContainer, [anyId(swap_id), anyId(calendar_id), anyId(future_id)]
)

discount = discountCurveId(ccyUsd, "USD.SOFR.1b")
index = forecastCurveId(ccyUsd, "SOFR", "1b")
cal = calendar.static_cast(marketContainer.get(anyId(calendar_id)))
swap_config = swapDefaultConventionConfig.static_cast(
    marketContainer.get(anyId(swap_id))
)
future_config = futureDefaultConventionConfig.static_cast(
    marketContainer.get(anyId(future_id))
)
settlement_days = str(swap_config.settlement_days()) + "b"

# %%
data = curveCalibrationInstrumentsMarketRates(valuationDate, "USD", marketContainer)
#data

# %%
priceable = []  # or use a dictionary: deposits = {}
trade_info = []
output_types = []
asset_info = []

# %%
cash_tenor = [
    "DEPOSIT_1b",
    "DEPOSIT_1m",
    "DEPOSIT_2m",
    "DEPOSIT_3m",
    "DEPOSIT_6m",
    "DEPOSIT_12m",
]
market_values = data.asset_data("DEPOSIT").values()

for tenor in cash_tenor:
    # Get trade info for current tenor
    info = tradeInfoData(tenor)

    # Calculate start date
    start_date = info.start_date_not_adjusted(valuationDate)

    # Create deposit object
    t = deposit(discount, index, start_date, info.period(), cal, swap_config)

    trade_info.append(tenor)
    output_types.append(option_output_enum.PV)
    priceable.append(t)
    asset_info.append("DEPOSIT")

# %%
fut_tenors = [
    "Mar25",
    "Apr25",
    "May25",
    "Jun25",
    "Jul25",
    "Aug25",
    "Sep25",
    "Oct25",
    "Nov25",
    "Dec25",
    "Jan26",
    "Feb26",
    "Mar26",
    "Apr26",
    "May26",
    "Jun26",
    "Jul26",
    "Aug26",
    "Sep26",
    "Oct26",
    "Nov26",
    "Dec26",
    "Jan27",
    "Feb27",
    "Mar27",
    "Apr27",
    "May27",
    "Jun27",
    "Jul27",
]

# Add FUTURE_ prefix to each tenor
fut_tenors = ["FUTURE_" + tenor for tenor in fut_tenors]
market_values = market_values + data.asset_data("FUTURE").values()

for tenor in fut_tenors:
    # Get trade info for current tenor
    info = tradeInfoData(tenor)

    # Calculate start date
    start_date = info.start_date_not_adjusted(valuationDate)

    # Create deposit object
    t = future(discount, index, start_date, info.period(), cal, future_config)

    trade_info.append(tenor)
    output_types.append(option_output_enum.PV)
    priceable.append(t)
    asset_info.append("FUTURE")

# %%
swap_tenors = [
    "1y",
    "2y",
    "3y",
    "4y",
    "5y",
    "6y",
    "7y",
    "8y",
    "9y",
    "10y",
    "11y",
    "12y",
    "15y",
    "20y",
    "25y",
    "30y",
    "35y",
    "40y",
    "50y",
    "60y",
    "70y",
]

# %%
# 3. Swap instruments
tenors = ["IRSWAP_" + tenor for tenor in swap_tenors]
market_values = market_values + data.asset_data("IRSWAP").values()
market_values = list(market_values)

for tenor in tenors:
    # Get trade info for current tenor
    info = tradeInfoData(tenor)

    # Calculate start date
    start_date = info.start_date_not_adjusted(valuationDate)
    effective_date = tradeInfoData.adjust_date(
        start_date, settlement_days, cal, swap_config.business_day_convention()
    )
    maturity = tradeInfoData.adjust_date(
        effective_date, info.period(), cal, swap_config.business_day_convention()
    )

    # Create deposit object
    t = IRSwap(discount, index, effective_date, maturity, cal, swap_config)

    trade_info.append(tenor)
    output_types.append(option_output_enum.PAR)
    priceable.append(t)
    asset_info.append("IRSWAP")

# %%
# 4. basis Swap instruments
tenors = ["IRBASISSWAP_" + tenor for tenor in swap_tenors]

settlement_days = str(swap_config.settlement_days()) + "b"
index_libor = forecastCurveId(ccyUsd, "SOFR", "3m")
for tenor in tenors:
    # Get trade info for current tenor
    info = tradeInfoData(tenor)

    # Calculate start date
    start_date = info.start_date_not_adjusted(valuationDate)
    effective_date = tradeInfoData.adjust_date(
        start_date, settlement_days, cal, swap_config.business_day_convention()
    )
    maturity = tradeInfoData.adjust_date(
        effective_date, info.period(), cal, swap_config.business_day_convention()
    )

    # Create deposit object
    t = IRBasisSwap(
        discount,
        index_libor,
        index,
        effective_date,
        maturity,
        cal,
        "3m",
        "3m",
        swap_config,
    )

    trade_info.append(tenor)
    output_types.append(option_output_enum.PAR)
    priceable.append(t)
    asset_info.append("IRBASISSWAP")
    market_values.append(0)

# %%
# 5. term deposit instruments
tenors = ["IRTERMDEPOSIT_" + tenor for tenor in swap_tenors]

for tenor in tenors:
    # Get trade info for current tenor
    info = tradeInfoData(tenor)

    # Calculate start date
    start_date = info.start_date_not_adjusted(valuationDate)
    effective_date = tradeInfoData.adjust_date(
        start_date, settlement_days, cal, swap_config.business_day_convention()
    )
    maturity = tradeInfoData.adjust_date(
        effective_date, info.period(), cal, swap_config.business_day_convention()
    )

    # Create deposit object
    t = IRTermDeposit(discount, index, effective_date, maturity, cal, swap_config)

    trade_info.append(tenor)
    output_types.append(option_output_enum.PV)
    priceable.append(t)
    asset_info.append("IRTERMDEPOSIT")
    market_values.append(0)

# %%
# 6. fly instruments
fly_tenors = [
    "2s3s5s",
    "2s5s10s",
    "2s10s20s",
    "3s4s5s",
    "4s5s6s",
    "5s6s7s",
    "5s7s10s",
    "5s10s15s",
    "5s10s30s",
    "6s7s8s",
    "7s8s9s",
    "7s10s15s",
    "8s9s10s",
    "10s11s12s",
    "10s12s15s",
    "10s15s20s",
    "10s15s30s",
    "10s20s30s",
    "15s17s20s",
    "15s20s25s",
    "15s20s30s",
    "15s25s35s",
    "20s25s30s",
    "20s30s40s",
    "25s30s35s",
    "30s35s40s",
    "30s40s50s",
]

tenors = ["IRFLY_" + tenor for tenor in fly_tenors]

for tenor in tenors:
    # Get trade info for current tenor
    info = tradeInfoData(tenor)

    # Calculate start date
    start_date = info.start_date_not_adjusted(valuationDate)
    effective_date = tradeInfoData.adjust_date(
        start_date, settlement_days, cal, swap_config.business_day_convention()
    )
    maturities = tradeInfoData.extract_maturities(info.period())
    swaps = []
    max_maturity = None
    for m in maturities:
        maturity = tradeInfoData.adjust_date(
            effective_date, str(m) + "Y", cal, swap_config.business_day_convention()
        )
        swaps.append(
            IRSwap(discount, index, effective_date, maturity, cal, swap_config)
        )
        if max_maturity is None or maturity > max_maturity:
            max_maturity = maturity

    # Create deposit object
    t = irFly(effective_date, max_maturity, swaps[0], swaps[1], swaps[2])

    trade_info.append(tenor)
    output_types.append(option_output_enum.PV)
    priceable.append(t)
    asset_info.append("IRFLY")
    market_values.append(0)

# %%
# 7. spread instruments
spread_tenors = [
    "1s2s",
    "2s5s",
    "2s10s",
    "2s20s",
    "3s4s",
    "3s5s",
    "5s7s",
    "5s10s",
    "5s30s",
    "10s12s",
    "10s15s",
    "10s20s",
    "10s25s",
    "10s30s",
    "12s20s",
    "15s25s",
    "15s30s",
    "20s30s",
    "30s35s",
    "30s40s",
    "30s50s",
    "40s50s",
    "50s60s",
    "50s70s",
    "50s80s",
    "50s90s",
    "50s100s",
]

tenors = ["IRSPREAD_" + tenor for tenor in spread_tenors]

for tenor in tenors:
    # Get trade info for current tenor
    info = tradeInfoData(tenor)

    # Calculate start date
    start_date = info.start_date_not_adjusted(valuationDate)
    effective_date = tradeInfoData.adjust_date(
        start_date, settlement_days, cal, swap_config.business_day_convention()
    )
    maturities = tradeInfoData.extract_maturities(info.period())
    swaps = []
    max_maturity = None
    for m in maturities:
        maturity = tradeInfoData.adjust_date(
            effective_date, str(m) + "Y", cal, swap_config.business_day_convention()
        )
        swaps.append(
            IRSwap(discount, index, effective_date, maturity, cal, swap_config)
        )
        if max_maturity is None or maturity > max_maturity:
            max_maturity = maturity

    # Create deposit object
    t = irSpread(effective_date, max_maturity, swaps[0], swaps[1])
    priceable.append(t)

    trade_info.append(tenor)
    output_types.append(option_output_enum.PV)
    asset_info.append("IRSPREAD")
    market_values.append(0)

# %%
p = portfolio(priceable, output_types)

# %%
marketContainer.insert(
    anyId(valuationDatetimeId()), anyObject(valuationDatetime(valuationDate))
)
calibrate_rates(
    marketContainer, forecastCurveId(ccyUsd, "SOFR", "1b"), ccyUsd, False, False, True
)
calibrate_rates(
    marketContainer, forecastCurveId(ccyUsd, "SOFR", "3M"), ccyUsd, False, False, True
)

# %%
prices = p.price(marketContainer)

# %%
import pandas as pd

df = pd.DataFrame(
    {
        "asset_info": asset_info,
        "trade_info": trade_info,
        "prices": prices,
        "market_values": market_values,
        "output_types": output_types,
    }
)

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

# %%
filtered_df = df[df["asset_info"] == "DEPOSIT"]
print(filtered_df)

# %%
filtered_df = df[df["asset_info"] == "FUTURE"]
print(filtered_df)

# %%
filtered_df = df[df["asset_info"] == "IRSWAP"]
print(filtered_df)

# %%
filtered_df = df[df["asset_info"] == "IRBASISSWAP"]
print(filtered_df)

# %%
filtered_df = df[df["asset_info"] == "IRSPREAD"]
print(filtered_df)

# %%
filtered_df = df[df["asset_info"] == "IRFLY"]
print(filtered_df)

# %%
filtered_df = df[df["asset_info"] == "IRTERMDEPOSIT"]
print(filtered_df)
