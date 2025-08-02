from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Chiller_Constantcop(EpBunch):
    """This constant COP chiller model provides a means of quickly specifying a"""

    Name: Annotated[str, Field(default=...)]

    Nominal_Capacity: Annotated[float, Field(default=..., ge=0.0)]

    Nominal_COP: Annotated[float, Field(default=..., gt=0.0)]

    Design_Chilled_Water_Flow_Rate: Annotated[str, Field()]
    """For variable volume this is the maximum flow and for constant flow this is the flow."""

    Design_Condenser_Water_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """This field is not used for Condenser Type = AirCooled or EvaporativelyCooled"""

    Chilled_Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Chilled_Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Condenser_Inlet_Node_Name: Annotated[str, Field()]

    Condenser_Outlet_Node_Name: Annotated[str, Field()]

    Condenser_Type: Annotated[Literal['AirCooled', 'WaterCooled', 'EvaporativelyCooled'], Field(default='AirCooled')]

    Chiller_Flow_Mode: Annotated[Literal['ConstantFlow', 'LeavingSetpointModulated', 'NotModulated'], Field(default='NotModulated')]
    """Select operating mode for fluid flow through the chiller. "NotModulated" is for"""

    Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized capacity and flow rates"""

    Basin_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled and for periods"""

    Basin_Heater_Setpoint_Temperature: Annotated[float, Field(ge=2.0, default=2.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Basin_Heater_Operating_Schedule_Name: Annotated[str, Field()]
    """This field is only used for Condenser Type = EvaporativelyCooled."""