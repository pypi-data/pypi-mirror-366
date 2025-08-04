import xlwings as xw
import numpy as np
from functools import lru_cache, wraps
from xsigmamodules.util.object_converter import xsigmaConverter, xsigma_excel
from xsigmamodules.Util import (
    zabrAnalytics,
    implied_volatility_enum,
    sabrAnalytics,
    zabrClassicalAnalytics,
    blackScholes,
    bachelier,
)
from xsigmamodules.Vectorization import vector, matrix, tensor
from xsigmamodules.util.numpy_support import xsigmaToNumpy, numpyToXsigma


@xsigma_excel(call_in_wizard=False)
@xw.arg("forward", doc="option forward.", numbers=float)
@xw.arg("strike", doc="option strike.", numbers=float)
@xw.arg("expiry", doc="option expiry.", numbers=float)
@xw.arg("alpha", doc="SABR parameter alpha.", numbers=float)
@xw.arg("beta", doc="SABR parameter beta.", numbers=float)
@xw.arg("nu", doc="SABR parameter nu.", numbers=float)
@xw.arg("rho", doc="SABR parameter rho.", numbers=float)
@xw.arg("shift", doc="SABR parameter shift.", numbers=float)
@xw.arg("dampening", doc="SABR parameter dampening.")
def SABR_implied_volatility(
    forward, strike, expiry, alpha, beta, nu, rho, shift, dampening=False
):
    p = sabrAnalytics.price(
        forward, strike, expiry, 1.0, 1.0, alpha, beta, nu, rho, shift, dampening
    )
    return blackScholes.implied_volatility(forward, strike, expiry, p, 1.0, 1.0)


@xsigma_excel(call_in_wizard=False)
@xw.arg("forward", doc="option forward.", numbers=float)
@xw.arg("expiry", doc="option expiry.", numbers=float)
@xw.arg("alpha", doc="ZABR parameter alpha.", numbers=float)
@xw.arg("beta", doc="ZABR parameter beta.", numbers=float)
@xw.arg("nu", doc="ZABR parameter nu.", numbers=float)
@xw.arg("rho", doc="ZABR parameter rho.", numbers=float)
@xw.arg("shift", doc="SABR parameter shift.", numbers=float)
@xw.arg("gamma", doc="ZABR parameter gamma.", numbers=float)
@xw.ret(convert=xsigmaConverter)
def ZABR_analytics(forward, expiry, alpha, beta, nu, rho, shift, gamma):
    return zabrClassicalAnalytics(beta, shift, expiry, forward, alpha, nu, rho, gamma)


@xsigma_excel(call_in_wizard=False)
@xw.arg("obj", convert=xsigmaConverter)
@xw.arg("strikes", doc="option strikes.")
@xw.arg("condition", doc="bounry condition.")
@xw.ret(transpose=True)
def ZABR_implied_volatility(obj, strikes, condition):
    output = np.zeros(len(strikes))
    output_ = numpyToXsigma(output)
    obj.optoin_prices(output_, strikes, condition)
    obj.implied_volatility(output_, strikes)
    return output
