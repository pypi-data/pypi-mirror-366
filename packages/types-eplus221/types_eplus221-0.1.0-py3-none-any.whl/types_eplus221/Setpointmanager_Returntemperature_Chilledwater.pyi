from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Returntemperature_Chilledwater(EpBunch):
    """This setpoint manager is used to place a temperature setpoint on a plant supply"""

    Name: Annotated[str, Field(default=...)]

    Plant_Loop_Supply_Outlet_Node: Annotated[str, Field(default=...)]
    """This is the name of the supply outlet node for the plant being controlled by this"""

    Plant_Loop_Supply_Inlet_Node: Annotated[str, Field(default=...)]
    """This is the name of the supply inlet node for the plant being controlled with this"""

    Minimum_Supply_Temperature_Setpoint: Annotated[float, Field(default=5)]
    """This is the minimum chilled water supply temperature setpoint. This is also used as the default"""

    Maximum_Supply_Temperature_Setpoint: Annotated[float, Field(default=10)]
    """This is the maximum reset temperature for the chilled water supply."""

    Return_Temperature_Setpoint_Input_Type: Annotated[Literal['Constant', 'Scheduled', 'ReturnTemperatureSetpoint'], Field(default=...)]
    """This defines whether the chilled water return temperature target is constant,"""

    Return_Temperature_Setpoint_Constant_Value: Annotated[float, Field(default=13)]
    """This is the desired return temperature target, which is met by adjusting the"""

    Return_Temperature_Setpoint_Schedule_Name: Annotated[str, Field()]
    """This is the desired return temperature target, which is met by adjusting the"""