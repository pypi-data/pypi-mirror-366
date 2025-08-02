from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Groundtemperature_Undisturbed_Xing(EpBunch):
    """Undisturbed ground temperature object using the"""

    Name: Annotated[str, Field(default=...)]

    Soil_Thermal_Conductivity: Annotated[float, Field(default=..., gt=0.0)]

    Soil_Density: Annotated[float, Field(default=..., gt=0.0)]

    Soil_Specific_Heat: Annotated[float, Field(default=..., gt=0.0)]

    Average_Soil_Surface_Tempeature: Annotated[float, Field(default=...)]

    Soil_Surface_Temperature_Amplitude_1: Annotated[float, Field(default=...)]

    Soil_Surface_Temperature_Amplitude_2: Annotated[float, Field(default=...)]

    Phase_Shift_of_Temperature_Amplitude_1: Annotated[float, Field(default=..., lt=365)]

    Phase_Shift_of_Temperature_Amplitude_2: Annotated[float, Field(default=..., lt=365)]