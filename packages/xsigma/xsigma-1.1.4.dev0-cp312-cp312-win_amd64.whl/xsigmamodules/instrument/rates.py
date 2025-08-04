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
    curveCalibrationDatesConfigId,
    curveCalibrationDatesConfig,
    curveCalibrationInstrumentConfig,
    calibration_grid_enum,
)
from xsigmamodules.Math import interpolation_enum
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
    calendar,
    dayCountConvention,
    day_count_convention_enum,
    option_output_enum,
    yearMonthDay,
    key,
    business_day_convention_enum,
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


def IRSwap(
    discount,
    index,
    effective_date,
    maturity,
    holiday_list,
    fixed_frequency,
    forecast_frequency,
    bdc,
    fixed_basis,
    forecast_basis,
):
    fixed_params_schedule = (
        scheduleParametersBuilder()
        .with_effective_date(effective_date)
        .with_maturity_date(maturity)
        .with_frequency(fixed_frequency)
        .with_business_day_convention(bdc)
        .with_holiday_list(holiday_list)
        .with_day_count_basis(fixed_basis)
        .build()
    )

    float_params_schedule = (
        scheduleParametersBuilder()
        .with_effective_date(effective_date)
        .with_maturity_date(maturity)
        .with_frequency(forecast_frequency)
        .with_business_day_convention(bdc)
        .with_holiday_list(holiday_list)
        .with_day_count_basis(forecast_basis)
        .build()
    )

    return irSwap(
        discount,
        index,
        effective_date,
        maturity,
        fixedLeg(fixed_params_schedule),
        floatLeg(float_params_schedule),
    )

def IRSwap(discount, index, effective_date, maturity, holiday_list, swap_config, float_frequency=None, fixed_frequency=None):
   # Use provided frequencies if given, otherwise fall back to swap_config
   actual_fixed_frequency = fixed_frequency if fixed_frequency is not None else swap_config.fixed_frequency()
   actual_float_frequency = float_frequency if float_frequency is not None else swap_config.forecast_frequency()
   
   fixed_params_schedule = (
       scheduleParametersBuilder()
       .with_effective_date(effective_date)
       .with_maturity_date(maturity)
       .with_holiday_list(holiday_list)
       .with_frequency(actual_fixed_frequency)
       .with_business_day_convention(swap_config.business_day_convention())
       .with_day_count_basis(swap_config.fixed_basis())
       .build()
   )
   float_params_schedule = (
       scheduleParametersBuilder()
       .with_effective_date(effective_date)
       .with_maturity_date(maturity)
       .with_holiday_list(holiday_list)
       .with_frequency(actual_float_frequency)
       .with_business_day_convention(swap_config.business_day_convention())
       .with_day_count_basis(swap_config.forecast_basis())
       .build()
   )
   return irSwap(
       discount,
       index,
       effective_date,
       maturity,
       fixedLeg(fixed_params_schedule),
       floatLeg(float_params_schedule),
   )


def IRTermDeposit(discount, index, effective_date, maturity, holiday_list, swap_config):
    fixed_params_schedule = (
        scheduleParametersBuilder()
        .with_effective_date(effective_date)
        .with_maturity_date(maturity)
        .with_holiday_list(holiday_list)
        .with_frequency(swap_config.fixed_frequency())
        .with_business_day_convention(swap_config.business_day_convention())
        .with_day_count_basis(swap_config.fixed_basis())
        .build()
    )

    float_params_schedule = (
        scheduleParametersBuilder()
        .with_effective_date(effective_date)
        .with_maturity_date(maturity)
        .with_holiday_list(holiday_list)
        .with_frequency(swap_config.forecast_frequency())
        .with_business_day_convention(swap_config.business_day_convention())
        .with_day_count_basis(swap_config.forecast_basis())
        .build()
    )

    return irTermDeposit(
        discount,
        index,
        effective_date,
        maturity,
        1,
        fixedLeg(fixed_params_schedule),
        floatLeg(float_params_schedule),
    )


def IRBasisSwap(
    discount,
    index,
    index_base,
    effective_date,
    maturity,
    holiday_list,
    freq,
    freq_base,
    swap_config,
):
    params_schedule = (
        scheduleParametersBuilder()
        .with_effective_date(effective_date)
        .with_maturity_date(maturity)
        .with_frequency(freq)
        .with_business_day_convention(swap_config.business_day_convention())
        .with_holiday_list(holiday_list)
        .with_day_count_basis(swap_config.forecast_basis())
        .build()
    )

    params_schedule_base = (
        scheduleParametersBuilder()
        .with_effective_date(effective_date)
        .with_maturity_date(maturity)
        .with_frequency(freq_base)
        .with_business_day_convention(swap_config.business_day_convention())
        .with_holiday_list(holiday_list)
        .with_day_count_basis(swap_config.forecast_basis())
        .build()
    )
    fixed_leg = fixedLeg(params_schedule)
    float_leg = floatLeg(params_schedule)
    base_float_leg = floatLeg(params_schedule_base)
    return irBasisSwap(
        discount,
        index,
        index_base,
        effective_date,
        maturity,
        fixed_leg,
        float_leg,
        base_float_leg,
        1,
    )
