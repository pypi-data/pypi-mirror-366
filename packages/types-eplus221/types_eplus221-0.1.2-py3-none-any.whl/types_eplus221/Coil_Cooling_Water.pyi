from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Cooling_Water(EpBunch):
    """Chilled water cooling coil, NTU-effectiveness model, with inputs for design entering"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Design_Water_Flow_Rate: Annotated[str, Field(default='autosize')]

    Design_Air_Flow_Rate: Annotated[str, Field(default='autosize')]

    Design_Inlet_Water_Temperature: Annotated[str, Field(default='autosize')]

    Design_Inlet_Air_Temperature: Annotated[str, Field(default='autosize')]

    Design_Outlet_Air_Temperature: Annotated[str, Field(default='autosize')]

    Design_Inlet_Air_Humidity_Ratio: Annotated[str, Field(default='autosize')]

    Design_Outlet_Air_Humidity_Ratio: Annotated[str, Field(default='autosize')]

    Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Type_of_Analysis: Annotated[Literal['SimpleAnalysis', 'DetailedAnalysis'], Field(default='SimpleAnalysis')]

    Heat_Exchanger_Configuration: Annotated[Literal['CrossFlow', 'CounterFlow'], Field(default='CounterFlow')]

    Condensate_Collection_Water_Storage_Tank_Name: Annotated[str, Field()]

    Design_Water_Temperature_Difference: Annotated[float, Field(gt=0.0)]
    """This input field is optional. If specified, it is used for sizing the Design Water Flow Rate."""