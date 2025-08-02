from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac_Unitaryheatpump_Airtoair(EpBunch):
    """Unitary heat pump system, heating and cooling, single-speed with supply fan, direct"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Must be less than or equal to the fan's maximum flow rate."""

    Heating_Supply_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Must be less than or equal to the fan's maximum flow rate."""

    No_Load_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Must be less than or equal to the fan's maximum flow rate."""

    Controlling_Zone_Or_Thermostat_Location: Annotated[str, Field(default=...)]

    Supply_Air_Fan_Object_Type: Annotated[Literal['Fan:OnOff', 'Fan:ConstantVolume'], Field(default=...)]
    """Fan:ConstantVolume only works with continuous fan operating mode (i.e. fan"""

    Supply_Air_Fan_Name: Annotated[str, Field(default=...)]
    """Needs to match in the fan object"""

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:DX:SingleSpeed', 'Coil:Heating:DX:VariableSpeed', 'CoilSystem:IntegratedHeatPump:AirSource'], Field(default=...)]
    """Only works with Coil:Heating:DX:SingleSpeed or"""

    Heating_Coil_Name: Annotated[str, Field(default=...)]
    """Needs to match in the DX heating coil object"""

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:DX:SingleSpeed', 'Coil:Cooling:DX:VariableSpeed', 'CoilSystem:Cooling:DX:HeatExchangerAssisted', 'CoilSystem:IntegratedHeatPump:AirSource'], Field(default=...)]
    """Only works with Coil:Cooling:DX:SingleSpeed or"""

    Cooling_Coil_Name: Annotated[str, Field(default=...)]
    """Needs to match in the DX cooling coil object"""

    Supplemental_Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:Fuel', 'Coil:Heating:Electric', 'Coil:Heating:Water', 'Coil:Heating:Steam'], Field(default=...)]
    """works with gas, electric, hot water and steam heating coils"""

    Supplemental_Heating_Coil_Name: Annotated[str, Field(default=...)]
    """Needs to match in the supplemental heating coil object"""

    Maximum_Supply_Air_Temperature_From_Supplemental_Heater: Annotated[float, Field(default=...)]

    Maximum_Outdoor_Dry_Bulb_Temperature_For_Supplemental_Heater_Operation: Annotated[float, Field(le=21.0, default=21.0)]

    Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='BlowThrough')]

    Supply_Air_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """A fan operating mode schedule value of 0 indicates cycling fan mode (supply air"""

    Dehumidification_Control_Type: Annotated[Literal['None', 'Multimode', 'CoolReheat'], Field()]
    """None = meet sensible load only"""