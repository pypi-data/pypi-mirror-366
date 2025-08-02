from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Refrigeration_Compressorrack(EpBunch):
    """Works in conjunction with the refrigeration case and walk-in objects to simulate the"""

    Name: Annotated[str, Field(default=...)]

    Heat_Rejection_Location: Annotated[Literal['Outdoors', 'Zone'], Field(default='Outdoors')]

    Design_Compressor_Rack_COP: Annotated[float, Field(gt=0.0, default=2.0)]
    """It is important that this COP correspond to the lowest saturated suction"""

    Compressor_Rack_COP_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """It is important that this COP curve correspond to the lowest saturated suction"""

    Design_Condenser_Fan_Power: Annotated[float, Field(ge=0.0, default=250.0)]
    """Design power for condenser fan(s)."""

    Condenser_Fan_Power_Function_of_Temperature_Curve_Name: Annotated[str, Field()]

    Condenser_Type: Annotated[Literal['AirCooled', 'EvaporativelyCooled', 'WaterCooled'], Field(default='AirCooled')]
    """Applicable only when Heat Rejection Location is Outdoors."""

    WaterCooled_Condenser_Inlet_Node_Name: Annotated[str, Field()]

    WaterCooled_Condenser_Outlet_Node_Name: Annotated[str, Field()]

    WaterCooled_Loop_Flow_Type: Annotated[Literal['VariableFlow', 'ConstantFlow'], Field(default='VariableFlow')]
    """Applicable only when Condenser Type is WaterCooled."""

    WaterCooled_Condenser_Outlet_Temperature_Schedule_Name: Annotated[str, Field()]
    """Applicable only when loop Flow type is VariableFlow."""

    WaterCooled_Condenser_Design_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Applicable only when loop flow type is ConstantFlow."""

    WaterCooled_Condenser_Maximum_Flow_Rate: Annotated[float, Field(gt=0.0)]

    WaterCooled_Condenser_Maximum_Water_Outlet_Temperature: Annotated[float, Field(ge=10.0, le=60.0, default=55.0)]

    WaterCooled_Condenser_Minimum_Water_Inlet_Temperature: Annotated[float, Field(ge=10.0, le=30.0, default=10.0)]

    Evaporative_Condenser_Availability_Schedule_Name: Annotated[str, Field()]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Evaporative_Condenser_Effectiveness: Annotated[float, Field(ge=0.0, le=1.0, default=0.9)]
    """Applicable only for Condenser Type = EvaporativlyCooled."""

    Evaporative_Condenser_Air_Flow_Rate: Annotated[float, Field(gt=0.0, default=Autocalculate)]
    """Applicable only for Condenser Type = EvaporativelyCooled."""

    Basin_Heater_Capacity: Annotated[float, Field(ge=0.0, default=200.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled and for periods"""

    Basin_Heater_Setpoint_Temperature: Annotated[float, Field(ge=2.0, default=2.0)]
    """Enter the outdoor dry-bulb temperature at which the basin heater turns on."""

    Design_Evaporative_Condenser_Water_Pump_Power: Annotated[float, Field(ge=0.0, default=1000.0)]
    """Design recirc water pump power for Condenser Type = EvaporativelyCooled."""

    Evaporative_Water_Supply_Tank_Name: Annotated[str, Field()]
    """If blank, water supply is from Mains."""

    Condenser_Air_Inlet_Node_Name: Annotated[str, Field()]
    """Applicable only when Heat Rejection Location is Outdoors and Condenser Type is"""

    EndUse_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""

    Refrigeration_Case_Name_or_WalkIn_Name_or_CaseAndWalkInList_Name: Annotated[str, Field()]
    """Enter the name of a Refrigeration:Case or Refrigeration:Walkin or"""

    Heat_Rejection_Zone_Name: Annotated[str, Field()]
    """This must be a controlled zone and appear in a ZoneHVAC:EquipmentConnections object."""