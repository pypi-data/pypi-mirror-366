from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Waterheater_Heatpump_Wrappedcondenser(EpBunch):
    """This object models an air-source heat pump for water heating where the heating coil is wrapped around"""

    Name: Annotated[str, Field(default=...)]
    """Unique name for this instance of a heat pump water heater."""

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Compressor_Setpoint_Temperature_Schedule_Name: Annotated[str, Field(default=...)]
    """Defines the cut-out temperature where the heat pump compressor turns off."""

    Dead_Band_Temperature_Difference: Annotated[float, Field(gt=0.0, le=20, default=5.0)]
    """Setpoint temperature minus the dead band temperature difference defines"""

    Condenser_Bottom_Location: Annotated[float, Field(ge=0, default=0)]
    """Distance from the bottom of the tank to the bottom of the wrapped condenser."""

    Condenser_Top_Location: Annotated[float, Field(default=..., ge=0)]
    """Distance from the bottom of the tank to the top of the wrapped condenser."""

    Evaporator_Air_Flow_Rate: Annotated[float, Field(gt=0)]
    """Actual air flow rate across the heat pump's air coil (evaporator)."""

    Inlet_Air_Configuration: Annotated[Literal['Schedule', 'ZoneAirOnly', 'OutdoorAirOnly', 'ZoneAndOutdoorAir'], Field(default=...)]
    """Defines the configuration of the airflow path through the air coil and fan section."""

    Air_Inlet_Node_Name: Annotated[str, Field()]
    """Zone air exhaust node name if Inlet Air Configuration is ZoneAirOnly or"""

    Air_Outlet_Node_Name: Annotated[str, Field()]
    """Zone Air Inlet Node Name if Inlet Air Configuration is ZoneAirOnly or"""

    Outdoor_Air_Node_Name: Annotated[str, Field()]
    """Outdoor air node name if inlet air configuration is ZoneAndOutdoorAir"""

    Exhaust_Air_Node_Name: Annotated[str, Field()]
    """Simply a unique Node Name if Inlet Air Configuration is ZoneAndOutdoorAir"""

    Inlet_Air_Temperature_Schedule_Name: Annotated[str, Field()]
    """Used only if Inlet Air Configuration is Schedule, otherwise leave blank."""

    Inlet_Air_Humidity_Schedule_Name: Annotated[str, Field()]
    """Used only if Inlet Air Configuration is Schedule, otherwise leave blank."""

    Inlet_Air_Zone_Name: Annotated[str, Field()]
    """Used only if Inlet Air Configuration is ZoneAirOnly or ZoneAndOutdoorAir."""

    Tank_Object_Type: Annotated[Literal['WaterHeater:Stratified'], Field(default='WaterHeater:Stratified')]
    """Specify the type of water heater tank used by this heat pump water heater."""

    Tank_Name: Annotated[str, Field(default=...)]
    """Needs to match the name used in the corresponding Water Heater object."""

    Tank_Use_Side_Inlet_Node_Name: Annotated[str, Field()]
    """Used only when the heat pump water heater is connected to a plant loop,"""

    Tank_Use_Side_Outlet_Node_Name: Annotated[str, Field()]
    """Used only when the heat pump water heater is connected to a plant loop,"""

    DX_Coil_Object_Type: Annotated[Literal['Coil:WaterHeating:AirToWaterHeatPump:Wrapped'], Field(default='Coil:WaterHeating:AirToWaterHeatPump:Wrapped')]
    """Specify the type of DX coil used by this heat pump water heater. The only"""

    DX_Coil_Name: Annotated[str, Field(default=...)]
    """Must match the name used in the corresponding Coil:WaterHeating:AirToWaterHeatPump:Wrapped object."""

    Minimum_Inlet_Air_Temperature_for_Compressor_Operation: Annotated[float, Field(default=10)]
    """Heat pump compressor will not operate when the inlet air dry-bulb temperature"""

    Maximum_Inlet_Air_Temperature_for_Compressor_Operation: Annotated[float, Field(ge=26, le=94, default=48.88888888889)]
    """Heat pump compressor will not operate when the inlet air dry-bulb temperature"""

    Compressor_Location: Annotated[Literal['Schedule', 'Zone', 'Outdoors'], Field(default=...)]
    """If Zone is selected, Inlet Air Configuration must be ZoneAirOnly or"""

    Compressor_Ambient_Temperature_Schedule_Name: Annotated[str, Field()]
    """Used only if Compressor Location is Schedule, otherwise leave field blank."""

    Fan_Object_Type: Annotated[Literal['Fan:OnOff', 'Fan:SystemModel'], Field(default='Fan:OnOff')]
    """Specify the type of fan used by this heat pump water heater. The only"""

    Fan_Name: Annotated[str, Field(default=...)]
    """Needs to match the name used in the corresponding Fan:SystemModel or Fan:OnOff object."""

    Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='DrawThrough')]
    """BlowThrough means the fan is located before the air coil (upstream)."""

    On_Cycle_Parasitic_Electric_Load: Annotated[float, Field(ge=0.0, default=0.0)]
    """Parasitic electric power consumed when the heat pump compressor operates."""

    Off_Cycle_Parasitic_Electric_Load: Annotated[float, Field(ge=0.0, default=0.0)]
    """Parasitic electric power consumed when the heat pump compressor is off."""

    Parasitic_Heat_Rejection_Location: Annotated[Literal['Zone', 'Outdoors'], Field(default='Outdoors')]
    """This field determines if the parasitic electric load impacts the zone air"""

    Inlet_Air_Mixer_Node_Name: Annotated[str, Field()]
    """Required only if Inlet Air Configuration is ZoneAndOutdoorAir, otherwise"""

    Outlet_Air_Splitter_Node_Name: Annotated[str, Field()]
    """Required only if Inlet Air Configuration is ZoneAndOutdoorAir, otherwise"""

    Inlet_Air_Mixer_Schedule_Name: Annotated[str, Field()]
    """Required only if Inlet Air Configuration is ZoneAndOutdoorAir, otherwise"""

    Tank_Element_Control_Logic: Annotated[Literal['MutuallyExclusive', 'Simultaneous'], Field(default='Simultaneous')]
    """MutuallyExclusive means that once the tank heating element is active the"""

    Control_Sensor_1_Height_In_Stratified_Tank: Annotated[float, Field(ge=0.0)]
    """Used to indicate height of control sensor if Tank Object Type is WaterHeater:Stratified"""

    Control_Sensor_1_Weight: Annotated[str, Field(default='1.0')]
    """Weight to give Control Sensor 1 temperature"""

    Control_Sensor_2_Height_In_Stratified_Tank: Annotated[float, Field(ge=0.0)]
    """Used to indicate height of control sensor if Tank Object Type is WaterHeater:Stratified"""