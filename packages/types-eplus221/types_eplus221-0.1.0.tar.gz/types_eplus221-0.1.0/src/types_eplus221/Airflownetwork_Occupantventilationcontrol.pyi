from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Occupantventilationcontrol(EpBunch):
    """This object is used to provide advanced thermal comfort control of window opening and closing"""

    Name: Annotated[str, Field(default=...)]
    """Enter the name where the advanced thermal comfort control is required."""

    Minimum_Opening_Time: Annotated[float, Field(ge=0.0, default=0.0)]

    Minimum_Closing_Time: Annotated[float, Field(ge=0.0, default=0.0)]

    Thermal_Comfort_Low_Temperature_Curve_Name: Annotated[str, Field()]
    """Enter a curve name that represents thermal comfort temperature as a"""

    Thermal_Comfort_Temperature_Boundary_Point: Annotated[float, Field(ge=0.0, default=10.0)]
    """This point is used to allow separate low and high thermal comfort temperature"""

    Thermal_Comfort_High_Temperature_Curve_Name: Annotated[str, Field()]
    """Enter a curve name that represents thermal comfort temperature as a"""

    Maximum_Threshold_For_Persons_Dissatisfied_Ppd: Annotated[float, Field(ge=0, le=100, default=10.0)]

    Occupancy_Check: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """If Yes, occupancy check will be performed as part of the opening probability check."""

    Opening_Probability_Schedule_Name: Annotated[str, Field()]
    """If this field is blank, the opening probability check is bypassed and opening is true."""

    Closing_Probability_Schedule_Name: Annotated[str, Field()]
    """If this field is blank, the closing probability check is bypassed and closing is true."""