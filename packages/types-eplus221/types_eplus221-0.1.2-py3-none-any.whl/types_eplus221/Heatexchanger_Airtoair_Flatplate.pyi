from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Heatexchanger_Airtoair_Flatplate(EpBunch):
    """Flat plate air-to-air heat exchanger, typically used for exhaust or relief air heat"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Flow_Arrangement_Type: Annotated[Literal['CounterFlow', 'ParallelFlow', 'CrossFlowBothUnmixed'], Field()]

    Economizer_Lockout: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """Yes means that the heat exchanger will be locked out (off)"""

    Ratio_of_Supply_to_Secondary_hA_Values: Annotated[float, Field(ge=0.0)]
    """Ratio of h*A for supply side to h*A for exhaust side"""

    Nominal_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0.0, default=autosize)]

    Nominal_Supply_Air_Inlet_Temperature: Annotated[float, Field(default=...)]

    Nominal_Supply_Air_Outlet_Temperature: Annotated[float, Field(default=...)]

    Nominal_Secondary_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Nominal_Secondary_Air_Inlet_Temperature: Annotated[float, Field(default=...)]

    Nominal_Electric_Power: Annotated[float, Field()]

    Supply_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Supply_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Secondary_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Secondary_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]