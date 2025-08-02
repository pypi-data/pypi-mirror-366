from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Daylightingdevice_Tubular(EpBunch):
    """Defines a tubular daylighting device (TDD) consisting of three components:"""

    Name: Annotated[str, Field(default=...)]

    Dome_Name: Annotated[str, Field(default=...)]
    """This must refer to a subsurface object of type TubularDaylightDome"""

    Diffuser_Name: Annotated[str, Field(default=...)]
    """This must refer to a subsurface object of type TubularDaylightDiffuser"""

    Construction_Name: Annotated[str, Field(default=...)]

    Diameter: Annotated[float, Field(default=..., gt=0)]

    Total_Length: Annotated[float, Field(default=..., gt=0)]
    """The exterior exposed length is the difference between total and sum of zone lengths"""

    Effective_Thermal_Resistance: Annotated[float, Field(gt=0, default=0.28)]
    """R value between TubularDaylightDome and TubularDaylightDiffuser"""

    Transition_Zone_1_Name: Annotated[str, Field()]

    Transition_Zone_1_Length: Annotated[float, Field(ge=0.0)]

    Transition_Zone_2_Name: Annotated[str, Field()]

    Transition_Zone_2_Length: Annotated[float, Field(ge=0.0)]

    Transition_Zone_3_Name: Annotated[str, Field()]

    Transition_Zone_3_Length: Annotated[float, Field(ge=0.0)]

    Transition_Zone_4_Name: Annotated[str, Field()]

    Transition_Zone_4_Length: Annotated[float, Field(ge=0.0)]