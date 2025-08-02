from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Watertoairheatpump(EpBunch):
    """Water-to-air heat pump. Forced-convection heating-cooling unit with supply fan,"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Outdoor_Air_Mixer_Object_Type: Annotated[Literal['OutdoorAir:Mixer'], Field()]
    """Currently only one OutdoorAir:Mixer object type is available."""

    Outdoor_Air_Mixer_Name: Annotated[str, Field()]
    """If this field is blank, the OutdoorAir:Mixer is not used."""

    Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Must be less than or equal to fan size."""

    Heating_Supply_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Must be less than or equal to fan size."""

    No_Load_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0)]
    """Must be less than or equal to fan size."""

    Cooling_Outdoor_Air_Flow_Rate: Annotated[float, Field(default=..., ge=0)]
    """Must be less than or equal to supply air flow rate during cooling operation."""

    Heating_Outdoor_Air_Flow_Rate: Annotated[float, Field(default=..., ge=0)]
    """Must be less than or equal to supply air flow rate during heating operation."""

    No_Load_Outdoor_Air_Flow_Rate: Annotated[float, Field(ge=0)]
    """Only used when heat pump Fan operating mode is continuous. This air flow rate"""

    Supply_Air_Fan_Object_Type: Annotated[Literal['Fan:SystemModel', 'Fan:OnOff'], Field(default=...)]

    Supply_Air_Fan_Name: Annotated[str, Field(default=...)]
    """Needs to match Fan:SystemModel or Fan:OnOff object"""

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:WaterToAirHeatPump:EquationFit', 'Coil:Heating:WaterToAirHeatPump:VariableSpeedEquationFit'], Field(default=...)]

    Heating_Coil_Name: Annotated[str, Field(default=...)]
    """Needs to match in the water-to-air heat pump heating coil object"""

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:WaterToAirHeatPump:EquationFit', 'Coil:Cooling:WaterToAirHeatPump:VariableSpeedEquationFit'], Field(default=...)]

    Cooling_Coil_Name: Annotated[str, Field(default=...)]
    """Needs to match in the water-to-air heat pump cooling coil object"""

    Maximum_Cycling_Rate: Annotated[float, Field(ge=0.0, le=5.0, default=2.5)]
    """The maximum on-off cycling rate for the compressor"""

    Heat_Pump_Time_Constant: Annotated[float, Field(ge=0.0, le=500.0, default=60.0)]
    """Time constant for the cooling coil's capacity to reach steady state after startup"""

    Fraction_of_OnCycle_Power_Use: Annotated[str, Field(default='0.01')]
    """The fraction of on-cycle power use to adjust the part load fraction based on"""

    Heat_Pump_Fan_Delay_Time: Annotated[str, Field(default='60')]
    """Programmed time delay for heat pump fan to shut off after compressor cycle off."""

    Supplemental_Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:Fuel', 'Coil:Heating:Electric', 'Coil:Heating:Water', 'Coil:Heating:Steam'], Field(default=...)]
    """works with gas, electric, hot water and steam heating coils"""

    Supplemental_Heating_Coil_Name: Annotated[str, Field(default=...)]
    """Needs to match in the supplemental heating coil object"""

    Maximum_Supply_Air_Temperature_from_Supplemental_Heater: Annotated[float, Field(default=autosize)]
    """Supply air temperature from the supplemental heater will not exceed this value."""

    Maximum_Outdoor_DryBulb_Temperature_for_Supplemental_Heater_Operation: Annotated[float, Field(le=21.0, default=21.0)]

    Outdoor_DryBulb_Temperature_Sensor_Node_Name: Annotated[str, Field()]

    Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='BlowThrough')]

    Supply_Air_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """Enter the name of a schedule that controls fan operation. Schedule values of 0 denote"""

    Availability_Manager_List_Name: Annotated[str, Field()]
    """Enter the name of an AvailabilityManagerAssignmentList object."""

    Heat_Pump_Coil_Water_Flow_Mode: Annotated[Literal['Constant', 'Cycling', 'ConstantOnDemand'], Field(default='Cycling')]
    """used only when the heat pump coils are of the type WaterToAirHeatPump:EquationFit"""

    Design_Specification_ZoneHVAC_Sizing_Object_Name: Annotated[str, Field()]
    """Enter the name of a DesignSpecificationZoneHVACSizing object."""