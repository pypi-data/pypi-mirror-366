from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Chiller_Absorption_Indirect(EpBunch):
    """This indirect absorption chiller model is an enhanced model from the"""

    Name: Annotated[str, Field(default=...)]

    Nominal_Capacity: Annotated[float, Field(default=..., gt=0.0)]

    Nominal_Pumping_Power: Annotated[float, Field(default=..., ge=0.0)]

    Chilled_Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Chilled_Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Condenser_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Condenser_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Minimum_Part_Load_Ratio: Annotated[float, Field(ge=0.0)]

    Maximum_Part_Load_Ratio: Annotated[float, Field(ge=0.0)]

    Optimum_Part_Load_Ratio: Annotated[float, Field(ge=0.0)]

    Design_Condenser_Inlet_Temperature: Annotated[float, Field(default=30.0)]
    """Used only when condenser flow rate is autosized."""

    Condenser_Inlet_Temperature_Lower_Limit: Annotated[float, Field(default=15.0)]
    """Provides warnings when entering condenser temperature is below minimum."""

    Chilled_Water_Outlet_Temperature_Lower_Limit: Annotated[float, Field(default=5.0)]
    """Capacity is adjusted when leaving chilled water temperature is below minimum."""

    Design_Chilled_Water_Flow_Rate: Annotated[float, Field(gt=0, default=autosize)]
    """For variable flow this is the max flow & for constant flow this is the flow."""

    Design_Condenser_Water_Flow_Rate: Annotated[float, Field(gt=0.0, default=autosize)]

    Chiller_Flow_Mode: Annotated[Literal['ConstantFlow', 'LeavingSetpointModulated', 'NotModulated'], Field(default='NotModulated')]
    """Select operating mode for fluid flow through the chiller. "NotModulated" is for"""

    Generator_Heat_Input_Function_Of_Part_Load_Ratio_Curve_Name: Annotated[str, Field(default=...)]

    Pump_Electric_Input_Function_Of_Part_Load_Ratio_Curve_Name: Annotated[str, Field()]

    Generator_Inlet_Node_Name: Annotated[str, Field()]
    """Enter the generator inlet node name which connects this chiller to a"""

    Generator_Outlet_Node_Name: Annotated[str, Field()]
    """Enter the generator outlet node name which connects this chiller to a"""

    Capacity_Correction_Function_Of_Condenser_Temperature_Curve_Name: Annotated[str, Field()]
    """Curve which shows the change in normalized capacity to changes in condenser temperature."""

    Capacity_Correction_Function_Of_Chilled_Water_Temperature_Curve_Name: Annotated[str, Field()]
    """Curve which shows the change in normalized capacity to changes in leaving chilled water temperature."""

    Capacity_Correction_Function_Of_Generator_Temperature_Curve_Name: Annotated[str, Field()]
    """Used when generator fluid type is hot water"""

    Generator_Heat_Input_Correction_Function_Of_Condenser_Temperature_Curve_Name: Annotated[str, Field()]
    """Curve which shows the change in normalized heat input to changes in condenser temperature."""

    Generator_Heat_Input_Correction_Function_Of_Chilled_Water_Temperature_Curve_Name: Annotated[str, Field()]
    """Curve which shows the change in normalized heat input to changes in leaving chilled water temperature."""

    Generator_Heat_Source_Type: Annotated[Literal['HotWater', 'Steam'], Field(default='Steam')]
    """The Generator side of the chiller can be connected to a hot water or steam plant where the"""

    Design_Generator_Fluid_Flow_Rate: Annotated[float, Field()]
    """For variable flow this is the max flow and for constant flow this is the flow."""

    Temperature_Lower_Limit_Generator_Inlet: Annotated[float, Field(default=0.0)]
    """Provides warnings when entering generator temperature is below minimum."""

    Degree_Of_Subcooling_In_Steam_Generator: Annotated[float, Field(ge=0.0, le=20.0, default=1.0)]
    """This field is not used when the generator inlet/outlet nodes are not specified or"""

    Degree_Of_Subcooling_In_Steam_Condensate_Loop: Annotated[float, Field(ge=0.0, default=0.0)]
    """This field is not used when the generator inlet/outlet nodes are not specified or"""

    Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized capacity and flow rates"""