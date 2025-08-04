from typing import overload, Any, Callable, TypeVar, Union
from typing import Tuple, List, Sequence, MutableSequence

Callback = Union[Callable[..., None], None]
Buffer = TypeVar('Buffer')
Pointer = TypeVar('Pointer')
Template = TypeVar('Template')

import xsigmamodules.Core

class random_enum(int):
    DSFMT:'random_enum'
    MERSENNE_TWISTER:'random_enum'
    PCG64:'random_enum'
    PHILOX:'random_enum'
    SFMT:'random_enum'
    SOBOL:'random_enum'
    SOBOL_BROWNIAN_BRIDGE:'random_enum'
    THREEFRY:'random_enum'
    WELL_19937:'random_enum'
    WELL_44497:'random_enum'
    XOROSHIRO128:'random_enum'
    XORSHIFT1024:'random_enum'
    XOSHIRO512:'random_enum'

class random(object):
    def discard(self, discard_count:int) -> None: ...
    def gaussians(self, output:MutableSequence[float], size:int, discard_count:int): ...
    def generate_upfront_onley(type:'random_enum') -> bool: ...
    def random_generator_factory(main_generator_type:'random_enum', generator_type:'random_enum', seed:int, full_skip:bool, use_shift:bool, number_of_paths_per_batch:int, number_of_factors:int, number_of_dates:int, batch_index:int) -> 'random': ...
    def static_cast(self) -> 'random': ...
    def uniforms(self, output:MutableSequence[float], size:int, discard_count:int) -> None: ...

