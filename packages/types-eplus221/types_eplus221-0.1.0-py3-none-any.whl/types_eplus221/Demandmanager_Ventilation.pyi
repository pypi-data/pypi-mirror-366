from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Demandmanager_Ventilation(EpBunch):
    """used for demand limiting Controller:OutdoorAir objects."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this demand manager. Schedule value > 0 means the demand manager is available."""

    Limit_Control: Annotated[Literal['Off', 'FixedRate', 'ReductionRatio'], Field(default=...)]

    Minimum_Limit_Duration: Annotated[int, Field(gt=0)]
    """If blank, duration defaults to the timestep"""

    Fixed_Rate: Annotated[float, Field(ge=0.0)]
    """Used in case when Limit strategy is set to FixedRate"""

    Reduction_Ratio: Annotated[float, Field(ge=0.0, le=1.0)]
    """Used in case when Limit Control is set to ReductionRatio"""

    Limit_Step_Change: Annotated[float, Field()]
    """Not yet implemented"""

    Selection_Control: Annotated[Literal['All', 'RotateMany', 'RotateOne'], Field(default='All')]

    Rotation_Duration: Annotated[int, Field(ge=0)]
    """If blank, duration defaults to the timestep"""

    Controller_Outdoor_Air_1_Name: Annotated[str, Field(default=...)]
    """Enter the name of a Controller:OutdoorAir object."""

    Controller_Outdoor_Air_2_Name: Annotated[str, Field()]

    Controller_Outdoor_Air_3_Name: Annotated[str, Field()]

    Controller_Outdoor_Air_4_Name: Annotated[str, Field()]

    Controller_Outdoor_Air_5_Name: Annotated[str, Field()]

    Controller_Outdoor_Air_6_Name: Annotated[str, Field()]

    Controller_Outdoor_Air_7_Name: Annotated[str, Field()]

    Controller_Outdoor_Air_8_Name: Annotated[str, Field()]

    Controller_Outdoor_Air_9_Name: Annotated[str, Field()]

    Controller_Outdoor_Air_10_Name: Annotated[str, Field()]