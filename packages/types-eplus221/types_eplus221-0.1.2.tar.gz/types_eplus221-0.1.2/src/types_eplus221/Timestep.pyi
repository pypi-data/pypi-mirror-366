from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Timestep(EpBunch):
    """Specifies the "basic" timestep for the simulation. The"""

    Number_of_Timesteps_per_Hour: Annotated[int, Field(ge=1, le=60, default=6)]
    """Number in hour: normal validity 4 to 60: 6 suggested"""