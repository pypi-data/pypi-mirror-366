from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Waterheating_Airtowaterheatpump_Variablespeed(EpBunch):
    """vairlable-speed Heat pump water heater (VSHPWH) heating coil, air-to-water direct-expansion (DX)"""

    Name: Annotated[str, Field(default=...)]
    """Unique name for this instance of a variable-speed heat pump water heater DX coil."""

    Number_Of_Speeds: Annotated[int, Field(ge=1, le=10, default=1)]

    Nominal_Speed_Level: Annotated[int, Field(default=1)]
    """must be lower than or equal to the highest speed number"""

    Rated_Water_Heating_Capacity: Annotated[float, Field(default=..., gt=0)]
    """Water Heating capacity at the rated inlet air temperatures, rated condenser inlet"""

    Rated_Evaporator_Inlet_Air_Dry_Bulb_Temperature: Annotated[float, Field(gt=5, default=19.7)]
    """Evaporator inlet air dry-bulb temperature corresponding to rated coil performance"""

    Rated_Evaporator_Inlet_Air_Wet_Bulb_Temperature: Annotated[float, Field(gt=5, default=13.5)]
    """Evaporator inlet air wet-bulb temperature corresponding to rated coil performance"""

    Rated_Condenser_Inlet_Water_Temperature: Annotated[float, Field(gt=25, default=57.5)]
    """Condenser inlet water temperature corresponding to rated coil performance"""

    Rated_Evaporator_Air_Flow_Rate: Annotated[float, Field(gt=0)]
    """Evaporator air flow rate corresponding to rated coil performance"""

    Rated_Condenser_Water_Flow_Rate: Annotated[float, Field(gt=0)]
    """Condenser water flow rate corresponding to rated coil performance"""

    Evaporator_Fan_Power_Included_In_Rated_Cop: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """Select Yes if the evaporator fan power is included in the rated COP. This choice field"""

    Condenser_Pump_Power_Included_In_Rated_Cop: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Select Yes if the condenser pump power is included in the rated COP. This choice field"""

    Condenser_Pump_Heat_Included_In_Rated_Heating_Capacity_And_Rated_Cop: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Select Yes if the condenser pump heat is included in the rated heating capacity and"""

    Fraction_Of_Condenser_Pump_Heat_To_Water: Annotated[float, Field(ge=0, le=1, default=0.2)]
    """Fraction of pump heat transferred to the condenser water. The pump is assumed"""

    Evaporator_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """The node from which the DX coil draws its inlet air."""

    Evaporator_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """The node to which the DX coil sends its outlet air."""

    Condenser_Water_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """The node from which the DX coil condenser draws its inlet water."""

    Condenser_Water_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """The node to which the DX coil condenser sends its outlet water."""

    Crankcase_Heater_Capacity: Annotated[float, Field(ge=0, default=0)]
    """The compressor crankcase heater only operates when the dry-bulb temperature of air"""

    Maximum_Ambient_Temperature_For_Crankcase_Heater_Operation: Annotated[float, Field(ge=0, default=10)]
    """The compressor crankcase heater only operates when the dry-bulb temperature of air"""

    Evaporator_Air_Temperature_Type_For_Curve_Objects: Annotated[Literal['DryBulbTemperature', 'WetBulbTemperature'], Field(default='WetBulbTemperature')]
    """Determines temperature type for heating capacity curves and"""

    Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Rated_Water_Heating_Capacity_At_Speed_1: Annotated[float, Field(default=..., gt=0)]
    """Heating capacity at the rated inlet air temperatures, rated condenser inlet"""

    Rated_Water_Heating_Cop_At_Speed_1: Annotated[float, Field(gt=0, default=3.2)]
    """Heating coefficient of performance at the rated inlet air and water temperatures,"""

    Rated_Sensible_Heat_Ratio_At_Speed_1: Annotated[float, Field(ge=0.5, le=1, default=0.85)]
    """Gross air-side sensible heat ratio at the rated inlet air temperatures,"""

    Speed_1_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(default=..., ge=0)]

    Speed_1_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(default=..., ge=0)]

    Speed_1_Reference_Unit_Water_Pump_Input_Power_At_Rated_Conditions: Annotated[float, Field(default=..., ge=0)]

    Speed_1_Total_Wh_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """Table:Lookup object can also be used"""

    Speed_1_Total_Wh_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """Table:Lookup object can also be used"""

    Speed_1_Total_Wh_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """Table:Lookup object can also be used"""

    Speed_1_Cop_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """Table:Lookup object can also be used"""

    Speed_1_Cop_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """Table:Lookup object can also be used"""

    Speed_1_Cop_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """Table:Lookup object can also be used"""

    Rated_Water_Heating_Capacity_At_Speed_2: Annotated[float, Field(gt=0)]
    """Heating capacity at the rated inlet air temperatures, rated condenser inlet"""

    Rated_Water_Heating_Cop_At_Speed_2: Annotated[float, Field(gt=0, default=3.2)]
    """Heating coefficient of performance at the rated inlet air and water temperatures,"""

    Rated_Sensible_Heat_Ratio_At_Speed_2: Annotated[float, Field(ge=0.5, le=1, default=0.85)]
    """Gross air-side sensible heat ratio at the rated inlet air temperatures,"""

    Speed_2_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_2_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_2_Reference_Unit_Water_Pump_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_2_Total_Wh_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_2_Total_Wh_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_2_Total_Wh_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_2_Cop_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_2_Cop_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_2_Cop_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Rated_Water_Heating_Capacity_At_Speed_3: Annotated[float, Field(gt=0)]
    """Heating capacity at the rated inlet air temperatures, rated condenser inlet"""

    Rated_Water_Heating_Cop_At_Speed_3: Annotated[float, Field(gt=0, default=3.2)]
    """Heating coefficient of performance at the rated inlet air and water temperatures,"""

    Rated_Sensible_Heat_Ratio_At_Speed_3: Annotated[float, Field(ge=0.5, le=1, default=0.85)]
    """Gross air-side sensible heat ratio at the rated inlet air temperatures,"""

    Speed_3_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_3_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_3_Reference_Unit_Water_Pump_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_3_Total_Wh_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_3_Total_Wh_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_3_Total_Wh_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_3_Cop_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_3_Cop_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_3_Cop_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Rated_Water_Heating_Capacity_At_Speed_4: Annotated[float, Field(gt=0)]
    """Heating capacity at the rated inlet air temperatures, rated condenser inlet"""

    Rated_Water_Heating_Cop_At_Speed_4: Annotated[float, Field(gt=0, default=3.2)]
    """Heating coefficient of performance at the rated inlet air and water temperatures,"""

    Rated_Sensible_Heat_Ratio_At_Speed_4: Annotated[float, Field(ge=0.5, le=1, default=0.85)]
    """Gross air-side sensible heat ratio at the rated inlet air temperatures,"""

    Speed_4_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_4_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_4_Reference_Unit_Water_Pump_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_4_Total_Wh_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_4_Total_Wh_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_4_Total_Wh_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_4_Cop_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_4_Cop_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_4_Cop_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Rated_Water_Heating_Capacity_At_Speed_5: Annotated[float, Field(gt=0)]
    """Heating capacity at the rated inlet air temperatures, rated condenser inlet"""

    Rated_Water_Heating_Cop_At_Speed_5: Annotated[float, Field(gt=0, default=3.2)]
    """Heating coefficient of performance at the rated inlet air and water temperatures,"""

    Rated_Sensible_Heat_Ratio_At_Speed_5: Annotated[float, Field(ge=0.5, le=1, default=0.85)]
    """Gross air-side sensible heat ratio at the rated inlet air temperatures,"""

    Speed_5_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_5_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_5_Reference_Unit_Water_Pump_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_5_Total_Wh_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_5_Total_Wh_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_5_Total_Wh_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_5_Cop_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_5_Cop_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_5_Cop_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Rated_Water_Heating_Capacity_At_Speed_6: Annotated[float, Field(gt=0)]
    """Heating capacity at the rated inlet air temperatures, rated condenser inlet"""

    Rated_Water_Heating_Cop_At_Speed_6: Annotated[float, Field(gt=0, default=3.2)]
    """Heating coefficient of performance at the rated inlet air and water temperatures,"""

    Rated_Sensible_Heat_Ratio_At_Speed_6: Annotated[float, Field(ge=0.5, le=1, default=0.85)]
    """Gross air-side sensible heat ratio at the rated inlet air temperatures,"""

    Speed_6_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_6_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_6_Reference_Unit_Water_Pump_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_6_Total_Wh_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_6_Total_Wh_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_6_Total_Wh_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_6_Cop_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_6_Cop_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_6_Cop_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Rated_Water_Heating_Capacity_At_Speed_7: Annotated[float, Field(gt=0)]
    """Heating capacity at the rated inlet air temperatures, rated condenser inlet"""

    Rated_Water_Heating_Cop_At_Speed_7: Annotated[float, Field(gt=0, default=3.2)]
    """Heating coefficient of performance at the rated inlet air and water temperatures,"""

    Rated_Sensible_Heat_Ratio_At_Speed_7: Annotated[float, Field(ge=0.5, le=1, default=0.85)]
    """Gross air-side sensible heat ratio at the rated inlet air temperatures,"""

    Speed_7_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_7_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_7_Reference_Unit_Water_Pump_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_7_Total_Wh_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_7_Total_Wh_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_7_Total_Wh_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_7_Cop_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_7_Cop_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_7_Cop_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Rated_Water_Heating_Capacity_At_Speed_8: Annotated[float, Field(gt=0)]
    """Heating capacity at the rated inlet air temperatures, rated condenser inlet"""

    Rated_Water_Heating_Cop_At_Speed_8: Annotated[float, Field(gt=0, default=3.2)]
    """Heating coefficient of performance at the rated inlet air and water temperatures,"""

    Rated_Sensible_Heat_Ratio_At_Speed_8: Annotated[float, Field(ge=0.5, le=1, default=0.85)]
    """Gross air-side sensible heat ratio at the rated inlet air temperatures,"""

    Speed_8_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_8_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_8_Reference_Unit_Water_Pump_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_8_Total_Wh_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_8_Total_Wh_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_8_Total_Wh_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_8_Cop_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_8_Cop_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_8_Cop_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Rated_Water_Heating_Capacity_At_Speed_9: Annotated[float, Field(gt=0)]
    """Heating capacity at the rated inlet air temperatures, rated condenser inlet"""

    Rated_Water_Heating_Cop_At_Speed_9: Annotated[float, Field(gt=0, default=3.2)]
    """Heating coefficient of performance at the rated inlet air and water temperatures,"""

    Rated_Sensible_Heat_Ratio_At_Speed_9: Annotated[float, Field(ge=0.5, le=1, default=0.85)]
    """Gross air-side sensible heat ratio at the rated inlet air temperatures,"""

    Speed_9_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_9_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_9_Reference_Unit_Water_Pump_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_9_Total_Wh_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_9_Total_Wh_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_9_Total_Wh_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_9_Cop_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_9_Cop_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_9_Cop_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Rated_Water_Heating_Capacity_At_Speed_10: Annotated[float, Field(gt=0)]
    """Heating capacity at the rated inlet air temperatures, rated condenser inlet"""

    Rated_Water_Heating_Cop_At_Speed_10: Annotated[float, Field(gt=0, default=3.2)]
    """Heating coefficient of performance at the rated inlet air and water temperatures,"""

    Rated_Sensible_Heat_Ratio_At_Speed_10: Annotated[float, Field(ge=0.5, le=1, default=0.85)]
    """Gross air-side sensible heat ratio at the rated inlet air temperatures,"""

    Speed_10_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_10_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_10_Reference_Unit_Water_Pump_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_10_Total_Wh_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_10_Total_Wh_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_10_Total_Wh_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_10_Cop_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_10_Cop_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""

    Speed_10_Cop_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Table:Lookup object can also be used"""