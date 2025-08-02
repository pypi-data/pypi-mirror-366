from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Cooling_Dx_Twospeed(EpBunch):
    """Direct expansion (DX) cooling coil and condensing unit (includes electric compressor"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    High_Speed_Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(default=..., gt=0.0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    High_Speed_Rated_Sensible_Heat_Ratio: Annotated[float, Field(default=..., ge=0.5, le=1.0)]
    """Rated sensible heat ratio (gross sensible capacity/gross total capacity)"""

    High_Speed_Gross_Rated_Cooling_Cop: Annotated[float, Field(gt=0.0, default=3.0)]
    """Gross cooling capacity divided by power input to the compressor and outdoor fan,"""

    High_Speed_Rated_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Flow rate corresponding to rated total cooling capacity, Rated SHR"""

    Unit_Internal_Static_Air_Pressure: Annotated[float, Field(gt=0.0)]
    """Enter pressure drop for the unit containing the coil."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Total_Cooling_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*wb + c*wb**2 + d*edb + e*edb**2 + f*wb*edb"""

    Total_Cooling_Capacity_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""

    Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*wb + c*wb**2 + d*edb + e*edb**2 + f*wb*edb"""

    Energy_Input_Ratio_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""

    Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*PLR + c*PLR**2"""

    Low_Speed_Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(default=..., gt=0.0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Low_Speed_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(default=..., ge=0.5, le=1.0)]
    """Gross Rated Sensible Heat Ratio (gross sensible capacity/gross total capacity)"""

    Low_Speed_Gross_Rated_Cooling_Cop: Annotated[float, Field(gt=0.0, default=3.0)]
    """Gross cooling capacity divided by power input to the compressor and outdoor fan,"""

    Low_Speed_Rated_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Flow rate corresponding to rated total cooling capacity, Rated SHR"""

    Low_Speed_Total_Cooling_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*wb + c*wb**2 + d*edb + e*edb**2 + f*wb*edb"""

    Low_Speed_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*wb + c*wb**2 + d*edb + e*edb**2 + f*wb*edb"""

    Condenser_Air_Inlet_Node_Name: Annotated[str, Field()]
    """Enter the name of an outdoor air node. This node name is also specified in"""

    Condenser_Type: Annotated[Literal['AirCooled', 'EvaporativelyCooled'], Field(default='AirCooled')]

    Minimum_Outdoor_Dry_Bulb_Temperature_For_Compressor_Operation: Annotated[float, Field(default=-25.0)]

    High_Speed_Evaporative_Condenser_Effectiveness: Annotated[float, Field(ge=0.0, le=1.0, default=0.9)]

    High_Speed_Evaporative_Condenser_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Used to calculate evaporative condenser water use"""

    High_Speed_Evaporative_Condenser_Pump_Rated_Power_Consumption: Annotated[float, Field(ge=0.0)]
    """Rated power consumed by the evaporative condenser's water pump at high speed"""

    Low_Speed_Evaporative_Condenser_Effectiveness: Annotated[float, Field(ge=0.0, le=1.0, default=0.9)]

    Low_Speed_Evaporative_Condenser_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Used to calculate evaporative condenser water use"""

    Low_Speed_Evaporative_Condenser_Pump_Rated_Power_Consumption: Annotated[float, Field(ge=0.0)]
    """Rated power consumed by the evaporative condenser's water pump at low speed"""

    Supply_Water_Storage_Tank_Name: Annotated[str, Field()]

    Condensate_Collection_Water_Storage_Tank_Name: Annotated[str, Field()]

    Basin_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled and for periods"""

    Basin_Heater_Setpoint_Temperature: Annotated[float, Field(ge=2.0, default=2.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Basin_Heater_Operating_Schedule_Name: Annotated[str, Field()]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Sensible_Heat_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*db + e*db**2 + f*wb*db"""

    Sensible_Heat_Ratio_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ff + c*ff**2"""

    Low_Speed_Sensible_Heat_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*db + e*db**2 + f*wb*db"""

    Low_Speed_Sensible_Heat_Ratio_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ff + c*ff**2"""

    Zone_Name_For_Condenser_Placement: Annotated[str, Field()]
    """This input field is name of a conditioned or unconditioned zone where the secondary"""