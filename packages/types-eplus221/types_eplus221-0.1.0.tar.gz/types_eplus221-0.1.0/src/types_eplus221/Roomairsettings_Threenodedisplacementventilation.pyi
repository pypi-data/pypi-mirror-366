from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roomairsettings_Threenodedisplacementventilation(EpBunch):
    """The UCSD model for Displacement Ventilation"""

    Zone_Name: Annotated[str, Field(default=...)]
    """Name of Zone being described. Any existing zone name"""

    Gain_Distribution_Schedule_Name: Annotated[str, Field(default=...)]
    """Distribution of the convective heat gains between the occupied and mixed zones."""

    Number_Of_Plumes_Per_Occupant: Annotated[float, Field(gt=0.0, default=1.0)]
    """Used only in the UCSD displacement ventilation model."""

    Thermostat_Height: Annotated[float, Field(gt=0.0, default=1.1)]
    """Height of thermostat/temperature control sensor above floor"""

    Comfort_Height: Annotated[float, Field(gt=0.0, default=1.1)]
    """Height at which air temperature is calculated for comfort purposes"""

    Temperature_Difference_Threshold_For_Reporting: Annotated[float, Field(ge=0.0, default=0.4)]
    """Minimum temperature difference between predicted upper and lower layer"""