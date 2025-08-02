from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Pipingsystem_Underground_Pipesegment(EpBunch):
    """The pipe segment to be used in an underground piping system"""

    Name: Annotated[str, Field(default=...)]

    X_Position: Annotated[float, Field(default=..., gt=0)]
    """This segment will be centered at this distance from the x=0"""

    Y_Position: Annotated[float, Field(default=..., gt=0)]
    """This segment will be centered at this distance away from the"""

    Flow_Direction: Annotated[Literal['IncreasingZ', 'DecreasingZ'], Field(default=...)]
    """This segment will be simulated such that the flow is in the"""