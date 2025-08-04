import json
import os
from pathlib import Path

import numpy as np
from xsigmamodules.Util import datetimeHelper
from xsigmamodules.util.numpy_support import xsigmaToNumpy, numpyToXsigma
from matplotlib import pyplot as plt
from xsigmamodules.Market import currencyMappingConfig, currencyMappingConfigBuilder
from xsigmamodules.util.misc import xsigmaGetDataRoot, xsigmaGetTempDir
from xsigmamodules.Analytics import (
    correlationManager,
    correlationManagerBuilder,
    simulatedMarketDataIrIdBuilder,
    simulatedMarketDataFxIdBuilder,
    simulatedMarketDataCreditIdBuilder,
    simulatedMarketDataEquityIdBuilder,
)


def CreateCurrencyMappingConfig(path, value_filter,output_file):
    """
    Load mapping from JSON and build config, filtering by value substring if provided.

    Args:
        path: Path to the JSON file.
        value_filter: Substring to filter values (if not None).

    Returns:
        Built currencyMappingConfig object.

    Raises:
        ValueError: If no values match the filter.
    """
    with open(path, "r") as f:
        mapping = json.load(f)
    if value_filter:
        filtered = [(k, v) for k, v in mapping.items() if value_filter not in v]
        if filtered:
            keys, values = zip(*filtered)
            keys, values = list(keys), list(values)
        else:
            raise ValueError(f"No mapping values contain '{value_filter}'")
    else:
        keys, values = list(mapping.keys()), list(mapping.values())
    config = currencyMappingConfigBuilder().with_mapping(keys, values).build()
    currencyMappingConfig.write_to_json(output_file, config)
    return config


def convert_dates_to_fraction(valuation_date, dates, convention):
    """
    Convert a list of dates to fractional years based on a given day count convention.

    Parameters:
    - valuation_date: The base date for the conversion.
    - dates: List of dates to be converted.
    - convention: The day count convention to be used for the conversion.

    Returns:
    - np_array: Numpy array of fractional years.
    """
    np_array = np.zeros(len(dates))
    for i in range(len(dates)):
        np_array[i] = convention.fraction(valuation_date, dates[i])
    return np_array


def plot_params(
    x, np_array1, np_array2, title, xlabel, ylabel, legend, legend_2, num_factor
):
    """
    Plot parameters with the given data and labels.

    Parameters:
    - x: X-axis data.
    - np_array1: First set of Y-axis data arrays.
    - np_array2: Second set of Y-axis data arrays.
    - title: Title of the plot.
    - xlabel: Label for the X-axis.
    - ylabel: Label for the Y-axis.
    - legend: List of legends for the first set of data.
    - legend_2: List of legends for the second set of data.
    - num_factor: Number of factors (subplots).
    """
    for i in range(num_factor):
        if np_array1.size == 0:
            print("No data available for np_array1")
        else:
            plt.plot(x, np_array1[i], ".-", label=legend[i])
        if np_array2.size == 0:
            print("No data available for np_array2")
        else:
            plt.plot(x, np_array2[i], ".-", label=legend_2[i], dashes=[6, 2])
        plt.legend(loc="lower right")
        plt.title(title)
        plt.grid(True, which="both")
        plt.axhline(y=0, color="k")
        plt.axvline(x=0, color="k")
        plt.xlim(np.min(x), np.max(x))
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        plt.show()
    return 0


def markov_test(a, b):
    """
    Perform Markov test on the given inputs.

    Parameters:
    - a: First input array.
    - b: Second input array.

    Returns:
    - Average of the product of the inputs, with b exponentiated.
    """
    z = xsigmaToNumpy(a) * np.exp(xsigmaToNumpy(b))
    return np.average(z)


def mm_test(a):
    """
    Calculate the average of the given input array.

    Parameters:
    - a: Input array.

    Returns:
    - Average of the input array.
    """
    return np.average(xsigmaToNumpy(a))


def average(a):
    """
    Calculate the average of the given input array.

    Parameters:
    - a: Input array.

    Returns:
    - Average of the input array.
    """
    return np.average(xsigmaToNumpy(a))


def average_product(a, b):
    """
    Calculate the average of the product of two input arrays.

    Parameters:
    - a: First input array.
    - b: Second input array.

    Returns:
    - Average of the product of the input arrays.
    """
    return np.average(xsigmaToNumpy(a) * xsigmaToNumpy(b))


