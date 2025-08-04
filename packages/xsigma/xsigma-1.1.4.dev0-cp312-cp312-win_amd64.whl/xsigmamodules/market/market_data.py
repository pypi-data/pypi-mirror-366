from xsigmamodules.Analytics import (
    calibrationIrTargetsConfiguration,
    calibrationHjmSettings,
    correlationManager,
)
from xsigmamodules.util.numpy_support import xsigmaToNumpy, numpyToXsigma
from xsigmamodules.Market import discountCurveInterpolated, irVolatilitySabr
from xsigmamodules.Util import dayCountConvention
import os
from xsigmamodules.util.misc import xsigmaGetDataRoot
from xsigmamodules.market.object_factory import ObjectFactory
import logging

from itertools import chain

# Initialize the object factory with the mapping rules file
object_factory = ObjectFactory(
    os.path.join(xsigmaGetDataRoot(), "Data", "object_mapping_rules.xml"),
    xsigmaGetDataRoot(),
)


class market_data:
    def __init__(self, path):
        self.__target_config_ = calibrationIrTargetsConfiguration.read_from_json(
            path + "/Data/calibrationIrTargetsConfiguration.json"
        )
        self.__calibration_settings_ = calibrationHjmSettings.read_from_json(
            path + "/Data/calibrationIrHjmSettings3F.json"
        )
        self.__discount_curve_ = discountCurveInterpolated.read_from_json(
            path + "/Data/discountCurve.json"
        )
        self.__correlation_mgr_ = correlationManager.read_from_json(
            path + "/Data/correlationManager.json"
        )
        self.__ir_volatility_surface_ = irVolatilitySabr.read_from_json(
            path + "/Data/irVolatility.json"
        )
        self.__convention_ = (
            self.__target_config_.convention()
        )  # dayCountConvention.read_from_json(
        # path + "/Data/staticData/day_count_convention_360.json"
        # )
        self.__valuation_date_ = self.__discount_curve_.valuation_date()

    def valuation_date(self):
        return self.__valuation_date_

    def discountCurve(self):
        return self.__discount_curve_

    def irVolatilitySurface(self):
        return self.__ir_volatility_surface_

    def dayCountConvention(self):
        return self.__convention_

    def calibrationIrTargetsConfiguration(self):
        return self.__target_config_

    def calibrationIrHjmSettings(self):
        return self.__calibration_settings_

    def correlationManager(self):
        return self.__correlation_mgr_

    def correlation(self, diffusion_ids):
        correlation = self.__correlation_mgr_.pair_correlation_matrix(
            diffusion_ids, diffusion_ids
        )
        return correlation


def update_one_id(market, any_id, processed_ids=None):
    """Process a single ID and its dependencies."""
    try:
        if not any_id or market.contains(any_id):
            # print("not any_id or market.contains(any_id): " + str(any_id))
            return
        processed_ids = processed_ids or []
        if any_id in processed_ids:
            # print("any_id in processed_ids: " + str(any_id))
            return
        processed_ids.append(any_id)

        if object_factory.contains(any_id):
            # print("update_market_container: " + str(any_id))
            object_factory.update_market_container(market, [any_id])
            return

        while True:
            result = market.discover_recursive(any_id)

            if result.has_missing_dependencies():
                tmp = result.get_missing_dependency()

                if object_factory.contains(tmp):
                    # print("update_market_container: " + str(tmp))
                    object_factory.update_market_container(market, [tmp])
                else:
                    if not tmp.has_generic_builder():
                        logging.error(
                            f"Unable to discover missing dependency: {str(tmp)} for id: {str(any_id)}"
                        )
                        return
                    obj = market.discover_recursive(tmp)
                    if obj.has_object():
                        market.insert(obj.id(), obj.object())
            else:
                break
    except Exception as e:
        logging.error(f"Error processing ID {any_id}: {str(e)}")
        raise


def discover(market, ids):
    """Discover multiple IDs and their dependencies."""
    processed_ids = []
    for any_id in ids:
        update_one_id(market, any_id, processed_ids)
