from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Daylighting_Referencepoint(EpBunch):
    """Used by Daylighting:Controls to identify the reference point coordinates for each sensor."""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    XCoordinate_of_Reference_Point: Annotated[float, Field(default=...)]

    YCoordinate_of_Reference_Point: Annotated[float, Field(default=...)]

    ZCoordinate_of_Reference_Point: Annotated[float, Field(default=0.8)]