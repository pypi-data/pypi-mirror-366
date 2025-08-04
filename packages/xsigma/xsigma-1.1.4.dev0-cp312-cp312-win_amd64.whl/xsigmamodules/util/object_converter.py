from xlwings.conversion import Converter
import datetime
import xlwings as xw
from functools import lru_cache, wraps


def _list_to_tuple(arg):
    if isinstance(arg, list):
        my_tuple = tuple([_list_to_tuple(e) for e in arg])
        return my_tuple
    return arg


def xsigma_excel(call_in_wizard=True, **kwargs):
    def xsigma_excel_internal(func):
        @wraps(func)
        def excel_wraper(*args, **kwargs):
            my_args = []
            for i, arg in enumerate(args):
                my_args.append(_list_to_tuple(arg))
            my_args = tuple(my_args)
            my_kwargs = dict()
            for key, value in kwargs.items():
                my_kwargs[key] = _list_to_tuple(value)
            # init_xsigma()
            return func(*my_args, **my_kwargs)

        kwargs["call_in_wizard"] = call_in_wizard
        return xw.func(excel_wraper, **kwargs)

    return xsigma_excel_internal


object_cache = {}
cache_counters = {}
cell_id_to_obj_id = {}


class xsigmaConverter(Converter):
    """Convert an object to a reference. The reference can include the 'caller' address to ensure
    uniqueness (not needed if singleton - caller=False).

    The object are stored in a global dict by their key and looked up when reading.

    When used on a return value, the converter will transform the value into a reference.
    If the value is a dict, it will return a reference for each item in the dict.

    When used in an input, the converter will return the value that was stored in a reference.
    """

    @staticmethod
    def get_cell_id():
        caller = xw.apps.active.api.Caller
        return "{caller.Worksheet.Name}!{caller.Address}"

    @staticmethod
    def read_value(key, options):
        if not key:
            return
        if key in object_cache:
            return object_cache.get(key)
        else:
            raise ValueError(f"No data available for {key}")

    @staticmethod
    def add_new_cache_handle(options, name):
        global cache_counters
        obj_enum = options.get("objectType", False)
        if not obj_enum:
            obj_enum = name
        handleName = options.get("handleName", False)
        if not handleName:
            handleName = ""
        cache_counter = cache_counters.get(obj_enum, 0)
        cache_counters[obj_enum] = cache_counter + 1
        name = "{}{}@{}".format(obj_enum, handleName, cache_counter)
        return name

    @staticmethod
    def write_value(obj, options):
        global object_cache
        cache_name = xsigmaConverter.add_new_cache_handle(options, type(obj).__name__)
        object_cache[cache_name] = obj
        return cache_name
