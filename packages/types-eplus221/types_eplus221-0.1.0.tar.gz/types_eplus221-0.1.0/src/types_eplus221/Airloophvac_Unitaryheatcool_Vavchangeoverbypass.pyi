from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac_Unitaryheatcool_Vavchangeoverbypass(EpBunch):
    """Unitary system, heating and cooling with constant volume supply fan (continuous or"""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this unitary system."""

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Enter the system air flow rate during cooling"""

    Heating_Supply_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Enter the system air flow rate during heating"""

    No_Load_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Only used when the supply air fan operating mode is continuous (see field"""

    Cooling_Outdoor_Air_Flow_Rate: Annotated[float, Field(default=..., ge=0.0)]
    """Enter the outdoor air flow rate during"""

    Heating_Outdoor_Air_Flow_Rate: Annotated[float, Field(default=..., ge=0.0)]
    """Enter the outdoor air flow rate during"""

    No_Load_Outdoor_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Only used when the supply air fan operating mode is continuous (see field"""

    Outdoor_Air_Flow_Rate_Multiplier_Schedule_Name: Annotated[str, Field()]
    """Enter the name of a schedule that contains multipliers for the outdoor air"""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Enter the name of the unitary system's air inlet node."""

    Bypass_Duct_Mixer_Node_Name: Annotated[str, Field(default=...)]
    """Enter the name of the bypass duct mixer node. This name should be the name"""

    Bypass_Duct_Splitter_Node_Name: Annotated[str, Field(default=...)]
    """Enter the name of the bypass duct splitter node."""

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """Enter the name of the unitary system's air outlet node."""

    Outdoor_Air_Mixer_Object_Type: Annotated[Literal['OutdoorAir:Mixer'], Field(default=...)]
    """currently only one type OutdoorAir:Mixer object is available."""

    Outdoor_Air_Mixer_Name: Annotated[str, Field(default=...)]
    """Enter the name of the outdoor air mixer used with this unitary system."""

    Supply_Air_Fan_Object_Type: Annotated[Literal['Fan:SystemModel', 'Fan:OnOff', 'Fan:ConstantVolume'], Field(default=...)]
    """Specify the type of supply air fan used in this unitary system."""

    Supply_Air_Fan_Name: Annotated[str, Field(default=...)]
    """Enter the name of the supply air fan used in this unitary system."""

    Supply_Air_Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default=...)]
    """Specify supply air fan placement as either blow through or draw through."""

    Supply_Air_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """Enter the name of a schedule to control the supply air fan. Schedule Name values of zero"""

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:DX:SingleSpeed', 'Coil:Cooling:DX:VariableSpeed', 'CoilSystem:Cooling:DX:HeatExchangerAssisted', 'Coil:Cooling:DX:TwoStageWithHumidityControlMode'], Field(default=...)]
    """Specify the type of cooling coil used in this unitary system."""

    Cooling_Coil_Name: Annotated[str, Field(default=...)]
    """Enter the name of the cooling coil used in this unitary system."""

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:DX:SingleSpeed', 'Coil:Heating:DX:VariableSpeed', 'Coil:Heating:Fuel', 'Coil:Heating:Electric', 'Coil:Heating:Water', 'Coil:Heating:Steam'], Field(default=...)]
    """works with DX, gas, electric, hot water and steam heating coils"""

    Heating_Coil_Name: Annotated[str, Field(default=...)]
    """Enter the name of the heating coil used in this unitary system."""

    Priority_Control_Mode: Annotated[Literal['CoolingPriority', 'HeatingPriority', 'ZonePriority', 'LoadPriority'], Field(default='ZonePriority')]
    """CoolingPriority = system provides cooling if any zone requires cooling."""

    Minimum_Outlet_Air_Temperature_During_Cooling_Operation: Annotated[float, Field(gt=0.0, default=8.0)]
    """Specify the minimum outlet air temperature allowed for this unitary system"""

    Maximum_Outlet_Air_Temperature_During_Heating_Operation: Annotated[float, Field(gt=0.0, default=50.0)]
    """Specify the maximum outlet air temperature allowed for this unitary system"""

    Dehumidification_Control_Type: Annotated[Literal['None', 'Multimode', 'CoolReheat'], Field()]
    """None = meet sensible load only."""

    Plenum_Or_Mixer_Inlet_Node_Name: Annotated[str, Field()]
    """Enter the name of the bypass duct node connected to a plenum or mixer."""

    Minimum_Runtime_Before_Operating_Mode_Change: Annotated[float, Field(ge=0.0, default=0.25)]
    """This is the minimum amount of time the unit operates in cooling or heating mode before changing modes."""