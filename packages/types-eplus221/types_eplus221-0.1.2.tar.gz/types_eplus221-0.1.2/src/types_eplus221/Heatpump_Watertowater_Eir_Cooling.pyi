from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Heatpump_Watertowater_Eir_Cooling(EpBunch):
    """An EIR formulated water to water heat pump model, cooling operation."""

    Name: Annotated[str, Field(default=...)]

    Load_Side_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Load_Side_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Source_Side_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Source_Side_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Companion_Heat_Pump_Name: Annotated[str, Field()]
    """This field allows the user to specify a companion heating"""

    Load_Side_Reference_Flow_Rate: Annotated[float, Field(gt=0.0, default=autosize)]
    """This component is currently a constant-flow device, meaning it will always"""

    Source_Side_Reference_Flow_Rate: Annotated[float, Field(gt=0.0, default=autosize)]

    Reference_Capacity: Annotated[float, Field(gt=0.0, default=autosize)]

    Reference_Coefficient_of_Performance: Annotated[float, Field(gt=0.0, default=7.5)]

    Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized capacity and flow rates"""

    Capacity_Modifier_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """Cooling capacity modifier as a function of CW supply temp and entering condenser temp"""

    Electric_Input_to_Output_Ratio_Modifier_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """Electric Input Ratio (EIR) modifier as a function of temperature"""

    Electric_Input_to_Output_Ratio_Modifier_Function_of_Part_Load_Ratio_Curve_Name: Annotated[str, Field(default=...)]
    """Electric Input Ratio (EIR) modifier as a function of Part Load Ratio (PLR)"""