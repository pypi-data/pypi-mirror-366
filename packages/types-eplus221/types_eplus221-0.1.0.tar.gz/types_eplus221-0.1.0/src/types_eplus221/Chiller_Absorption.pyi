from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Chiller_Absorption(EpBunch):
    """This indirect absorption chiller model is the empirical model from the"""

    Name: Annotated[str, Field(default=...)]

    Nominal_Capacity: Annotated[float, Field(default=..., gt=0.0)]

    Nominal_Pumping_Power: Annotated[str, Field(default=...)]

    Chilled_Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Chilled_Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Condenser_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Condenser_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Minimum_Part_Load_Ratio: Annotated[str, Field()]

    Maximum_Part_Load_Ratio: Annotated[str, Field()]

    Optimum_Part_Load_Ratio: Annotated[str, Field()]

    Design_Condenser_Inlet_Temperature: Annotated[str, Field()]

    Design_Chilled_Water_Flow_Rate: Annotated[float, Field(gt=0)]
    """For variable volume this is the max flow & for constant flow this is the flow."""

    Design_Condenser_Water_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """The steam use coefficients below specify the"""

    Coefficient_1_Of_The_Hot_Water_Or_Steam_Use_Part_Load_Ratio_Curve: Annotated[str, Field()]

    Coefficient_2_Of_The_Hot_Water_Or_Steam_Use_Part_Load_Ratio_Curve: Annotated[str, Field()]

    Coefficient_3_Of_The_Hot_Water_Or_Steam_Use_Part_Load_Ratio_Curve: Annotated[str, Field()]

    Coefficient_1_Of_The_Pump_Electric_Use_Part_Load_Ratio_Curve: Annotated[str, Field()]
    """The pump electric use coefficients specify the"""

    Coefficient_2_Of_The_Pump_Electric_Use_Part_Load_Ratio_Curve: Annotated[str, Field()]

    Coefficient_3_Of_The_Pump_Electric_Use_Part_Load_Ratio_Curve: Annotated[str, Field()]

    Chilled_Water_Outlet_Temperature_Lower_Limit: Annotated[str, Field()]

    Generator_Inlet_Node_Name: Annotated[str, Field()]

    Generator_Outlet_Node_Name: Annotated[str, Field()]

    Chiller_Flow_Mode: Annotated[Literal['ConstantFlow', 'LeavingSetpointModulated', 'NotModulated'], Field(default='NotModulated')]
    """Select operating mode for fluid flow through the chiller. "NotModulated" is for"""

    Generator_Heat_Source_Type: Annotated[Literal['Steam', 'HotWater'], Field(default='Steam')]
    """The Generator side of the chiller can be connected to a hot water or steam plant where the"""

    Design_Generator_Fluid_Flow_Rate: Annotated[float, Field(gt=0.0)]

    Degree_Of_Subcooling_In_Steam_Generator: Annotated[float, Field(default=1.0)]
    """This field is not used when the generator inlet/outlet nodes are not specified or"""

    Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized capacity and flow rates"""