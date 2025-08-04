"""
Converted from Jupyter notebook: CurveCalibrationEUR.ipynb
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
    inflationDefaultConventionConfigId,
    inflationFixing,
    inflationFixingId,
    inflationSeasonality,
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
fromYear = 2025
valuationDate = yearMonthDay(fromYear, 2, 18).to_datetime()

# %%
# Unified Instrument Data Structure
# =================================
# Single data structure that can be used for both:
# 1. Creating curveCalibrationData objects
# 2. Creating priceable instruments

# Instrument specifications: (asset_name, index_info, output_type, tenors, values, weights, instrument_type)
EUR_INSTRUMENTS = [
    # Deposits
    ("DEPOSIT_IBOR", "IBOR", option_output_enum.PV, 
     ["1m", "3m", "6m", "12m"], [v/100 for v in [2.6160, 2.5100, 2.4890, 2.4240]], [1.0, 1.0, 1.0, 1.0], "DEPOSIT"),
    
    # Futures 1M
    ("FUTURE_IBOR1M_1M", "IBOR1M", option_output_enum.PV,
     ["Mar25", "Apr25", "May25", "Jun25", "Jul25", "Aug25"],
     [97.5855, 97.6849, 97.7751, 97.8297, 97.8728, 97.9142], [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], "FUTURE"),
    
    # Futures 3M
    ("FUTURE_IBOR3M_3M", "IBOR3M", option_output_enum.PV,
     ["Sep25", "Dec25", "Mar26", "Jun26", "Sep26", "Dec26", "Mar27", "Jun27", "Sep27", "Dec27"],
     [97.9425, 97.9894, 97.9829, 97.9493, 97.9153, 97.8800, 97.8395, 97.8080, 97.7835, 97.7650], [1.0]*10, "FUTURE"),
    
    # RFR Swaps
    ("IRSWAP_RFR_3M", "RFR", option_output_enum.PAR,
     ["4y", "5y", "6y", "7y", "8y", "9y", "10y", "11y", "12y", "15y", "17y", "20y", "25y", "30y", "35y", "40y", "50y", "60y"],
     [v/100 for v in [2.0952, 2.1305, 2.1627, 2.1946, 2.2270, 
                      2.2597, 2.2905, 2.3190, 2.3452, 2.3933, 
                      2.4062, 2.3886, 2.3219, 2.2548, 2.2090, 
                      2.1697, 2.0886, 2.0266]], [1.0]*18, "SWAP"),
    
    # IBOR3M Swaps
    ("IRSWAP_IBOR3M_3M", "IBOR3M", option_output_enum.PAR,
     ["1y",  "2y",  "3y",  "4y",  "5y",  "6y",
      "7y",  "8y",  "9y",  "10y", "11y", "12y",
      "15y", "20y", "25y", "30y", "35y", "40y",
      "50y", "60y", "70y", "80y", "90y", "100y"],
     [v/100 for v in [2.2576, 2.1817, 2.2011, 2.2336, 2.2647, 2.2925,
                      2.3203, 2.3501, 2.3798, 2.4078, 2.4336, 2.4578,
                      2.5041, 2.4848, 2.4098, 2.3353, 2.2825, 2.2368,
                      2.1433, 2.0693, 2.0117, 1.9689, 1.9361, 1.9104]], [1.0]*24, "SWAP"),
    
    # IBOR6M Swaps
    ("IRSWAP_IBOR6M_6M", "IBOR6M", option_output_enum.PAR,
     ["1y", "2y", "3y", "4y", "5y", "6y", "7y", "8y", "9y", "10y", 
      "11y", "12y", "15y", "17y", "20y", "25y", "30y", "35y", "40y",
      "50y", "60y", "70y", "80y", "90y", "100y"],
     [v/100 for v in [2.2576, 2.2627, 2.2742, 2.2993, 2.3227, 2.3438, 2.3648,
        2.3870, 2.4091, 2.4298, 2.4483, 2.4651, 2.4926, 2.4874,
        2.4533, 2.3655, 2.2808, 2.2182, 2.1638, 2.0558, 1.9788,
        1.9218, 1.8795, 1.8471, 1.8218]], [1.0]*25, "SWAP"),
    
    # Butterfly Spreads
    ("IRFLY_IBOR6M_6M", "IBOR6M", option_output_enum.PAR,
     ["2s3s4s", "2s3s5s", "2s5s10s", "2s10s20s", "3s4s5s", "4s5s6s", 
      "5s6s7s", "5s7s10s", "5s10s15s", "5s10s30s", "6s7s8s", "7s8s9s", 
      "7s10s15s", "8s9s10s", "10s11s12s", "10s12s15s", "10s15s20s", "10s15s30s", 
      "10s20s30s", "15s17s20s", "15s20s25s", "15s20s30s", "15s25s35s", "20s25s30s", 
      "20s30s40s", "25s30s35s", "30s35s40s", "30s40s50s"],
     [v/10000 for v in [-1.36, -3.70, -4.71, 14.36, 0.17, 0.23, 0.01, 
                        -2.29, 4.43, 25.61, -0.12, 0.01, 0.22, 0.14, 0.17, 
                        0.78, 10.21, 27.46, 19.60, 2.89, 4.85, 13.32, 2.02, 
                        -0.31, -5.55, -2.21, -0.82, -0.90]], [0.0]*28, "FLY"),
    
    # Spread Instruments
    ("IRSPREAD_IBOR6M_6M", "IBOR6M", option_output_enum.PAR,
     ["1s2s", "2s5s", "2s10s", "2s20s", "3s4s", "3s5s", "5s7s", "5s10s", "5s30s", 
      "10s12s", "10s15s", "10s20s", "10s25s", "10s30s", "12s20s", "15s25s", 
      "15s30s", "20s30s", "30s35s", "30s40s", "30s50s", "40s50s", "50s60s", 
      "50s70s", "50s80s", "50s90s", "50s100s"],
     [v/10000 for v in [0.51, 6.00, 16.71, 19.06, 2.51, 4.85, 4.21, 10.71, 
                        -4.19, 3.53, 6.28, 2.35, -6.43, -14.90, -1.18, -12.71, 
                        -21.18, -17.25, -6.26, -11.70, -22.50, -10.80, -7.70, 
                        -13.40, -17.63, -20.87, -23.40]], [0.0]*27, "SPREAD"),
    
    # Basis Swaps
    ("IRBASISSWAP_IBOR1M_1M_IBOR3M_3M", "IBOR1M", option_output_enum.PAR,
     ["3M", "6M", "9M", "1Y", "18M", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", 
      "8Y", "9Y", "10Y", "12Y", "15Y", "20Y", "25Y", "30Y", "40Y", "50Y", 
      "60Y", "1y_1y", "2y_1y", "3y_1y", "4y_1y", "5y_1y", "5y_2y"],
     [v/10000 for v in [6.38, 7.88, 8.41, 8.55, 8.35, 8.1, 7.5, 7, 6.3, 
                        5.9, 4.6, 3.8, 3.15, 2.5, 1.1, -0.6, -2, -3.6, -5, 
                        -5.8, -6.1, -6.4, 7.63, 6.28, 5.42, 3.34, 1.22, 0]], [1.0]*28, "BASIS"),
    
    ("IRBASISSWAP_IBOR3M_3M_IBOR6M_6M", "IBOR3M", option_output_enum.PAR,
     ["3M", "6M", "9M", "1Y", "18M", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y",
      "9Y", "10Y", "12Y", "15Y", "20Y", "25Y", "30Y", "40Y", "50Y", "60Y",
      "1y_1y", "2y_1y", "3y_1y", "4y_1y", "5y_1y", "5y_2y"],
     [v/10000 for v in [-2.1,        -0.77419761,  0.80756842, -0.00000478,  5.76281393,  7.92791432,
  7.15408943,  6.42544117,  5.67236543,  5.01693797,  4.3516754,   3.6070912,
  2.86399112,  2.15030775,  0.71328251, -1.12359268, -3.07737183, -4.32902081,
 -5.32718428, -7.13742646, -8.55783056, -8.85311625, 16.66036901,  5.00132004,
  4.1934537,   2.49319281,  1.51537572,  0.7824135]], [1.0]*28, "BASIS"),
    
    ("IRBASISSWAP_IBOR3M_3M_IBOR12M_12M", "IBOR12M", option_output_enum.PAR,
     ["3M", "6M", "9M", "1Y", "18M", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y",
      "9Y", "10Y", "15Y", "20Y", "25Y", "30Y", "40Y", "70Y", "3y_1y", 
      "4y_1y", "5y_1y", "5y_2y", "6y_1y", "7y_1y"],
     [v/10000 for v in [8.5, 9, 14.03, 19.95, 19.97, 17.85, 16.65, 16.35, 16.2, 
                        16.45, 16.05, 15.8, 15.55, 15.6, 15.75, 15.25, 15.05, 14.2, 
                        14.4, 14.79, 15.4, 15.57, 17.79, 15.64, 13.45, 13.89]], [1.0]*26, "BASIS"),
    
    ("IRBASISSWAP_RFR_3M_IBOR3M_3M", "RFR", option_output_enum.PAR,
     ["1y",  "2y",  "3y",  "4y",  "5y",  "6y",  "7y",  "8y",  "9y",  "10y", "11y",
		"12y", "15y", "20y", "25y", "30y", "35y", "40y", "50y", "60y", "70y"],
     [v/10000 for v in [11.419882556154076, 8.5183744934109985, 10.437079038047681, 13.474586996457133,
		13.062282465626926, 12.638657382564298, 12.244196486209074, 11.988013659876516,
		11.707178589993863, 11.440771250876595, 11.184195607348961, 10.993973057744214,
		10.330220615512619, 9.4336617722757231, 8.6536151437404101, 7.9285990876299989,
		7.2509723442677168, 6.6400136856970069, 5.4438021319158788, 4.2734575410359205,
		2.9554714511050446]], [1.0]*21, "BASIS")
]

def get_calibration_tenors(tenors, instrument_type):
    """Add appropriate prefixes to tenors based on instrument type"""
    prefix_map = {
        "DEPOSIT": "DEPOSIT_",
        "FUTURE": "FUTURE_",
        "SWAP": "IRSWAP_",
        "BASIS": "IRBASISSWAP_",
        "FLY": "IRFLY_",
        "SPREAD": "IRSPREAD_"
    }
    prefix = prefix_map.get(instrument_type, "")
    return [prefix + tenor for tenor in tenors]

def curveCalibrationInstrumentsMarketRates(valuation_date):
    """Create curveCalibrationDataArray from unified instrument data"""
    instruments = []
    
    for asset_name, index_info, output_type, tenors, values, weights, inst_type in EUR_INSTRUMENTS:
        calibration_tenors = get_calibration_tenors(tenors, inst_type)
        instruments.append(
            curveCalibrationData(index_info, asset_name, output_type, calibration_tenors, values, weights)
        )
    
    return curveCalibrationDataArray(valuation_date, instruments)

def filter_instruments_by_type(instrument_type):
    """Filter instruments by type for specific analysis"""
    return [spec for spec in EUR_INSTRUMENTS if spec[6] == instrument_type]

def get_instrument_summary():
    """Get summary of all instruments"""
    type_counts = {}
    total = 0
    
    for spec in EUR_INSTRUMENTS:
        inst_type = spec[6]  # instrument_type is now at index 6
        count = len(spec[3])  # tenors
        
        if inst_type not in type_counts:
            type_counts[inst_type] = 0
        type_counts[inst_type] += count
        total += count
    
    return type_counts, total

# Display summary
type_counts, total_instruments = get_instrument_summary()
print(f"Unified EUR Instrument Data Structure with Weights")
print(f"Total instruments: {total_instruments}")
print("Breakdown by type:")
for inst_type, count in type_counts.items():
    # Show weight info
    weight_info = "weight=1.0" if inst_type in ["DEPOSIT", "FUTURE", "SWAP"] else "weight=0.0"
    print(f"  {inst_type}: {count} instruments ({weight_info})")

data=curveCalibrationInstrumentsMarketRates(valuationDate)

# %%
def calibrate_rates(marketContainer, id, ccyBase, useBootstraping=False, useCeres=False, useAad=True):
    marketContainer.insert(
        anyId(curveCalibrationDataRatesId(id.ccy(), ccyBase)),
        anyObject(
            curveCalibrationInstrumentsMarketRates(valuationDate)
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
def testVariations(useBootstraping, useCeres=False, useAad=True):
    timer = timerLog()
    timer.StartTimer()

    ccy = "EUR"

    marketContainer = anyContainer()
    marketContainer.insert(
        anyId(valuationDatetimeId()), anyObject(valuationDatetime(valuationDate))
    )

    calibrate_rates(
        marketContainer,
        forecastCurveId(ccy, "ESTR", "1b"),
        ccy,
        useBootstraping,
        useCeres,
        useAad,
    )

    calibrate_rates(
        marketContainer,
        forecastCurveId(ccy, "EURIBOR", "1M"),
        ccy,
        useBootstraping,
        useCeres,
        useAad,
    )

    calibrate_rates(
        marketContainer,
        forecastCurveId(ccy, "EURIBOR", "3m"),
        ccy,
        useBootstraping,
        useCeres,
        useAad,
    )

    calibrate_rates(
        marketContainer,
        forecastCurveId(ccy, "EURIBOR", "6m"),
        ccy,
        useBootstraping,
        useCeres,
        useAad,
    )

    calibrate_rates(
        marketContainer,
        forecastCurveId(ccy, "EURIBOR", "12m"),
        ccy,
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
    #testVariations(False, True, True)
    testVariations(False, False, False)
    #testVariations(False, True, False)
    testVariations(True)

# %%
#testCurveCalibration()

# %%
marketContainer = anyContainer()
ccy = "EUR"

swap_id = swapDefaultConventionConfigId(ccy, "RFR")
calendar_id = calendarId("EUR")
future_1m_id = futureDefaultConventionConfigId(ccy, "EURIBOR", "1m")
future_3m_id = futureDefaultConventionConfigId(ccy, "EURIBOR", "3m")
market_data.discover(
    marketContainer, [anyId(swap_id), anyId(calendar_id), anyId(future_1m_id), anyId(future_3m_id)]
)

discount = discountCurveId(ccy, "EUR.ESTR.1b")
index = forecastCurveId(ccy, "ESTR", "1b")

cal = calendar.static_cast(marketContainer.get(anyId(calendar_id)))

swap_config = swapDefaultConventionConfig.static_cast(
    marketContainer.get(anyId(swap_id))
)

future_1m_config = futureDefaultConventionConfig.static_cast(
    marketContainer.get(anyId(future_1m_id))
)

future_3m_config = futureDefaultConventionConfig.static_cast(
    marketContainer.get(anyId(future_3m_id))
)

settlement_days = str(swap_config.settlement_days()) + "b"

# %%
data = curveCalibrationInstrumentsMarketRates(valuationDate)

# %%
marketContainer.insert(
    anyId(valuationDatetimeId()), anyObject(valuationDatetime(valuationDate))
)

calibrate_rates(
    marketContainer,
    forecastCurveId(ccy, "ESTR", "1b"),
    ccy
)

calibrate_rates(
    marketContainer,
    forecastCurveId(ccy, "EURIBOR", "1M"),
    ccy
)

calibrate_rates(
    marketContainer,
    forecastCurveId(ccy, "EURIBOR", "3m"),
    ccy
)

calibrate_rates(
    marketContainer,
    forecastCurveId(ccy, "EURIBOR", "6m"),
    ccy
)

calibrate_rates(
    marketContainer,
    forecastCurveId(ccy, "EURIBOR", "12m"),
    ccy
)

# %%
def create_forecast_curve_id(swap_string):
    """Parse type_XXX_ZZZ and create forecastCurveId entrie"""
    parts = swap_string.split('_')
    xxx, zzz = parts[1], parts[2]
    
    # Apply IBOR rule for both XXX and YYY
    return forecastCurveId(ccy, "EURIBOR", zzz.lower()) if "IBOR" in xxx.upper() else index

# %%
def create_forecast_curve_ids(swap_string):
    """Parse IRBASISSWAP_XXX_ZZZ_YYY_AAA and create 2 forecastCurveId entries"""
    parts = swap_string.split('_')
    xxx, zzz, yyy, aaa = parts[1], parts[2], parts[3], parts[4]
    
    # Apply IBOR rule for both XXX and YYY
    index_basis = forecastCurveId(ccy, "EURIBOR", zzz.lower()) if "IBOR" in xxx.upper() else index
    index_base = forecastCurveId(ccy, "EURIBOR", aaa.lower()) if "IBOR" in yyy.upper() else index
    
    return [index_basis, index_base]

# %%
priceable = []  # or use a dictionary: deposits = {}
trade_info = []
output_types = []
asset_info = []

# %%
cash_tenor = get_calibration_tenors(EUR_INSTRUMENTS[0][3], EUR_INSTRUMENTS[0][6])

market_values = EUR_INSTRUMENTS[0][4]
for tenor in cash_tenor:
    # Get trade info for current tenor
    info = tradeInfoData(tenor)

    # Calculate start date
    start_date = info.start_date_not_adjusted(valuationDate)
    # Create deposit object
    forecast_index=forecastCurveId(ccy, "EURIBOR", info.period())
    t = deposit(discount, forecast_index, start_date, info.period(), cal, swap_config)

    trade_info.append(tenor)
    output_types.append(option_output_enum.PV)
    priceable.append(t)
    asset_info.append("DEPOSIT")

# %%
for asset_name, index_info, output_type, tenors, values, weights, inst_type in EUR_INSTRUMENTS:
    if(inst_type=="FUTURE"):
        market_values = market_values + values
        tenors = get_calibration_tenors(tenors, inst_type)
        for tenor in tenors:
            # Get trade info for current tenor
            info = tradeInfoData(tenor)
        
            # Calculate start date
            start_date = info.start_date_not_adjusted(valuationDate)
        
            # Create deposit object
            forecast_index = create_forecast_curve_id(asset_name)
            future_config  = future_3m_config if forecast_index.frequency()=="3m" else future_1m_config

            t = future(discount, forecast_index, start_date, info.period(), cal, future_config)
        
            trade_info.append(tenor)
            output_types.append(output_type)
            priceable.append(t)
            asset_info.append(asset_name)

# %%
# 3. Swap instruments
for asset_name, index_info, output_type, tenors, values, weights, inst_type in EUR_INSTRUMENTS:
    if(inst_type=="SWAP"):
        market_values = market_values + values
        tenors = get_calibration_tenors(tenors, inst_type)
        forecast_index = create_forecast_curve_id(asset_name)
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
            freq = forecast_index.frequency() if forecast_index.frequency() != "1b" else "3M"
            # Create deposit object
            t = IRSwap(discount, forecast_index, effective_date, maturity, cal, swap_config, freq)
        
            trade_info.append(tenor)
            output_types.append(output_type)
            priceable.append(t)
            asset_info.append(asset_name)

# %%
# 4. basis Swap instruments
settlement_days = str(swap_config.settlement_days()) + "b"

for asset_name, index_info, output_type, tenors, values, weights, inst_type in EUR_INSTRUMENTS:
    if(inst_type=="BASIS"):
        market_values = market_values + values
        tenors = get_calibration_tenors(tenors, inst_type)
        index_basis, index_base = create_forecast_curve_ids(asset_name)
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
            freq_base = index_base.frequency() if index_base.frequency() != "1b" else "3M"
            freq = index_basis.frequency() if index_basis.frequency() != "1b" else "3M"
            t = IRBasisSwap(
                discount,
                index_basis,
                index_base,
                effective_date,
                maturity,
                cal,
                freq,
                freq_base,
                swap_config,
            )
        
            trade_info.append(tenor)
            output_types.append(output_type)
            priceable.append(t)
            asset_info.append(asset_name)

# %%
# 6. fly instruments
for asset_name, index_info, output_type, tenors, values, weights, inst_type in EUR_INSTRUMENTS:
    if(inst_type=="FLY"):
        market_values = market_values + values
        tenors = get_calibration_tenors(tenors, inst_type)
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
            forecast_index = create_forecast_curve_id(asset_name)
            for m in maturities:
                maturity = tradeInfoData.adjust_date(
                    effective_date, str(m) + "Y", cal, swap_config.business_day_convention()
                )
                swaps.append(
                    IRSwap(discount, forecast_index, effective_date, maturity, cal, swap_config)
                )
                if max_maturity is None or maturity > max_maturity:
                    max_maturity = maturity
        
            # Create deposit object
            t = irFly(effective_date, max_maturity, swaps[0], swaps[1], swaps[2])
        
            trade_info.append(tenor)
            output_types.append(output_type)
            priceable.append(t)
            asset_info.append(asset_name)

# %%
# 7. spread instruments
for asset_name, index_info, output_type, tenors, values, weights, inst_type in EUR_INSTRUMENTS:
    if(inst_type=="SPREAD"):
        market_values = market_values + values
        tenors = get_calibration_tenors(tenors, inst_type)
        forecast_index = create_forecast_curve_id(asset_name)
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
                    IRSwap(discount, forecast_index, effective_date, maturity, cal, swap_config)
                )
                if max_maturity is None or maturity > max_maturity:
                    max_maturity = maturity
        
            # Create deposit object
            t = irSpread(effective_date, max_maturity, swaps[1], swaps[0])
            priceable.append(t)
        
            trade_info.append(tenor)
            output_types.append(output_type)
            asset_info.append(asset_name)

# %%
p = portfolio(priceable, output_types)
print(len(priceable))
print(len(output_types))

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
    }
)
df["diff"] = df["prices"] - df["market_values"]
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

# %%
filtered_df = df[df["asset_info"] == "DEPOSIT"]
print(filtered_df)

# %%
filtered_df = df[df["asset_info"] == "FUTURE_IBOR3M_3M"]
display_df = filtered_df.copy()
display_df["asset_info"] = "FUTURE"
print(display_df)

# %%
filtered_df = df[df["asset_info"] == "FUTURE_IBOR1M_1M"]
display_df = filtered_df.copy()
display_df["asset_info"] = "FUTURE"
print(display_df)

# %%
filtered_df = df[df["asset_info"] == "IRSWAP_RFR_3M"]
display_df = filtered_df.copy()
display_df["asset_info"] = "IRSWAP"
print(display_df)

# %%
filtered_df = df[df["asset_info"] == "IRSWAP_IBOR3M_3M"]
display_df = filtered_df.copy()
display_df["asset_info"] = "IRSWAP"
print(display_df)

# %%
filtered_df = df[df["asset_info"] == "IRSWAP_IBOR6M_6M"]
display_df = filtered_df.copy()
display_df["asset_info"] = "IRSWAP"
print(display_df)

# %%
filtered_df = df[df["asset_info"] == "IRFLY_IBOR6M_6M"]
display_df = filtered_df.copy()
display_df["asset_info"] = "IRFLY"
print(display_df)

# %%
filtered_df = df[df["asset_info"] == "IRSPREAD_IBOR6M_6M"]
display_df = filtered_df.copy()
display_df["asset_info"] = "IRSPREAD"
print(display_df)

# %%
filtered_df = df[df["asset_info"] == "IRBASISSWAP_IBOR1M_1M_IBOR3M_3M"]
display_df = filtered_df.copy()
display_df["asset_info"] = "IRBASISSWAP"
print(display_df)

# %%
import numpy as np
filtered_df = df[df["asset_info"] == "IRBASISSWAP_IBOR3M_3M_IBOR6M_6M"]
display_df = filtered_df.copy()
display_df["asset_info"] = "IRBASISSWAP"
print(display_df)

# %%
filtered_df = df[df["asset_info"] == "IRBASISSWAP_IBOR3M_3M_IBOR12M_12M"]
display_df = filtered_df.copy()
display_df["asset_info"] = "IRBASISSWAP"
print(display_df)

# %%
filtered_df = df[df["asset_info"] == "IRBASISSWAP_RFR_3M_IBOR3M_3M"]
display_df = filtered_df.copy()
display_df["asset_info"] = "IRBASISSWAP"
print(display_df)
