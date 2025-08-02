from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Location(EpBunch):
    """Specifies the building's location. Only one location is allowed."""

    Name: Annotated[str, Field(default=...)]

    Latitude: Annotated[float, Field(ge=-90.0, le=+90.0, default=0.0)]
    """+ is North, - is South, degree minutes represented in decimal (i.e. 30 minutes is .5)"""

    Longitude: Annotated[float, Field(ge=-180.0, le=+180.0, default=0.0)]
    """- is West, + is East, degree minutes represented in decimal (i.e. 30 minutes is .5)"""

    Time_Zone: Annotated[float, Field(ge=-12.0, le=+14.0, default=0.0)]
    """basic these limits on the WorldTimeZone Map (2003)"""

    Elevation: Annotated[float, Field(ge=-300.0, lt=8900.0, default=0.0)]