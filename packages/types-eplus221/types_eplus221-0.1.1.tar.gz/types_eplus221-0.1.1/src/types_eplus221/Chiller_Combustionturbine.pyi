from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Chiller_Combustionturbine(EpBunch):
    """This chiller model is the empirical model from the Building Loads"""

    Name: Annotated[str, Field(default=...)]

    Condenser_Type: Annotated[Literal['AirCooled', 'WaterCooled', 'EvaporativelyCooled'], Field(default='AirCooled')]

    Nominal_Capacity: Annotated[str, Field(default=...)]

    Nominal_Cop: Annotated[str, Field(default=...)]

    Chilled_Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Chilled_Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Condenser_Inlet_Node_Name: Annotated[str, Field()]

    Condenser_Outlet_Node_Name: Annotated[str, Field()]

    Minimum_Part_Load_Ratio: Annotated[str, Field()]

    Maximum_Part_Load_Ratio: Annotated[str, Field()]

    Optimum_Part_Load_Ratio: Annotated[str, Field()]

    Design_Condenser_Inlet_Temperature: Annotated[str, Field()]

    Temperature_Rise_Coefficient: Annotated[str, Field(default=...)]

    Design_Chilled_Water_Outlet_Temperature: Annotated[str, Field()]

    Design_Chilled_Water_Flow_Rate: Annotated[str, Field()]
    """For variable volume this is the max flow & for constant flow this is the flow."""

    Design_Condenser_Water_Flow_Rate: Annotated[str, Field()]
    """This field is not used for Condenser Type = AirCooled or EvaporativelyCooled"""

    Coefficient_1_Of_Capacity_Ratio_Curve: Annotated[str, Field()]

    Coefficient_2_Of_Capacity_Ratio_Curve: Annotated[str, Field()]

    Coefficient_3_Of_Capacity_Ratio_Curve: Annotated[str, Field()]

    Coefficient_1_Of_Power_Ratio_Curve: Annotated[str, Field()]

    Coefficient_2_Of_Power_Ratio_Curve: Annotated[str, Field()]

    Coefficient_3_Of_Power_Ratio_Curve: Annotated[str, Field()]

    Coefficient_1_Of_Full_Load_Ratio_Curve: Annotated[str, Field()]

    Coefficient_2_Of_Full_Load_Ratio_Curve: Annotated[str, Field()]

    Coefficient_3_Of_Full_Load_Ratio_Curve: Annotated[str, Field()]

    Chilled_Water_Outlet_Temperature_Lower_Limit: Annotated[str, Field()]
    """Special Gas Turbine Chiller Parameters Below"""

    Coefficient_1_Of_Fuel_Input_Curve: Annotated[str, Field()]

    Coefficient_2_Of_Fuel_Input_Curve: Annotated[str, Field()]

    Coefficient_3_Of_Fuel_Input_Curve: Annotated[str, Field()]

    Coefficient_1_Of_Temperature_Based_Fuel_Input_Curve: Annotated[str, Field()]

    Coefficient_2_Of_Temperature_Based_Fuel_Input_Curve: Annotated[str, Field()]

    Coefficient_3_Of_Temperature_Based_Fuel_Input_Curve: Annotated[str, Field()]

    Coefficient_1_Of_Exhaust_Flow_Curve: Annotated[str, Field()]

    Coefficient_2_Of_Exhaust_Flow_Curve: Annotated[str, Field()]

    Coefficient_3_Of_Exhaust_Flow_Curve: Annotated[str, Field()]

    Coefficient_1_Of_Exhaust_Gas_Temperature_Curve: Annotated[str, Field()]

    Coefficient_2_Of_Exhaust_Gas_Temperature_Curve: Annotated[str, Field()]

    Coefficient_3_Of_Exhaust_Gas_Temperature_Curve: Annotated[str, Field()]

    Coefficient_1_Of_Temperature_Based_Exhaust_Gas_Temperature_Curve: Annotated[str, Field()]

    Coefficient_2_Of_Temperature_Based_Exhaust_Gas_Temperature_Curve: Annotated[str, Field()]

    Coefficient_3_Of_Temperature_Based_Exhaust_Gas_Temperature_Curve: Annotated[str, Field()]

    Coefficient_1_Of_Recovery_Lube_Heat_Curve: Annotated[str, Field()]

    Coefficient_2_Of_Recovery_Lube_Heat_Curve: Annotated[str, Field()]

    Coefficient_3_Of_Recovery_Lube_Heat_Curve: Annotated[str, Field()]

    Coefficient_1_Of_U_Factor_Times_Area_Curve: Annotated[str, Field()]

    Coefficient_2_Of_U_Factor_Times_Area_Curve: Annotated[str, Field()]
    """typical value .9"""

    Gas_Turbine_Engine_Capacity: Annotated[str, Field()]

    Maximum_Exhaust_Flow_Per_Unit_Of_Power_Output: Annotated[str, Field()]

    Design_Steam_Saturation_Temperature: Annotated[str, Field()]

    Fuel_Higher_Heating_Value: Annotated[str, Field()]

    Design_Heat_Recovery_Water_Flow_Rate: Annotated[str, Field(default='0.0')]
    """If non-zero, then the heat recovery inlet and outlet node names must be entered."""

    Heat_Recovery_Inlet_Node_Name: Annotated[str, Field()]

    Heat_Recovery_Outlet_Node_Name: Annotated[str, Field()]

    Chiller_Flow_Mode: Annotated[Literal['ConstantFlow', 'LeavingSetpointModulated', 'NotModulated'], Field(default='NotModulated')]
    """Select operating mode for fluid flow through the chiller. "NotModulated" is for"""

    Fuel_Type: Annotated[Literal['NaturalGas', 'PropaneGas', 'Diesel', 'Gasoline', 'FuelOil#1', 'FuelOil#2', 'OtherFuel1', 'OtherFuel2'], Field(default='NaturalGas')]

    Heat_Recovery_Maximum_Temperature: Annotated[str, Field(default='80.0')]

    Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized capacity and flow rates"""

    Basin_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled and for periods"""

    Basin_Heater_Setpoint_Temperature: Annotated[float, Field(ge=2.0, default=2.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Basin_Heater_Operating_Schedule_Name: Annotated[str, Field()]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Condenser_Heat_Recovery_Relative_Capacity_Fraction: Annotated[float, Field(ge=0.0, le=1.0)]
    """This optional field is the fraction of total rejected heat that can be recovered at full load."""

    Turbine_Engine_Efficiency: Annotated[float, Field(default=0.35)]
    """This optional field is the nominal turbine engine efficiency and is used when Gas Turbine Engine Capacity is set to Autosize"""