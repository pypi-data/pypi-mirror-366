from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Heating_Water(EpBunch):
    """Hot water heating coil, NTU-effectiveness model, assumes a cross-flow heat exchanger."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    UFactor_Times_Area_Value: Annotated[str, Field(default='autosize')]
    """UA value under rating conditions"""

    Maximum_Water_Flow_Rate: Annotated[str, Field(default='autosize')]

    Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Performance_Input_Method: Annotated[Literal['UFactorTimesAreaAndDesignWaterFlowRate', 'NominalCapacity'], Field(default='UFactorTimesAreaAndDesignWaterFlowRate')]

    Rated_Capacity: Annotated[float, Field(ge=0, default=autosize)]

    Rated_Inlet_Water_Temperature: Annotated[float, Field(default=82.2)]

    Rated_Inlet_Air_Temperature: Annotated[float, Field(default=16.6)]

    Rated_Outlet_Water_Temperature: Annotated[float, Field(default=71.1)]

    Rated_Outlet_Air_Temperature: Annotated[float, Field(default=32.2)]

    Rated_Ratio_for_Air_and_Water_Convection: Annotated[float, Field(gt=0, default=0.5)]

    Design_Water_Temperature_Difference: Annotated[float, Field(gt=0.0)]
    """This input field is optional. If specified, it is used for sizing the Design Water Flow Rate."""