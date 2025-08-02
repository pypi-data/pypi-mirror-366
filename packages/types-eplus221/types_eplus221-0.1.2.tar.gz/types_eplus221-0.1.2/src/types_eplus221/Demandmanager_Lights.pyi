from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Demandmanager_Lights(EpBunch):
    """used for demand limiting Lights objects."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Limit_Control: Annotated[Literal['Off', 'Fixed'], Field(default=...)]

    Minimum_Limit_Duration: Annotated[int, Field(gt=0)]
    """If blank, duration defaults to the timestep"""

    Maximum_Limit_Fraction: Annotated[float, Field(ge=0.0, le=1.0)]

    Limit_Step_Change: Annotated[float, Field()]
    """Not yet implemented"""

    Selection_Control: Annotated[Literal['All', 'RotateMany', 'RotateOne'], Field(default=...)]

    Rotation_Duration: Annotated[int, Field(ge=0)]
    """If blank, duration defaults to the timestep"""

    Lights_1_Name: Annotated[str, Field(default=...)]
    """Enter the name of an Lights object."""

    Lights_2_Name: Annotated[str, Field()]
    """Enter the name of an Lights object."""

    Lights_3_Name: Annotated[str, Field()]
    """Enter the name of an Lights object."""

    Lights_4_Name: Annotated[str, Field()]
    """Enter the name of an Lights object."""

    Lights_5_Name: Annotated[str, Field()]
    """Enter the name of an Lights object."""

    Lights_6_Name: Annotated[str, Field()]
    """Enter the name of an Lights object."""

    Lights_7_Name: Annotated[str, Field()]
    """Enter the name of an Lights object."""

    Lights_8_Name: Annotated[str, Field()]
    """Enter the name of an Lights object."""

    Lights_9_Name: Annotated[str, Field()]
    """Enter the name of an Lights object."""

    Lights_10_Name: Annotated[str, Field()]
    """Enter the name of an Lights object."""