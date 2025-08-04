from xsigmamodules.market import market_data
from xsigmamodules.common import instrument
from xsigmamodules.common import helper
from xsigmamodules.Random import random_enum
from xsigmamodules.Util import datetimeHelper, bachelier, implied_volatility_enum
from xsigmamodules.Vectorization import vector, tensor, matrix
from xsigmamodules.Analytics import simulationManager
from xsigmamodules.Market import (
    anyId,
    anyContainer,
    anyObject,
)
from xsigmamodules.util.numpy_support import xsigmaToNumpy, numpyToXsigma

try:
    import numpy as np
except ImportError:
    print("This test requires numpy!")

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("This test requires matplotlib!")


class SimulationIRResults:
    def __init__(self):
        self.markov_result_mm = []
        self.markov_result_df = []
        self.model_swaption_implied = {}
        self.market_swaption_implied = {}

    def plot_charts(self, market_data, simulation_dates):
        x = list(self.model_swaption_implied.keys())
        model_vols = np.array(list(self.model_swaption_implied.values())).T * 10000
        market_vols = np.array(list(self.market_swaption_implied.values())).T * 10000

        expiry_fraction = helper.convert_dates_to_fraction(
            market_data.valuation_date(), x, market_data.dayCountConvention()
        )
        simulation_dates_fraction = helper.convert_dates_to_fraction(
            market_data.valuation_date(),
            simulation_dates,
            market_data.dayCountConvention(),
        )

        maturities = []
        for i in range(model_vols.size):
            maturities.append("option_" + str(i))

        legend = ["model_" + m for m in maturities]
        legend_2 = ["market_" + m for m in maturities]

        # print(legend_2)
        print(market_vols)
        print(model_vols)
        helper.plot_params(
            expiry_fraction,
            model_vols,
            market_vols,
            "Simulated Implied Volatility",
            "Expiry (Years)",
            "Normal Implied Volatility (bps)",
            legend,
            legend_2,
            len(model_vols),
        )

        error = np.asarray(
            [model_vols[i] - market_vols[i] for i in range(len(model_vols))]
        )
        print(error)
        helper.plot_params(
            expiry_fraction,
            error,
            np.array([]),
            "Error in Implied Volatility",
            "Expiry (Years)",
            "Error (bps)",
            legend,
            legend_2,
            len(model_vols),
        )

        mm = np.reshape(self.markov_result_mm, (1, len(self.markov_result_mm)))
        df = np.reshape(self.markov_result_df, (1, len(self.markov_result_df)))
        legend = ["MM Error"]
        legend_2 = ["DF Error"]
        helper.plot_params(
            simulation_dates_fraction,
            mm,
            df,
            "Markov Test",
            "Expiry (Years)",
            "Error (bps)",
            legend,
            legend_2,
            1,
        )


class Simulation:
    def __init__(
        self,
        market_data,
        num_of_paths,
        frequency,
        expiries,
        cms_tenors,
        coterminal_tenor,
        maturity,
        simulation_dates,
    ):
        self.market_data = market_data
        self.num_of_paths = num_of_paths
        self.maturity = maturity
        self.results = SimulationIRResults()
        self.swaptions = self._create_swaption_grid(
            simulation_dates, frequency, expiries, cms_tenors, coterminal_tenor
        )

    def _create_swaption_grid(
        self, simulation_dates, frequency, expiries, cms_tenors, coterminal_tenor
    ):
        swaptions_dict = {}
        valuation_date = simulation_dates[0]

        for expiry in expiries:
            expiry_date = datetimeHelper.add_tenor(valuation_date, expiry)
            swaptions_list = []

            maturity_date = datetimeHelper.add_tenor(expiry_date, frequency)
            swaptions_list.append(
                instrument.SwaptionInstrument(
                    self.market_data, frequency, expiry_date, maturity_date
                )
            )

            coterminal_maturity = datetimeHelper.add_tenor(
                valuation_date, coterminal_tenor
            )
            swaptions_list.append(
                instrument.SwaptionInstrument(
                    self.market_data, frequency, expiry_date, coterminal_maturity
                )
            )

            for tenor in cms_tenors:
                cms_maturity = datetimeHelper.add_tenor(expiry_date, tenor)
                swaptions_list.append(
                    instrument.SwaptionInstrument(
                        self.market_data, frequency, expiry_date, cms_maturity
                    )
                )

            swaptions_dict[expiry_date] = swaptions_list

        return swaptions_dict

    def plot(self, simulation_dates):
        self.results.plot_charts(self.market_data, simulation_dates)

    def process(self, t, curve_diffusion, simulation_date):
        if t == 0:
            self.results.markov_result_df.append(0)
            self.results.markov_result_mm.append(0)
            return

        mm = vector["double"](self.num_of_paths)
        df = vector["double"](self.num_of_paths)
        output = tensor["double"]([1, self.num_of_paths])

        curve_diffusion.discounting(mm, simulation_date)
        curve_diffusion.log_df(df, simulation_date, self.maturity)

        np_mm = xsigmaToNumpy(mm)
        np_df = np.exp(xsigmaToNumpy(df))

        avg_mm_df = np.average(np_mm * np_df)
        discount_curve = self.market_data.discountCurve()
        val_date = self.market_data.valuation_date()

        self.results.markov_result_df.append(
            (avg_mm_df - discount_curve.df(val_date, self.maturity)) * 10000
        )

        self.results.markov_result_mm.append(
            (np.average(np_mm) - discount_curve.df(val_date, simulation_date)) * 10000
        )

        if simulation_date in self.swaptions:
            swaption_list = self.swaptions[simulation_date]
            model_vols = []
            market_vols = []

            for s in swaption_list:
                swaption = s.swaption_
                strike = swaption.swap_rate()
                swaption.price(simulation_date, [curve_diffusion], output)
                vol = np.average(
                    xsigmaToNumpy(mm) * xsigmaToNumpy(output.get_matrix([]))
                )
                vol = bachelier.implied_volatility(
                    swaption.swap_rate(),
                    strike,
                    swaption.expiry_double(),
                    vol,
                    swaption.annuity(),
                    swaption.is_call(),
                )
                model_vols.append(vol)
                market_vol = (
                    self.market_data.irVolatilitySurface()
                    .model(swaption.swap().effective_date(), swaption.swap().maturity())
                    .implied_volatility(
                        swaption.swap_rate(),
                        strike,
                        swaption.expiry_double(),
                        implied_volatility_enum.NORMAL,
                    )
                )
                market_vols.append(market_vol)

            self.results.model_swaption_implied[simulation_date] = model_vols
            self.results.market_swaption_implied[simulation_date] = market_vols

    def run_simulation(self, simulated_ids, market, simulation_dates):
        simulation_mgr = simulationManager(simulated_ids, market, simulation_dates)

        curve_diffusion = simulation_mgr.discount_curve(simulated_ids[0])

        self.process(0, curve_diffusion, simulation_dates[0])
        simulation_mgr.states_initialize()

        for t in range(1, len(simulation_dates)):
            simulation_mgr.propagate(t)
            self.process(t, curve_diffusion, simulation_dates[t])
