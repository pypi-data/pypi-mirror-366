import xlwings as xw
import numpy as np
from functools import lru_cache, wraps
from xsigmamodules.util.object_converter import xsigmaConverter, xsigma_excel
from xsigmamodules.Math import (
    normalDistribution,
    gaussianQuadrature,
    hartmanWatsonDistribution,
    hartman_watson_distribution_enum,
)
from xsigmamodules.Vectorization import vector, matrix, tensor
from xsigmamodules.Market import irVolatilitySurface, volatilityModel, irVolatility
from xsigmamodules.Util import implied_volatility_enum
from xsigmamodules.util.numpy_support import xsigmaToNumpy, numpyToXsigma
from xsigmamodules.util.misc import xsigmaGetDataRoot


@xsigma_excel(call_in_wizard=False)
@lru_cache(maxsize=512)
@xw.arg("path", doc="path to external data.")
@xw.ret(convert=xsigmaConverter)
def ir_volatility_surface(path):
    vol_obj = irVolatilitySurface.read_from_json(path + "/Data/irVolatility.json")
    return vol_obj.data()


@xsigma_excel(call_in_wizard=False)
@xw.arg("vol_obj", convert=xsigmaConverter)
@xw.arg("expiry", doc="volatility expiry.", numbers=float)
@xw.arg("tenor", doc="volatility tenor.", numbers=float)
@xw.ret(convert=xsigmaConverter)
def ir_volatility_model(vol_obj, expiry, tenor):
    return vol_obj.model(expiry, tenor)


@xsigma_excel(call_in_wizard=False)
@xw.arg("vol_object", convert=xsigmaConverter)
@xw.arg("fwd", doc="option forward.", numbers=float)
@xw.arg("strike", doc="option strike.", numbers=float)
@xw.arg("expiry", doc="option expiry.", numbers=float)
def implied_volatility(vol_object, fwd, strike, expiry):
    return vol_object.implied_volatility(
        fwd, strike, expiry, implied_volatility_enum.NORMAL
    )


@xsigma_excel(call_in_wizard=False)
@xw.arg("x_0", doc="This is start value.", numbers=float)
@xw.arg("x_n", doc="This is end value.", numbers=float)
@xw.arg("t", doc="This is time.", numbers=float)
@xw.arg("n", doc="This is result size.", numbers=int)
@xw.ret(transpose=True)
def distribution(x_0, x_n, t, n):
    """Returns twice the sum of the two arguments"""
    size_roots = 32
    roots = vector["double"](size_roots)
    w1 = vector["double"](size_roots)
    w2 = vector["double"](size_roots)
    gaussianQuadrature.gauss_kronrod(size_roots, roots, w1, w2)
    a = np.linspace(x_0, x_n, n)
    print(a)
    r = numpyToXsigma(a)
    b = np.zeros(n)
    print(b)
    result = numpyToXsigma(b)
    hartmanWatsonDistribution.distribution(
        result, t, r, roots, w1, hartman_watson_distribution_enum.MIXTURE
    )
    print(result)
    print(b)
    return xsigmaToNumpy(result)


@xsigma_excel(call_in_wizard=False)
@xw.arg("x", doc="value.", numbers=float)
def cdfnorm(x):
    """Returns the cdfnorm value"""
    return normalDistribution.cdfnorm(x)


@xsigma_excel(call_in_wizard=False)
@xw.arg("x", doc="value.", numbers=float)
def cdfnorminv(x):
    """Returns the cdfnorm value"""
    return normalDistribution.cdfnorminv(x)


@xsigma_excel(call_in_wizard=False)
@xw.arg("x", doc="value.", numbers=float)
def cdfnorminv_fast(x):
    """Returns the cdfnorm value"""
    return normalDistribution.cdfnorminv_fast(x)
