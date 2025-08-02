from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Heating_Dx_Singlespeed(EpBunch):
    """Direct expansion (DX) heating coil (air-to-air heat pump) and compressor unit"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Gross_Rated_Heating_Capacity: Annotated[float, Field(default=..., gt=0.0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Gross_Rated_Heating_Cop: Annotated[float, Field(default=..., gt=0.0)]
    """Rated heating capacity divided by power input to the compressor and outdoor fan,"""

    Rated_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Flow rate corresponding to rated total capacity"""

    Rated_Supply_Fan_Power_Per_Volume_Flow_Rate: Annotated[float, Field(ge=0.0, le=1250.0, default=773.3)]
    """Enter the supply fan power per air volume flow rate at the rated test conditions."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Heating_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*oat + c*oat**2"""

    Heating_Capacity_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""

    Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*oat + c*oat**2"""

    Energy_Input_Ratio_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""

    Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*PLR + c*PLR**2"""

    Defrost_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """biquadratic curve = a + b*wb + c*wb**2 + d*oat + e*oat**2 + f*wb*oat"""

    Minimum_Outdoor_Dry_Bulb_Temperature_For_Compressor_Operation: Annotated[float, Field(default=-8.0)]

    Outdoor_Dry_Bulb_Temperature_To_Turn_On_Compressor: Annotated[float, Field()]
    """The outdoor temperature when the compressor is automatically turned back on following an"""

    Maximum_Outdoor_Dry_Bulb_Temperature_For_Defrost_Operation: Annotated[float, Field(ge=0.0, le=7.22, default=5.0)]

    Crankcase_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]

    Maximum_Outdoor_Dry_Bulb_Temperature_For_Crankcase_Heater_Operation: Annotated[float, Field(ge=0.0, default=10.0)]

    Defrost_Strategy: Annotated[Literal['ReverseCycle', 'Resistive'], Field(default='ReverseCycle')]

    Defrost_Control: Annotated[Literal['Timed', 'OnDemand'], Field(default='Timed')]

    Defrost_Time_Period_Fraction: Annotated[float, Field(ge=0.0, default=0.058333)]
    """Fraction of time in defrost mode"""

    Resistive_Defrost_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """only applicable if resistive defrost strategy is specified"""

    Region_Number_For_Calculating_Hspf: Annotated[int, Field(ge=1, le=6, default=4)]
    """Standard Region number for which HSPF and other standard ratings are calculated"""

    Evaporator_Air_Inlet_Node_Name: Annotated[str, Field()]
    """Enter the name of an outdoor air node. This node name is also specified in"""

    Zone_Name_For_Evaporator_Placement: Annotated[str, Field()]
    """This input field is name of a conditioned or unconditioned zone where the secondary"""

    Secondary_Coil_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """This input value is the secondary coil (evaporator) air flow rate when the heat pump"""

    Secondary_Coil_Fan_Flow_Scaling_Factor: Annotated[float, Field(gt=0.0, default=1.25)]
    """This input field is scaling factor for autosizing the secondary DX coil fan flow rate."""

    Nominal_Sensible_Heat_Ratio_Of_Secondary_Coil: Annotated[float, Field(gt=0.0, le=1.0)]
    """This input value is the nominal sensible heat ratio used to split the heat extracted by"""

    Sensible_Heat_Ratio_Modifier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*db + e*db**2 + f*wb*db"""

    Sensible_Heat_Ratio_Modifier_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ff + c*ff**2"""