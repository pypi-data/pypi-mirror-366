from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceproperty_Solarincidentinside(EpBunch):
    """Used to provide incident solar radiation on the inside of the surface. Reference surface-construction pair"""

    Name: Annotated[str, Field(default=...)]

    Surface_Name: Annotated[str, Field(default=...)]

    Construction_Name: Annotated[str, Field(default=...)]

    Inside_Surface_Incident_Sun_Solar_Radiation_Schedule_Name: Annotated[str, Field(default=...)]
    """Values in schedule are expected to be in W/m2"""