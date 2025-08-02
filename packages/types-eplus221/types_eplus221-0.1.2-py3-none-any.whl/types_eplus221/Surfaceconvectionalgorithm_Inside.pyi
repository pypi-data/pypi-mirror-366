from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceconvectionalgorithm_Inside(EpBunch):
    """Default indoor surface heat transfer convection algorithm to be used for all zones"""

    Algorithm: Annotated[Literal['Simple', 'TARP', 'CeilingDiffuser', 'AdaptiveConvectionAlgorithm'], Field(default='TARP')]
    """Simple = constant value natural convection (ASHRAE)"""