from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Heating_Electric_Multistage(EpBunch):
    """Electric heating coil, multi-stage. If the coil is located directly in an air loop"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Temperature_Setpoint_Node_Name: Annotated[str, Field()]
    """Required if coil is temperature controlled."""

    Number_of_Stages: Annotated[int, Field(default=..., ge=1, le=4)]
    """Enter the number of the following sets of data for coil"""

    Stage_1_Efficiency: Annotated[float, Field(default=..., gt=0.0)]

    Stage_1_Nominal_Capacity: Annotated[float, Field(default=..., gt=0.0)]

    Stage_2_Efficiency: Annotated[float, Field(gt=0.0)]

    Stage_2_Nominal_Capacity: Annotated[float, Field(gt=0.0)]

    Stage_3_Efficiency: Annotated[float, Field(gt=0.0)]

    Stage_3_Nominal_Capacity: Annotated[float, Field(gt=0.0)]

    Stage_4_Efficiency: Annotated[float, Field(gt=0.0)]

    Stage_4_Nominal_Capacity: Annotated[float, Field(gt=0.0)]