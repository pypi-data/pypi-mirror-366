from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Variablelocation(EpBunch):
    """Captures the scheduling of a moving/reorienting building, or more likely a vessel"""

    Name: Annotated[str, Field(default=...)]

    Building_Location_Latitude_Schedule: Annotated[str, Field()]
    """The name of a schedule that defines the latitude of the building at any time."""

    Building_Location_Longitude_Schedule: Annotated[str, Field()]
    """The name of a schedule that defines the longitude of the building at any time."""

    Building_Location_Orientation_Schedule: Annotated[str, Field()]
    """The name of a schedule that defines the orientation of the building at any time."""