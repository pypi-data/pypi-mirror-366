from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Groundtemperature_Undisturbed_Kusudaachenbach(EpBunch):
    """Undisturbed ground temperature object using the"""

    Name: Annotated[str, Field(default=...)]

    Soil_Thermal_Conductivity: Annotated[float, Field(default=..., gt=0.0)]

    Soil_Density: Annotated[float, Field(default=..., gt=0.0)]

    Soil_Specific_Heat: Annotated[float, Field(default=..., gt=0.0)]

    Average_Soil_Surface_Temperature: Annotated[float, Field()]
    """Annual average surface temperature"""

    Average_Amplitude_Of_Surface_Temperature: Annotated[float, Field(ge=0)]
    """Annual average surface temperature variation from average."""

    Phase_Shift_Of_Minimum_Surface_Temperature: Annotated[float, Field(ge=0, lt=365)]
    """The phase shift of minimum surface temperature, or the day"""