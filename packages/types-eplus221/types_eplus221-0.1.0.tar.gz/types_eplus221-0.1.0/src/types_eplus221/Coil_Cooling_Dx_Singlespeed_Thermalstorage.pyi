from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Cooling_Dx_Singlespeed_Thermalstorage(EpBunch):
    """Direct expansion (DX) cooling coil and condensing unit (includes electric compressor"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Operating_Mode_Control_Method: Annotated[Literal['ScheduledModes', 'EMSControlled'], Field(default=...)]

    Operation_Mode_Control_Schedule_Name: Annotated[str, Field()]
    """This field is used if the control method is set to ScheduledModes"""

    Storage_Type: Annotated[Literal['Water', 'UserDefinedFluidType', 'Ice'], Field(default=...)]

    User_Defined_Fluid_Type: Annotated[str, Field()]
    """This field is required when Storage Type is UserDefinedFluidType"""

    Fluid_Storage_Volume: Annotated[float, Field(gt=0)]
    """required field if Storage Type is Water or UserDefinedFluidType"""

    Ice_Storage_Capacity: Annotated[float, Field(gt=0)]
    """required field if Storage Type is Ice"""

    Storage_Capacity_Sizing_Factor: Annotated[float, Field()]
    """If one of the previous two fields is set to autocalculate, this determines the storage capacity"""

    Storage_Tank_Ambient_Temperature_Node_Name: Annotated[str, Field(default=...)]

    Storage_Tank_To_Ambient_U_Value_Times_Area_Heat_Transfer_Coefficient: Annotated[float, Field(default=..., gt=0)]

    Fluid_Storage_Tank_Rating_Temperature: Annotated[float, Field()]
    """required field if Storage Type is Water or UserDefinedFluidType"""

    Rated_Evaporator_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0)]
    """Flow rate corresponding to rated total cooling capacity, Rated SHR and Rated COP"""

    Evaporator_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Evaporator_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Cooling_Only_Mode_Available: Annotated[Literal['Yes', 'No'], Field(default=...)]

    Cooling_Only_Mode_Rated_Total_Evaporator_Cooling_Capacity: Annotated[float, Field(ge=0.0)]
    """required field if Cooling Only Mode is available or if autocalculating sizes"""

    Cooling_Only_Mode_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0.0, le=1.0, default=0.7)]
    """required field if Cooling Only Mode is available"""

    Cooling_Only_Mode_Rated_Cop: Annotated[float, Field(ge=0.0, default=3.0)]
    """Gross cooling capacity divided by power input to the compressor and outdoor fan,"""

    Cooling_Only_Mode_Total_Evaporator_Cooling_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Cooling Only Mode is available"""

    Cooling_Only_Mode_Total_Evaporator_Cooling_Capacity_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """required field if Cooling Only Mode is available"""

    Cooling_Only_Mode_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Cooling Only Mode is available"""

    Cooling_Only_Mode_Energy_Input_Ratio_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """required field if Cooling Only Mode is available"""

    Cooling_Only_Mode_Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field()]
    """required field if Cooling Only Mode is available"""

    Cooling_Only_Mode_Sensible_Heat_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Cooling Only Mode is available"""

    Cooling_Only_Mode_Sensible_Heat_Ratio_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """required field if Cooling Only Mode is available"""

    Cooling_And_Charge_Mode_Available: Annotated[Literal['Yes', 'No'], Field(default=...)]

    Cooling_And_Charge_Mode_Rated_Total_Evaporator_Cooling_Capacity: Annotated[float, Field(ge=0.0)]
    """required field if Cooling And Charge Mode is available"""

    Cooling_And_Charge_Mode_Capacity_Sizing_Factor: Annotated[float, Field(default=0.5)]
    """If previous field is autocalculate, this determines the evaporator capacity"""

    Cooling_And_Charge_Mode_Rated_Storage_Charging_Capacity: Annotated[float, Field(ge=0.0)]
    """required field if Cooling And Charge Mode is available"""

    Cooling_And_Charge_Mode_Storage_Capacity_Sizing_Factor: Annotated[float, Field(default=0.5)]
    """If previous field is autocalculate, this determines the storage cooling capacity"""

    Cooling_And_Charge_Mode_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0.0, le=1.0, default=0.7)]
    """required field if Cooling And Charge Mode is available"""

    Cooling_And_Charge_Mode_Cooling_Rated_Cop: Annotated[float, Field(ge=0.0, default=3.0)]
    """Gross evaporator cooling capacity divided by power input to the compressor (for cooling) and outdoor fan,"""

    Cooling_And_Charge_Mode_Charging_Rated_Cop: Annotated[float, Field(ge=0.0, default=3.0)]
    """net cooling capacity divided by power input to the compressor (for charging) and outdoor fan,"""

    Cooling_And_Charge_Mode_Total_Evaporator_Cooling_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Charge Mode is available"""

    Cooling_And_Charge_Mode_Total_Evaporator_Cooling_Capacity_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Charge Mode is available"""

    Cooling_And_Charge_Mode_Evaporator_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Charge Mode is available"""

    Cooling_And_Charge_Mode_Evaporator_Energy_Input_Ratio_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Charge Mode is available"""

    Cooling_And_Charge_Mode_Evaporator_Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Charge Mode is available"""

    Cooling_And_Charge_Mode_Storage_Charge_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Charge Mode is available"""

    Cooling_And_Charge_Mode_Storage_Charge_Capacity_Function_Of_Total_Evaporator_Plr_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Charge Mode is available"""

    Cooling_And_Charge_Mode_Storage_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Charge Mode is available"""

    Cooling_And_Charge_Mode_Storage_Energy_Input_Ratio_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Charge Mode is available"""

    Cooling_And_Charge_Mode_Storage_Energy_Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Charge Mode is available"""

    Cooling_And_Charge_Mode_Sensible_Heat_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Charge Mode is available"""

    Cooling_And_Charge_Mode_Sensible_Heat_Ratio_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Charge Mode is available"""

    Cooling_And_Discharge_Mode_Available: Annotated[Literal['Yes', 'No'], Field(default=...)]

    Cooling_And_Discharge_Mode_Rated_Total_Evaporator_Cooling_Capacity: Annotated[float, Field(ge=0.0)]
    """required field if Cooling And Discharge Mode is available"""

    Cooling_And_Discharge_Mode_Evaporator_Capacity_Sizing_Factor: Annotated[float, Field(default=1.0)]
    """If previous field is autocalculate, this determines the charging capacity"""

    Cooling_And_Discharge_Mode_Rated_Storage_Discharging_Capacity: Annotated[float, Field(ge=0.0)]
    """required field if Cooling And Discharge Mode is available"""

    Cooling_And_Discharge_Mode_Storage_Discharge_Capacity_Sizing_Factor: Annotated[float, Field(default=1.0)]
    """If previous field is autocalculate, this determines the charging capacity"""

    Cooling_And_Discharge_Mode_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0.0, le=1.0, default=0.7)]
    """required field if Cooling And Discharge Mode is available"""

    Cooling_And_Discharge_Mode_Cooling_Rated_Cop: Annotated[float, Field(ge=0.0, default=3.0)]
    """Gross evaporator cooling capacity divided by power input to the compressor (for cooling) and outdoor fan,"""

    Cooling_And_Discharge_Mode_Discharging_Rated_Cop: Annotated[float, Field(ge=0.0, default=3.0)]
    """gross cooling capacity divided by power input to the compressor (for discharging),"""

    Cooling_And_Discharge_Mode_Total_Evaporator_Cooling_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Cooling Only Mode is available"""

    Cooling_And_Discharge_Mode_Total_Evaporator_Cooling_Capacity_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Discharge Mode is available"""

    Cooling_And_Discharge_Mode_Evaporator_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Discharge Mode is available"""

    Cooling_And_Discharge_Mode_Evaporator_Energy_Input_Ratio_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Discharge Mode is available"""

    Cooling_And_Discharge_Mode_Evaporator_Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Discharge Mode is available"""

    Cooling_And_Discharge_Mode_Storage_Discharge_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Discharge Mode is available"""

    Cooling_And_Discharge_Mode_Storage_Discharge_Capacity_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Discharge Mode is available"""

    Cooling_And_Discharge_Mode_Storage_Discharge_Capacity_Function_Of_Total_Evaporator_Plr_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Discharge Mode is available"""

    Cooling_And_Discharge_Mode_Storage_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Discharge Mode is available"""

    Cooling_And_Discharge_Mode_Storage_Energy_Input_Ratio_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Discharge Mode is available"""

    Cooling_And_Discharge_Mode_Storage_Energy_Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Discharge Mode is available"""

    Cooling_And_Discharge_Mode_Sensible_Heat_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Discharge Mode is available"""

    Cooling_And_Discharge_Mode_Sensible_Heat_Ratio_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """required field if Cooling And Discharge Mode is available"""

    Charge_Only_Mode_Available: Annotated[Literal['Yes', 'No'], Field(default=...)]

    Charge_Only_Mode_Rated_Storage_Charging_Capacity: Annotated[float, Field(ge=0.0)]
    """required field if Charge Only Mode is available"""

    Charge_Only_Mode_Capacity_Sizing_Factor: Annotated[float, Field(default=1.0)]
    """If previous field is autocalculate, this determines the charging capacity"""

    Charge_Only_Mode_Charging_Rated_Cop: Annotated[float, Field(ge=0.0, default=3.0)]
    """net cooling capacity divided by power input to the compressor (for charging) and outdoor fan,"""

    Charge_Only_Mode_Storage_Charge_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Charge Only Mode is available"""

    Charge_Only_Mode_Storage_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Charge Only Mode is available"""

    Discharge_Only_Mode_Available: Annotated[Literal['Yes', 'No'], Field(default=...)]

    Discharge_Only_Mode_Rated_Storage_Discharging_Capacity: Annotated[float, Field(ge=0.0)]
    """required field if Discharge Only Mode is available"""

    Discharge_Only_Mode_Capacity_Sizing_Factor: Annotated[float, Field(default=1.0)]
    """If previous field is autocalculate, this determines the discharging capacity"""

    Discharge_Only_Mode_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0.0, le=1.0)]
    """required field if Discharge Only Mode is available"""

    Discharge_Only_Mode_Rated_Cop: Annotated[float, Field(ge=0.0, default=3.0)]
    """required field if Discharge Only Mode is available"""

    Discharge_Only_Mode_Storage_Discharge_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Discharge Only Mode is available"""

    Discharge_Only_Mode_Storage_Discharge_Capacity_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """required field if Discharge Only Mode is available"""

    Discharge_Only_Mode_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Discharge Only Mode is available"""

    Discharge_Only_Mode_Energy_Input_Ratio_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """required field if Discharge Only Mode is available"""

    Discharge_Only_Mode_Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field()]
    """required field if Discharge Only Mode is available"""

    Discharge_Only_Mode_Sensible_Heat_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """required field if Discharge Only Mode is available"""

    Discharge_Only_Mode_Sensible_Heat_Ratio_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """required field if Discharge Only Mode is available"""

    Ancillary_Electric_Power: Annotated[float, Field(ge=0.0)]
    """controls and miscellaneous standby ancillary electric power draw, when available"""

    Cold_Weather_Operation_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]

    Cold_Weather_Operation_Ancillary_Power: Annotated[float, Field(ge=0.0)]

    Condenser_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Enter the name of an outdoor air node. This node name is also specified in"""

    Condenser_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Condenser_Design_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Used to calculate condenser leaving conditions and water use if evaporatively cooled."""

    Condenser_Air_Flow_Sizing_Factor: Annotated[float, Field(default=1.0)]
    """If previous field is autocalculate, this determines the condenser air flow size as a"""

    Condenser_Type: Annotated[Literal['AirCooled', 'EvaporativelyCooled'], Field(default='AirCooled')]

    Evaporative_Condenser_Effectiveness: Annotated[float, Field(gt=0.0, le=1.0, default=0.7)]
    """required field if condenser type is evaporatively cooled"""

    Evaporative_Condenser_Pump_Rated_Power_Consumption: Annotated[float, Field(ge=0.0, default=0.0)]
    """Rated power consumed by the evaporative condenser's water pump"""

    Basin_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled and for periods"""

    Basin_Heater_Setpoint_Temperature: Annotated[float, Field(ge=2.0, default=2.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Basin_Heater_Availability_Schedule_Name: Annotated[str, Field()]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Supply_Water_Storage_Tank_Name: Annotated[str, Field()]

    Condensate_Collection_Water_Storage_Tank_Name: Annotated[str, Field()]

    Storage_Tank_Plant_Connection_Inlet_Node_Name: Annotated[str, Field()]

    Storage_Tank_Plant_Connection_Outlet_Node_Name: Annotated[str, Field()]

    Storage_Tank_Plant_Connection_Design_Flow_Rate: Annotated[float, Field(ge=0.0)]

    Storage_Tank_Plant_Connection_Heat_Transfer_Effectiveness: Annotated[float, Field(ge=0.0, le=1.0, default=0.7)]

    Storage_Tank_Minimum_Operating_Limit_Fluid_Temperature: Annotated[float, Field()]
    """For fluid storage tanks only, minimum limit for storage tank"""

    Storage_Tank_Maximum_Operating_Limit_Fluid_Temperature: Annotated[float, Field()]
    """For fluid storage tanks only, maximum limit for storage tank"""