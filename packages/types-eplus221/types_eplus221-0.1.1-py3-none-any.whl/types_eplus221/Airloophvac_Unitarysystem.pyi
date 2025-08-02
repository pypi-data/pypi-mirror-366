from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac_Unitarysystem(EpBunch):
    """AirloopHVAC:UnitarySystem is a generic HVAC system type that allows any"""

    Name: Annotated[str, Field(default=...)]
    """Unique name for the Unitary System."""

    Control_Type: Annotated[Literal['Load', 'SetPoint', 'SingleZoneVAV'], Field(default='Load')]
    """Load control requires a Controlling Zone name."""

    Controlling_Zone_Or_Thermostat_Location: Annotated[str, Field()]
    """Used only for Load based control"""

    Dehumidification_Control_Type: Annotated[Literal['None', 'Multimode', 'CoolReheat'], Field()]
    """None = meet sensible load only. Required when Control Type = SingleZoneVAV."""

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Enter the node name used as the inlet air node for the unitary system."""

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """Enter the node name used as the outlet air node for the unitary system."""

    Supply_Fan_Object_Type: Annotated[Literal['Fan:SystemModel', 'Fan:OnOff', 'Fan:ConstantVolume', 'Fan:VariableVolume', 'Fan:ComponentModel'], Field()]
    """Enter the type of supply air fan if included in the unitary system."""

    Supply_Fan_Name: Annotated[str, Field()]
    """Enter the name of the supply air fan if included in the unitary system."""

    Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field()]
    """Enter the type of supply air fan if included in the unitary system."""

    Supply_Air_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """A fan operating mode schedule value of 0 indicates cycling fan mode (supply air"""

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:DX:SingleSpeed', 'Coil:Heating:DX:MultiSpeed', 'Coil:Heating:DX:VariableSpeed', 'Coil:Heating:WaterToAirHeatPump:ParameterEstimation', 'Coil:Heating:WaterToAirHeatPump:EquationFit', 'Coil:Heating:WaterToAirHeatPump:VariableSpeedEquationFit', 'Coil:Heating:Fuel', 'Coil:Heating:Gas:MultiStage', 'Coil:Heating:Electric', 'Coil:Heating:Electric:MultiStage', 'Coil:Heating:Water', 'Coil:Heating:Steam', 'Coil:Heating:Desuperheater', 'Coil:UserDefined'], Field()]
    """Enter the type of heating coil if included in the unitary system."""

    Heating_Coil_Name: Annotated[str, Field()]
    """Enter the name of the heating coil if included in the unitary system."""

    Dx_Heating_Coil_Sizing_Ratio: Annotated[float, Field(gt=0, default=1.0)]
    """Used to adjust heat pump heating capacity with respect to DX cooling capacity"""

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:DX:SingleSpeed', 'Coil:Cooling:DX:TwoSpeed', 'Coil:Cooling:DX:MultiSpeed', 'Coil:Cooling:DX:VariableSpeed', 'Coil:Cooling:DX:TwoStageWithHumidityControlMode', 'Coil:Cooling:DX:SingleSpeed:ThermalStorage', 'CoilSystem:Cooling:DX:HeatExchangerAssisted', 'Coil:Cooling:WaterToAirHeatPump:ParameterEstimation', 'Coil:Cooling:WaterToAirHeatPump:EquationFit', 'Coil:Cooling:WaterToAirHeatPump:VariableSpeedEquationFit', 'Coil:Cooling:Water', 'Coil:Cooling:Water:DetailedGeometry', 'CoilSystem:Cooling:Water:HeatExchangerAssisted', 'Coil:UserDefined'], Field()]
    """Enter the type of cooling coil if included in the unitary system."""

    Cooling_Coil_Name: Annotated[str, Field()]
    """Enter the name of the cooling coil if included in the unitary system."""

    Use_Doas_Dx_Cooling_Coil: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """If Yes, the DX cooling coil runs as 100% DOAS DX coil."""

    Minimum_Supply_Air_Temperature: Annotated[float, Field(ge=0.0, le=20.0, default=2.0)]
    """When Use DOAS DX Cooling Coil is specified as Yes, Minimum Supply Air Temperature"""

    Latent_Load_Control: Annotated[Literal['SensibleOnlyLoadControl', 'LatentOnlyLoadControl', 'LatentWithSensibleLoadControl', 'LatentOrSensibleLoadControl'], Field(default='SensibleOnlyLoadControl')]
    """SensibleOnlyLoadControl is selected when thermostat or SingleZoneVAV control is used."""

    Supplemental_Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:Fuel', 'Coil:Heating:Electric', 'Coil:Heating:Desuperheater', 'Coil:Heating:Water', 'Coil:Heating:Steam', 'Coil:UserDefined'], Field()]
    """Enter the type of supplemental heating or reheat coil if included in the unitary system."""

    Supplemental_Heating_Coil_Name: Annotated[str, Field()]
    """Enter the name of the supplemental heating coil if included in the unitary system."""

    Cooling_Supply_Air_Flow_Rate_Method: Annotated[Literal['None', 'SupplyAirFlowRate', 'FlowPerFloorArea', 'FractionOfAutosizedCoolingValue', 'FlowPerCoolingCapacity'], Field()]
    """Enter the method used to determine the cooling supply air volume flow rate."""

    Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Enter the magnitude of the supply air volume flow rate during cooling operation."""

    Cooling_Supply_Air_Flow_Rate_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate per total floor area fraction."""

    Cooling_Fraction_Of_Autosized_Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate as a fraction of the cooling supply air flow rate."""

    Cooling_Supply_Air_Flow_Rate_Per_Unit_Of_Capacity: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate as a fraction of the cooling capacity."""

    Heating_Supply_Air_Flow_Rate_Method: Annotated[Literal['None', 'SupplyAirFlowRate', 'FlowPerFloorArea', 'FractionOfAutosizedHeatingValue', 'FlowPerHeatingCapacity'], Field()]
    """Enter the method used to determine the heating supply air volume flow rate."""

    Heating_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Enter the magnitude of the supply air volume flow rate during heating operation."""

    Heating_Supply_Air_Flow_Rate_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate per total floor area fraction."""

    Heating_Fraction_Of_Autosized_Heating_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate as a fraction of the heating supply air flow rate."""

    Heating_Supply_Air_Flow_Rate_Per_Unit_Of_Capacity: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate as a fraction of the heating capacity."""

    No_Load_Supply_Air_Flow_Rate_Method: Annotated[Literal['None', 'SupplyAirFlowRate', 'FlowPerFloorArea', 'FractionOfAutosizedCoolingValue', 'FractionOfAutosizedHeatingValue', 'FlowPerCoolingCapacity', 'FlowPerHeatingCapacity'], Field()]
    """Enter the method used to determine the supply air volume flow rate when no cooling or heating is required."""

    No_Load_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Enter the magnitude of the supply air volume flow rate during when no cooling or heating is required."""

    No_Load_Supply_Air_Flow_Rate_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate per total floor area fraction."""

    No_Load_Fraction_Of_Autosized_Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate as a fraction of the cooling supply air flow rate."""

    No_Load_Fraction_Of_Autosized_Heating_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate as a fraction of the heating supply air flow rate."""

    No_Load_Supply_Air_Flow_Rate_Per_Unit_Of_Capacity_During_Cooling_Operation: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate as a fraction of the cooling capacity."""

    No_Load_Supply_Air_Flow_Rate_Per_Unit_Of_Capacity_During_Heating_Operation: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate as a fraction of the heating capacity."""

    Maximum_Supply_Air_Temperature: Annotated[float, Field(default=80.0)]
    """Enter the maximum supply air temperature leaving the heating coil."""

    Maximum_Outdoor_Dry_Bulb_Temperature_For_Supplemental_Heater_Operation: Annotated[float, Field(default=21.0)]
    """Enter the maximum outdoor dry-bulb temperature for supplemental heater operation."""

    Outdoor_Dry_Bulb_Temperature_Sensor_Node_Name: Annotated[str, Field()]
    """If this field is blank, outdoor temperature from the weather file is used."""

    Maximum_Cycling_Rate: Annotated[float, Field(ge=0.0, le=5.0, default=2.5)]
    """Used only for water source heat pump."""

    Heat_Pump_Time_Constant: Annotated[float, Field(ge=0.0, le=500.0, default=60.0)]
    """Used only for water source heat pump."""

    Fraction_Of_On_Cycle_Power_Use: Annotated[float, Field(ge=0.0, le=0.05, default=0.01)]
    """Used only for water source heat pump."""

    Heat_Pump_Fan_Delay_Time: Annotated[float, Field(ge=0.0, default=60)]
    """Used only for water source heat pump."""

    Ancillary_On_Cycle_Electric_Power: Annotated[float, Field(ge=0, default=0)]
    """Enter the value of ancillary electric power for controls or other devices consumed during the on cycle."""

    Ancillary_Off_Cycle_Electric_Power: Annotated[float, Field(ge=0, default=0)]
    """Enter the value of ancillary electric power for controls or other devices consumed during the off cycle."""

    Design_Heat_Recovery_Water_Flow_Rate: Annotated[float, Field(ge=0.0, default=0.0)]
    """If non-zero, then the heat recovery inlet and outlet node names must be entered."""

    Maximum_Temperature_For_Heat_Recovery: Annotated[float, Field(ge=0.0, le=100.0, default=80.0)]
    """Enter the maximum heat recovery inlet temperature allowed for heat recovery."""

    Heat_Recovery_Water_Inlet_Node_Name: Annotated[str, Field()]
    """Enter the name of the heat recovery water inlet node if plant water loop connections are present."""

    Heat_Recovery_Water_Outlet_Node_Name: Annotated[str, Field()]
    """Enter the name of the heat recovery water outlet node if plant water loop connections are present."""

    Design_Specification_Multispeed_Object_Type: Annotated[Literal['UnitarySystemPerformance:Multispeed'], Field()]
    """Enter the type of performance specification object used to describe the multispeed coil."""

    Design_Specification_Multispeed_Object_Name: Annotated[str, Field()]
    """Enter the name of the performance specification object used to describe the multispeed coil."""