from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Sizing_Parameters(EpBunch):
    """Specifies global heating and cooling sizing factors/ratios."""

    Heating_Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]

    Cooling_Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]

    Timesteps_in_Averaging_Window: Annotated[int, Field(ge=1)]
    """blank => set the timesteps in averaging window to"""