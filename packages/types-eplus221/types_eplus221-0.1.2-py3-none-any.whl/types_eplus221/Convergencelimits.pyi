from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Convergencelimits(EpBunch):
    """Specifies limits on HVAC system simulation timesteps and iterations."""

    Minimum_System_Timestep: Annotated[int, Field(ge=0, le=60)]
    """0 sets the minimum to the zone timestep (ref: Timestep)"""

    Maximum_HVAC_Iterations: Annotated[int, Field(ge=1, default=20)]

    Minimum_Plant_Iterations: Annotated[int, Field(ge=1, default=2)]
    """Controls the minimum number of plant system solver iterations within a single HVAC iteration"""

    Maximum_Plant_Iterations: Annotated[int, Field(ge=2, default=8)]
    """Controls the maximum number of plant system solver iterations within a single HVAC iteration"""