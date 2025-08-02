from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Fan_Zoneexhaust(EpBunch):
    """Models a fan that exhausts air from a zone."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Fan_Total_Efficiency: Annotated[float, Field(gt=0.0, le=1.0, default=0.6)]

    Pressure_Rise: Annotated[str, Field(default=...)]

    Maximum_Flow_Rate: Annotated[str, Field()]

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    End_Use_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""

    Flow_Fraction_Schedule_Name: Annotated[str, Field()]
    """If field is used, then when fan runs the exhausted air flow rate is controlled to be the scheduled fraction times the Maximum Flow Rate"""

    System_Availability_Manager_Coupling_Mode: Annotated[Literal['Coupled', 'Decoupled'], Field(default='Coupled')]
    """Control if fan is to be interlocked with HVAC system Availability Managers or not."""

    Minimum_Zone_Temperature_Limit_Schedule_Name: Annotated[str, Field()]
    """If field is used, the exhaust fan will not run if the zone temperature is lower than this limit"""

    Balanced_Exhaust_Fraction_Schedule_Name: Annotated[str, Field()]
    """Used to control fan's impact on flow at the return air node. Enter the portion of the exhaust that is balanced by simple airflows."""