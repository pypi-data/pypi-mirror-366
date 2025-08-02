from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Weatherstation(EpBunch):
    """This object should only be used for non-standard weather data. Standard weather data"""

    Wind_Sensor_Height_Above_Ground: Annotated[float, Field(gt=0.0, default=10.0)]

    Wind_Speed_Profile_Exponent: Annotated[float, Field(ge=0.0, default=0.14)]

    Wind_Speed_Profile_Boundary_Layer_Thickness: Annotated[float, Field(ge=0.0, default=270.0)]

    Air_Temperature_Sensor_Height_Above_Ground: Annotated[float, Field(ge=0.0, default=1.5)]