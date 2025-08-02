from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zoneventilation_Windandstackopenarea(EpBunch):
    """This object is specified as natural ventilation driven by wind and stack effect only:"""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Opening_Area: Annotated[float, Field(ge=0, default=0)]
    """This is the opening area used to calculate stack effect and wind driven ventilation."""

    Opening_Area_Fraction_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the fraction values applied to the opening area given in the previous"""

    Opening_Effectiveness: Annotated[float, Field(ge=0, le=1, default=Autocalculate)]
    """This field is used to calculate wind driven ventilation."""

    Effective_Angle: Annotated[float, Field(ge=0.0, lt=360.0, default=0)]
    """This field is defined as normal angle of the opening area and is used when input"""

    Height_Difference: Annotated[float, Field(ge=0, default=0)]
    """This is the height difference between the midpoint of an opening and"""

    Discharge_Coefficient_for_Opening: Annotated[str, Field(default='Autocalculate')]
    """This is the discharge coefficient used to calculate stack effect."""

    Minimum_Indoor_Temperature: Annotated[float, Field(ge=-100, le=100, default=-100)]
    """This is the indoor temperature below which ventilation is shutoff."""

    Minimum_Indoor_Temperature_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the indoor temperature versus time below which"""

    Maximum_Indoor_Temperature: Annotated[float, Field(ge=-100, le=100, default=100)]
    """This is the indoor temperature above which ventilation is shutoff."""

    Maximum_Indoor_Temperature_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the indoor temperature versus time above which"""

    Delta_Temperature: Annotated[float, Field(ge=-100, default=-100)]
    """This is the temperature differential between indoor and outdoor below"""

    Delta_Temperature_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the temperature differential between indoor and outdoor"""

    Minimum_Outdoor_Temperature: Annotated[float, Field(ge=-100, le=100, default=-100)]
    """This is the outdoor temperature below which ventilation is shutoff."""

    Minimum_Outdoor_Temperature_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the outdoor temperature versus time below which"""

    Maximum_Outdoor_Temperature: Annotated[float, Field(ge=-100, le=100, default=100)]
    """This is the outdoor temperature above which ventilation is shutoff."""

    Maximum_Outdoor_Temperature_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the outdoor temperature versus time above which"""

    Maximum_Wind_Speed: Annotated[float, Field(ge=0, le=40, default=40)]
    """This is the outdoor wind speed above which ventilation is shutoff."""