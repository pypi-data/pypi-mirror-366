from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zoneairheatbalancealgorithm(EpBunch):
    """Determines which algorithm will be used to solve the zone air heat balance."""

    Algorithm: Annotated[Literal['ThirdOrderBackwardDifference', 'AnalyticalSolution', 'EulerMethod'], Field(default='ThirdOrderBackwardDifference')]