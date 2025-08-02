from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Chillerheaterperformance_Electric_Eir(EpBunch):
    """This chiller model is a generic chiller-heater where the cooling mode performance is a"""

    Name: Annotated[str, Field(default=...)]

    Reference_Cooling_Mode_Evaporator_Capacity: Annotated[float, Field(default=..., gt=0.0)]

    Reference_Cooling_Mode_COP: Annotated[float, Field(default=..., gt=0.0)]
    """Efficiency of the chiller compressor (cooling output/compressor energy input)."""

    Reference_Cooling_Mode_Leaving_Chilled_Water_Temperature: Annotated[float, Field(default=6.67)]

    Reference_Cooling_Mode_Entering_Condenser_Fluid_Temperature: Annotated[float, Field(default=29.44)]

    Reference_Cooling_Mode_Leaving_Condenser_Water_Temperature: Annotated[float, Field(default=35.0)]

    Reference_Heating_Mode_Cooling_Capacity_Ratio: Annotated[float, Field(default=0.75)]
    """During simultaneous cooling-heating mode, this ratio is relative to the Reference Cooling Mode Cooling Capacity"""

    Reference_Heating_Mode_Cooling_Power_Input_Ratio: Annotated[float, Field(gt=0.0, default=1.38)]
    """During simultaneous cooling-heating mode, this ratio is relative to the Reference Cooling Mode COP"""

    Reference_Heating_Mode_Leaving_Chilled_Water_Temperature: Annotated[float, Field(default=6.67)]
    """During simultaneous cooling-heating mode"""

    Reference_Heating_Mode_Leaving_Condenser_Water_Temperature: Annotated[float, Field(default=49)]
    """During simultaneous cooling-heating mode"""

    Reference_Heating_Mode_Entering_Condenser_Fluid_Temperature: Annotated[float, Field(default=29.44)]

    Heating_Mode_Entering_Chilled_Water_Temperature_Low_Limit: Annotated[float, Field(default=12.22)]
    """During simultaneous cooling-heating mode"""

    Chilled_Water_Flow_Mode_Type: Annotated[Literal['ConstantFlow', 'VariableFlow'], Field(default='ConstantFlow')]
    """Sets chilled water flow rate to either constant or variable."""

    Design_Chilled_Water_Flow_Rate: Annotated[float, Field(gt=0)]

    Design_Condenser_Water_Flow_Rate: Annotated[float, Field(gt=0.0)]

    Design_Hot_Water_Flow_Rate: Annotated[float, Field(ge=0.0, default=0.0)]

    Compressor_Motor_Efficiency: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]
    """Fraction of compressor electrical energy that must be rejected by the condenser."""

    Condenser_Type: Annotated[Literal['AirCooled', 'WaterCooled'], Field(default='WaterCooled')]

    Cooling_Mode_Temperature_Curve_Condenser_Water_Independent_Variable: Annotated[Literal['EnteringCondenser', 'LeavingCondenser'], Field(default='EnteringCondenser')]
    """Sets the second independent variable in the three temperature dependent performance"""

    Cooling_Mode_Cooling_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """Cooling capacity as a function of leaving chilled water temperature"""

    Cooling_Mode_Electric_Input_to_Cooling_Output_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """Electric Input Ratio (EIR) as a function of supply (leaving) chilled water temperature"""

    Cooling_Mode_Electric_Input_to_Cooling_Output_Ratio_Function_of_Part_Load_Ratio_Curve_Name: Annotated[str, Field(default=...)]
    """Electric Input Ratio (EIR) as a function of Part Load Ratio (PLR)"""

    Cooling_Mode_Cooling_Capacity_Optimum_Part_Load_Ratio: Annotated[float, Field(gt=0.0, default=1.0)]
    """Optimum part load ratio where the chiller is most efficient."""

    Heating_Mode_Temperature_Curve_Condenser_Water_Independent_Variable: Annotated[Literal['EnteringCondenser', 'LeavingCondenser'], Field(default='LeavingCondenser')]
    """Sets the second independent variable in the three temperature dependent performance"""

    Heating_Mode_Cooling_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """Evaporator (cooling) capacity as a function of leaving chilled water temperature"""

    Heating_Mode_Electric_Input_to_Cooling_Output_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """Electric Input Ratio (EIR) as a function of leaving chilled water temperature when in heating or simultaneous cool/heat mode"""

    Heating_Mode_Electric_Input_to_Cooling_Output_Ratio_Function_of_Part_Load_Ratio_Curve_Name: Annotated[str, Field(default=...)]
    """Electric Input Ratio (EIR) as a function of Part Load Ratio (PLR) when in heating or simultaneous cool/heat mode"""

    Heating_Mode_Cooling_Capacity_Optimum_Part_Load_Ratio: Annotated[float, Field(gt=0.0, default=1.0)]
    """Optimum part load ratio where the chiller is most efficient when in heating or simultaneous cool/heat mode."""

    Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized capacity and flow rates"""