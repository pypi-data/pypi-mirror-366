from xsigmamodules.Instrument import instrumentIrSwaption


class instrument:
    def simulated_value(self, discounting, ir_diffusion, strike_ratios):
        pass


class SwaptionInstrument(instrument):
    def __init__(self, marketData, frequence, expiry, maturity):
        self.swaption_ = instrumentIrSwaption(
            True,
            marketData.discountCurve(),
            expiry,
            maturity,
            frequence,
            marketData.dayCountConvention(),
        )

    def simulated_value(self, discounting, ir_diffusion, strike_ratios):
        return self.swaption_.simulated_value(discounting, ir_diffusion, strike_ratios)
