from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Heatexchanger_Desiccant_Balancedflow(EpBunch):
    """This object models a balanced desiccant heat exchanger."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Regeneration_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Regeneration_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Process_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Process_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Heat_Exchanger_Performance_Object_Type: Annotated[Literal['HeatExchanger:Desiccant:BalancedFlow:PerformanceDataType1'], Field(default='HeatExchanger:Desiccant:BalancedFlow:PerformanceDataType1')]

    Heat_Exchanger_Performance_Name: Annotated[str, Field(default=...)]

    Economizer_Lockout: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Yes means that the heat exchanger will be locked out (off)"""