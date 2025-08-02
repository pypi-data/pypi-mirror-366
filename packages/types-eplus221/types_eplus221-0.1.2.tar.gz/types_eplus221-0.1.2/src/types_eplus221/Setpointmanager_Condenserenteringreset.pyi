from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Condenserenteringreset(EpBunch):
    """This setpoint manager uses one curve to determine the optimum condenser entering water temperature"""

    Name: Annotated[str, Field(default=...)]

    Control_Variable: Annotated[Literal['Temperature'], Field(default='Temperature')]

    Default_Condenser_Entering_Water_Temperature_Schedule_Name: Annotated[str, Field(default=...)]
    """This scheduled setpoint value is only used in a given timestep if the"""

    Minimum_Design_Wetbulb_Temperature_Curve_Name: Annotated[str, Field(default=...)]

    Minimum_Outside_Air_Wetbulb_Temperature_Curve_Name: Annotated[str, Field(default=...)]

    Optimized_Cond_Entering_Water_Temperature_Curve_Name: Annotated[str, Field(default=...)]

    Minimum_Lift: Annotated[float, Field(default=11.1)]

    Maximum_Condenser_Entering_Water_Temperature: Annotated[float, Field(default=32)]

    Cooling_Tower_Design_Inlet_Air_WetBulb_Temperature: Annotated[float, Field(default=25.56)]

    Setpoint_Node_or_NodeList_Name: Annotated[str, Field(default=...)]
    """Node(s) at which control variable will be set"""