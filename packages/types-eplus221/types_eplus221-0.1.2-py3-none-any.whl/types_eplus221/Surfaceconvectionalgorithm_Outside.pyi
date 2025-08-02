from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceconvectionalgorithm_Outside(EpBunch):
    """Default outside surface heat transfer convection algorithm to be used for all zones"""

    Algorithm: Annotated[Literal['SimpleCombined', 'TARP', 'MoWiTT', 'DOE-2', 'AdaptiveConvectionAlgorithm'], Field(default='DOE-2')]
    """SimpleCombined = Combined radiation and convection coefficient using simple ASHRAE model"""