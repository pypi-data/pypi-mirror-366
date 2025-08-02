from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Electricequipment_Ite_Aircooled(EpBunch):
    """This object describes air-cooled electric information technology equipment (ITE) which has"""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Air_Flow_Calculation_Method: Annotated[Literal['FlowFromSystem', 'FlowControlWithApproachTemperatures'], Field(default='FlowFromSystem')]
    """The specified method is used to calculate the IT inlet temperature and zone return"""

    Design_Power_Input_Calculation_Method: Annotated[Literal['Watts/Unit', 'Watts/Area'], Field(default='Watts/Unit')]
    """The entered calculation method is used to specify the design power input"""

    Watts_per_Unit: Annotated[float, Field(ge=0)]

    Number_of_Units: Annotated[float, Field(ge=0, default=1)]

    Watts_per_Zone_Floor_Area: Annotated[float, Field(ge=0)]

    Design_Power_Input_Schedule_Name: Annotated[str, Field()]
    """Operating schedule for this equipment, fraction applied to the design power input,"""

    CPU_Loading_Schedule_Name: Annotated[str, Field()]
    """CPU loading schedule for this equipment as a fraction from 0.0 (idle) to 1.0 (full load)."""

    CPU_Power_Input_Function_of_Loading_and_Air_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """The name of a two-variable curve or table lookup object which modifies the CPU power"""

    Design_Fan_Power_Input_Fraction: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """The fraction of the total power input at design conditions which is for the cooling fan(s)"""

    Design_Fan_Air_Flow_Rate_per_Power_Input: Annotated[float, Field(default=..., ge=0.0)]
    """The cooling fan air flow rate per total electric power input at design conditions"""

    Air_Flow_Function_of_Loading_and_Air_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """The name of a two-variable curve or table lookup object which modifies the cooling"""

    Fan_Power_Input_Function_of_Flow_Curve_Name: Annotated[str, Field(default=...)]
    """The name of a single-variable curve or table lookup object which modifies the cooling"""

    Design_Entering_Air_Temperature: Annotated[float, Field(default=15.0)]
    """The entering air temperature at design conditions."""

    Environmental_Class: Annotated[Literal['None', 'A1', 'A2', 'A3', 'A4', 'B', 'C'], Field()]
    """Specifies the allowable operating conditions for the air inlet conditions."""

    Air_Inlet_Connection_Type: Annotated[Literal['AdjustedSupply', 'ZoneAirNode', 'RoomAirModel'], Field(default='AdjustedSupply')]
    """Specifies the type of connection between the zone and the ITE air inlet node."""

    Air_Inlet_Room_Air_Model_Node_Name: Annotated[str, Field()]
    """Name of a RoomAir:Node object which is connected to the ITE air inlet."""

    Air_Outlet_Room_Air_Model_Node_Name: Annotated[str, Field()]
    """Name of a RoomAir:Node object which is connected to the ITE air outlet."""

    Supply_Air_Node_Name: Annotated[str, Field()]
    """Name of the supply air inlet node serving this ITE. Required if the"""

    Design_Recirculation_Fraction: Annotated[float, Field(ge=0.0, le=0.5, default=0.0)]
    """The recirculation fraction for this equipment at design conditions. This field is used only"""

    Recirculation_Function_of_Loading_and_Supply_Temperature_Curve_Name: Annotated[str, Field()]
    """The name of a two-variable curve or table lookup object which modifies the recirculation"""

    Design_Electric_Power_Supply_Efficiency: Annotated[float, Field(gt=0.0, le=1.0, default=1.0)]
    """The efficiency of the power supply system serving this ITE"""

    Electric_Power_Supply_Efficiency_Function_of_Part_Load_Ratio_Curve_Name: Annotated[str, Field()]
    """The name of a single-variable curve or table lookup object which modifies the electric"""

    Fraction_of_Electric_Power_Supply_Losses_to_Zone: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]
    """Fraction of the electric power supply losses which are a heat gain to the zone"""

    CPU_EndUse_Subcategory: Annotated[str, Field(default='ITE-CPU')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""

    Fan_EndUse_Subcategory: Annotated[str, Field(default='ITE-Fans')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""

    Electric_Power_Supply_EndUse_Subcategory: Annotated[str, Field(default='ITE-UPS')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""

    Supply_Temperature_Difference: Annotated[float, Field()]
    """The difference of the IT inlet temperature from the AHU supply air temperature."""

    Supply_Temperature_Difference_Schedule: Annotated[str, Field()]
    """The difference schedule of the IT inlet temperature from the AHU supply air temperature."""

    Return_Temperature_Difference: Annotated[float, Field()]
    """The difference of the the actual AHU return air temperature to the IT equipment outlet temperature."""

    Return_Temperature_Difference_Schedule: Annotated[str, Field()]
    """The difference schedule of the actual AHU return air temperature to the IT equipment outlet temperature."""