def simulation_dates(start_date, tenor, size):
    """
    Generate a list of simulation dates starting from a given date with a specific tenor.

    Parameters:
    - start_date: The starting date.
    - tenor: The tenor to add for each subsequent date.
    - size: The number of dates to generate.

    Returns:
    - sim_dates: List of generated simulation dates.
    """
    sim_dates = [start_date]
    date_0 = start_date
    for _ in range(size):
        date_0 = datetimeHelper.add_tenor(date_0, tenor)
        sim_dates.append(date_0)
    return sim_dates


def simulation_dates_from_tenors(start_date, tenors):
    """
    Generate a list of simulation dates starting from a given date based on a list of tenors.

    Parameters:
    - start_date: The starting date.
    - tenors: List of tenors to add for each subsequent date.

    Returns:
    - sim_dates: List of generated simulation dates.
    """
    sim_dates = [start_date]
    for tenor in tenors:
        date_0 = datetimeHelper.add_tenor(start_date, tenor)
        sim_dates.append(date_0)
    return sim_dates


def simulated_id_builder(type, **kwargs):
    """
    Unified builder function for simulated market data IDs with camelCase naming.

    Args:
        type: Type of simulated market data ID ("IR", "FX", "CREDIT", "EQUITY")
        **kwargs: Parameters specific to each type

    Returns:
        Built simulated market data ID

    Examples:
        # IR
        ir_id = simulated_id_builder(type="IR", currency="USD", discount_definition="SOFR")

        # FX
        fx_id = simulated_id_builder(type="FX", domestic_currency="USD", foreign_currency="EUR",
                                   domestic_discount_definition="SOFR", foreign_discount_definition="EURIBOR")

        # Credit
        credit_id = simulated_id_builder(type="CREDIT", name="AAPL", discount_definition="SOFR",
                                       currency="USD", seniority="SNR", restructuring="CR", isda="2014")

        # Equity
        equity_id = simulated_id_builder(type="EQUITY", equity_name="MSFT", currency="USD",
                                       discount_definition="SOFR")
    """
    type = type.upper()

    if type == "IR":
        return (
            simulatedMarketDataIrIdBuilder()
            .with_currency(kwargs["currency"])
            .with_discount_definition(kwargs["discount_definition"])
            .build()
        )

    elif type == "FX":
        return (
            simulatedMarketDataFxIdBuilder()
            .with_domestic_currency(kwargs["domestic_currency"])
            .with_foreign_currency(kwargs["foreign_currency"])
            .with_domestic_discount_definition(kwargs["domestic_discount_definition"])
            .with_foreign_discount_definition(kwargs["foreign_discount_definition"])
            .build()
        )

    elif type == "CREDIT":
        return (
            simulatedMarketDataCreditIdBuilder()
            .with_name(kwargs["name"])
            .with_discount_definition(kwargs["discount_definition"])
            .with_currency(kwargs["currency"])
            .with_seniority(kwargs["seniority"])
            .with_restructuring(kwargs["restructuring"])
            .with_isda(kwargs["isda"])
            .build()
        )

    elif type == "EQUITY":
        return (
            simulatedMarketDataEquityIdBuilder()
            .with_equity_name(kwargs["equity_name"])
            .with_currency(kwargs["currency"])
            .with_discount_definition(kwargs["discount_definition"])
            .build()
        )

    else:
        raise ValueError(
            f"Unknown simulated market data type: {type}. "
            f"Supported types: IR, FX, CREDIT, EQUITY"
        )


def CreatecorrelationManager(valuation_date, ids, factors, matrix, json_path):
    ids_ = []
    for v in ids:
        if v[0] == "IR":
            ids_.append(
                simulated_id_builder(
                    type="IR", currency=v[1], discount_definition=v[2]
                )
            )
        elif v[0] == "FX":
            ids_.append(
                simulated_id_builder(
                    type="FX",
                    domestic_currency=v[1],
                    foreign_currency=v[2],
                    domestic_discount_definition=v[3],
                    foreign_discount_definition=v[4],
                )
            )
        elif v[0] == "CREDIT":
            ids_.append(
                simulated_id_builder(
                    type="CREDIT",
                    name=v[1],
                    currency=v[2],
                    discount_definition=v[3],
                    seniority=v[4],
                    restructuring=v[5],
                    isda=v[6],
                )
            )
        elif v[0] == "EQUITY":
            ids_.append(
                simulated_id_builder(
                    type="EQUITY",
                    equity_name=v[1],
                    currency=v[2],
                    discount_definition=v[3],
                )
            )

    correlation_matrix = numpyToXsigma(np.array(matrix))
    correlation_manager = (
        correlationManagerBuilder()
        .with_valuation_date(valuation_date)
        .with_ids(ids_)
        .with_factors(factors)
        .with_correlation(correlation_matrix)
        .build()
    )
    correlationManager.write_to_json(json_path, correlation_manager)
