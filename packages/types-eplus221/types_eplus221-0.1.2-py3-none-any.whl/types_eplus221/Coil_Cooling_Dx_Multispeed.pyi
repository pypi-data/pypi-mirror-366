from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Cooling_Dx_Multispeed(EpBunch):
    """Direct expansion (DX) cooling coil and condensing unit (includes electric or"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Condenser_Air_Inlet_Node_Name: Annotated[str, Field()]
    """Enter the name of an outdoor air node. This node name is also specified in"""

    Condenser_Type: Annotated[Literal['AirCooled', 'EvaporativelyCooled'], Field(default='AirCooled')]

    Minimum_Outdoor_DryBulb_Temperature_for_Compressor_Operation: Annotated[float, Field(default=-25.0)]

    Supply_Water_Storage_Tank_Name: Annotated[str, Field()]

    Condensate_Collection_Water_Storage_Tank_Name: Annotated[str, Field()]

    Apply_Part_Load_Fraction_to_Speeds_Greater_than_1: Annotated[Literal['Yes', 'No'], Field(default='No')]

    Apply_Latent_Degradation_to_Speeds_Greater_than_1: Annotated[Literal['Yes', 'No'], Field(default='No')]

    Crankcase_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]

    Maximum_Outdoor_DryBulb_Temperature_for_Crankcase_Heater_Operation: Annotated[float, Field(ge=0.0, default=10.0)]

    Basin_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled and for periods"""

    Basin_Heater_Setpoint_Temperature: Annotated[float, Field(ge=2.0, default=2.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Basin_Heater_Operating_Schedule_Name: Annotated[str, Field()]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Fuel_Type: Annotated[Literal['Electricity', 'NaturalGas', 'Propane', 'Diesel', 'Gasoline', 'FuelOil#1', 'FuelOil#2', 'OtherFuel1', 'OtherFuel2'], Field(default=...)]

    Number_of_Speeds: Annotated[int, Field(default=..., ge=2, le=4)]
    """Enter the number of the following sets of data for coil capacity, SHR, COP,"""

    Speed_1_Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(default=..., gt=0.0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Speed_1_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(default=..., ge=0.5, le=1.0)]
    """Gross Rated Sensible Heat Ratio (gross sensible capacity/gross total capacity)"""

    Speed_1_Gross_Rated_Cooling_COP: Annotated[float, Field(gt=0.0, default=3.0)]
    """Gross cooling capacity divided by power input to the compressor and outdoor fan,"""

    Speed_1_Rated_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Flow rate corresponding to rated total cooling capacity, rated SHR and rated"""

    Speed_1_Rated_Evaporator_Fan_Power_Per_Volume_Flow_Rate: Annotated[float, Field(ge=0.0, le=1250.0, default=773.3)]
    """Enter the evaporator fan power per air volume flow rate at the rated test conditions."""

    Speed_1_Total_Cooling_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*wb + c*wb**2 + d*edb + e*edb**2 + f*wb*edb"""

    Speed_1_Total_Cooling_Capacity_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_1_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*wb + c*wb**2 + d*edb + e*edb**2 + f*wb*edb"""

    Speed_1_Energy_Input_Ratio_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_1_Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*PLR + c*PLR**2"""

    Speed_1_Nominal_Time_for_Condensate_Removal_to_Begin: Annotated[float, Field(ge=0.0, le=3000.0, default=0.0)]
    """The nominal time for condensate to begin leaving the coil's condensate"""

    Speed_1_Ratio_of_Initial_Moisture_Evaporation_Rate_and_Steady_State_Latent_Capacity: Annotated[float, Field(ge=0.0, le=5.0, default=0.0)]
    """Ratio of the initial moisture evaporation Rate from the Cooling Coil (when"""

    Speed_1_Maximum_Cycling_Rate: Annotated[float, Field(ge=0.0, le=5.0, default=0.0)]
    """The maximum on-off cycling rate for the compressor, which occurs at 50% run time"""

    Speed_1_Latent_Capacity_Time_Constant: Annotated[float, Field(ge=0.0, le=500.0, default=0.0)]
    """Time constant for the cooling coil's latent capacity to reach steady state after"""

    Speed_1_Rated_Waste_Heat_Fraction_of_Power_Input: Annotated[float, Field(gt=0.0, le=1.0, default=0.2)]
    """Recoverable waste heat at full load and rated conditions"""

    Speed_1_Waste_Heat_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*odb + c*odb**2 + d*db + e*db**2 + f*odb*db"""

    Speed_1_Evaporative_Condenser_Effectiveness: Annotated[float, Field(ge=0.0, le=1.0, default=0.9)]

    Speed_1_Evaporative_Condenser_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Used to calculate evaporative condenser water use"""

    Speed_1_Rated_Evaporative_Condenser_Pump_Power_Consumption: Annotated[float, Field(ge=0.0)]
    """Rated power consumed by the evaporative condenser's water pump at high speed"""

    Speed_2_Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(default=..., gt=0.0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Speed_2_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(default=..., ge=0.5, le=1.0)]
    """Gross Rated Sensible Heat Ratio (gross sensible capacity/gross total capacity)"""

    Speed_2_Gross_Rated_Cooling_COP: Annotated[float, Field(gt=0.0, default=3.0)]
    """Gross cooling capacity divided by power input to the compressor and outdoor fan,"""

    Speed_2_Rated_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Flow rate corresponding to rated total cooling capacity, rated SHR and rated"""

    Speed_2_Rated_Evaporator_Fan_Power_Per_Volume_Flow_Rate: Annotated[float, Field(ge=0.0, le=1250.0, default=773.3)]
    """Enter the evaporator fan power per air volume flow rate at the rated test conditions."""

    Speed_2_Total_Cooling_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*wb + c*wb**2 + d*edb + e*edb**2 + f*wb*edb"""

    Speed_2_Total_Cooling_Capacity_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_2_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*wb + c*wb**2 + d*edb + e*edb**2 + f*wb*edb"""

    Speed_2_Energy_Input_Ratio_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_2_Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*PLR + c*PLR**2"""

    Speed_2_Nominal_Time_for_Condensate_Removal_to_Begin: Annotated[float, Field(ge=0.0, le=3000.0, default=0.0)]
    """The nominal time for condensate to begin leaving the coil's condensate"""

    Speed_2_Ratio_of_Initial_Moisture_Evaporation_Rate_and_steady_state_Latent_Capacity: Annotated[float, Field(ge=0.0, le=5.0, default=0.0)]
    """Ratio of the initial moisture evaporation rate from the cooling coil (when"""

    Speed_2_Maximum_Cycling_Rate: Annotated[float, Field(ge=0.0, le=5.0, default=0.0)]
    """The maximum on-off cycling rate for the compressor, which occurs at 50% run time"""

    Speed_2_Latent_Capacity_Time_Constant: Annotated[float, Field(ge=0.0, le=500.0, default=0.0)]
    """Time constant for the cooling coil's latent capacity to reach steady state after"""

    Speed_2_Rated_Waste_Heat_Fraction_of_Power_Input: Annotated[float, Field(gt=0.0, le=1.0, default=0.2)]
    """Recoverable waste heat at full load and rated conditions"""

    Speed_2_Waste_Heat_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*odb + c*odb**2 + d*db + e*db**2 + f*odb*db"""

    Speed_2_Evaporative_Condenser_Effectiveness: Annotated[float, Field(ge=0.0, le=1.0, default=0.9)]

    Speed_2_Evaporative_Condenser_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Used to calculate evaporative condenser water use"""

    Speed_2_Rated_Evaporative_Condenser_Pump_Power_Consumption: Annotated[float, Field(ge=0.0)]
    """Rated power consumed by the evaporative condenser's water pump at low speed"""

    Speed_3_Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(gt=0.0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Speed_3_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0.5, le=1.0)]
    """Gross Rated Sensible Heat Ratio (gross sensible capacity/gross total capacity)"""

    Speed_3_Gross_Rated_Cooling_COP: Annotated[float, Field(gt=0.0, default=3.0)]
    """Gross cooling capacity divided by power input to the compressor and outdoor fan,"""

    Speed_3_Rated_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Flow rate corresponding to rated total cooling capacity, rated SHR and rated"""

    Speed_3_Rated_Evaporator_Fan_Power_Per_Volume_Flow_Rate: Annotated[float, Field(ge=0.0, le=1250.0, default=773.3)]
    """Enter the evaporator fan power per air volume flow rate at the rated test conditions."""

    Speed_3_Total_Cooling_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*edb + e*edb**2 + f*wb*edb"""

    Speed_3_Total_Cooling_Capacity_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_3_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*edb + e*edb**2 + f*wb*edb"""

    Speed_3_Energy_Input_Ratio_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_3_Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*PLR + c*PLR**2"""

    Speed_3_Nominal_Time_for_Condensate_Removal_to_Begin: Annotated[float, Field(ge=0.0, le=3000.0, default=0.0)]
    """The nominal time for condensate to begin leaving the coil's condensate"""

    Speed_3_Ratio_of_Initial_Moisture_Evaporation_Rate_and_steady_state_Latent_Capacity: Annotated[float, Field(ge=0.0, le=5.0, default=0.0)]
    """Ratio of the initial moisture evaporation rate from the cooling coil (when"""

    Speed_3_Maximum_Cycling_Rate: Annotated[float, Field(ge=0.0, le=5.0, default=0.0)]
    """The maximum on-off cycling rate for the compressor, which occurs at 50% run time"""

    Speed_3_Latent_Capacity_Time_Constant: Annotated[float, Field(ge=0.0, le=500.0, default=0.0)]
    """Time constant for the cooling coil's latent capacity to reach steady state after"""

    Speed_3_Rated_Waste_Heat_Fraction_of_Power_Input: Annotated[float, Field(gt=0.0, le=1.0, default=0.2)]
    """Recoverable waste heat at full load and rated conditions"""

    Speed_3_Waste_Heat_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*odb + c*odb**2 + d*db + e*db**2 + f*odb*db"""

    Speed_3_Evaporative_Condenser_Effectiveness: Annotated[float, Field(ge=0.0, le=1.0, default=0.9)]

    Speed_3_Evaporative_Condenser_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Used to calculate evaporative condenser water use"""

    Speed_3_Rated_Evaporative_Condenser_Pump_Power_Consumption: Annotated[float, Field(ge=0.0)]
    """Rated power consumed by the evaporative condenser's water pump at Low speed"""

    Speed_4_Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(gt=0.0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Speed_4_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0.5, le=1.0)]
    """Gross Rated Sensible Heat Ratio (gross sensible capacity/gross total capacity)"""

    Speed_4_Gross_Rated_Cooling_COP: Annotated[float, Field(gt=0.0, default=3.0)]
    """Gross cooling capacity divided by power input to the compressor and outdoor fan,"""

    Speed_4_Rated_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Flow rate corresponding to rated total cooling capacity, rated SHR and rated"""

    Speed_4_Rated_Evaporator_Fan_Power_Per_Volume_Flow_Rate: Annotated[float, Field(ge=0.0, le=1250.0, default=773.3)]
    """Enter the evaporator fan power per air volume flow rate at the rated test conditions."""

    Speed_4_Total_Cooling_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*edb + e*edb**2 + f*wb*edb"""

    Speed_4_Total_Cooling_Capacity_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_4_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*edb + e*edb**2 + f*wb*edb"""

    Speed_4_Energy_Input_Ratio_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_4_Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*PLR + c*PLR**2"""

    Speed_4_Nominal_Time_for_Condensate_Removal_to_Begin: Annotated[float, Field(ge=0.0, le=3000.0, default=0.0)]
    """The nominal time for condensate to begin leaving the coil's condensate"""

    Speed_4_Ratio_of_Initial_Moisture_Evaporation_Rate_and_steady_state_Latent_Capacity: Annotated[float, Field(ge=0.0, le=5.0, default=0.0)]
    """Ratio of the initial moisture evaporation rate from the cooling coil (when"""

    Speed_4_Maximum_Cycling_Rate: Annotated[float, Field(ge=0.0, le=5.0, default=0.0)]
    """The maximum on-off cycling rate for the compressor, which occurs at 50% run time"""

    Speed_4_Latent_Capacity_Time_Constant: Annotated[float, Field(ge=0.0, le=500.0, default=0.0)]
    """Time constant for the cooling coil's latent capacity to reach steady state after"""

    Speed_4_Rated_Waste_Heat_Fraction_of_Power_Input: Annotated[float, Field(gt=0.0, le=1.0, default=0.2)]
    """Recoverable waste heat at full load and rated conditions"""

    Speed_4_Waste_Heat_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*odb + c*odb**2 + d*db + e*db**2 + f*odb*db"""

    Speed_4_Evaporative_Condenser_Effectiveness: Annotated[float, Field(ge=0.0, le=1.0, default=0.9)]

    Speed_4_Evaporative_Condenser_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Used to calculate evaporative condenser water use"""

    Speed_4_Rated_Evaporative_Condenser_Pump_Power_Consumption: Annotated[float, Field(ge=0.0)]
    """Rated power consumed by the evaporative condenser's water pump at Speed 4"""

    Zone_Name_for_Condenser_Placement: Annotated[str, Field()]
    """This input field is name of a conditioned or unconditioned zone where the secondary"""