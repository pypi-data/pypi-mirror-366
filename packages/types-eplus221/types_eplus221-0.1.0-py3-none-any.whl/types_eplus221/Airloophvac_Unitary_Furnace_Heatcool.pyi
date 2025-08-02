from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac_Unitary_Furnace_Heatcool(EpBunch):
    """Unitary system, heating and cooling with constant volume supply fan (continuous or"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Furnace_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Furnace_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Supply_Air_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """A fan operating mode schedule value of 0 indicates cycling fan mode (supply air"""

    Maximum_Supply_Air_Temperature: Annotated[float, Field(default=80.0)]

    Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Must be less than or equal to the fan's maximum flow rate."""

    Heating_Supply_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Must be less than or equal to the fan's maximum flow fate."""

    No_Load_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Must be less than or equal to the fan's maximum flow rate."""

    Controlling_Zone_Or_Thermostat_Location: Annotated[str, Field(default=...)]

    Supply_Fan_Object_Type: Annotated[Literal['Fan:OnOff', 'Fan:ConstantVolume'], Field(default=...)]
    """Fan:ConstantVolume only works with continuous fan operating mode (i.e. supply"""

    Supply_Fan_Name: Annotated[str, Field(default=...)]

    Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='BlowThrough')]

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:Fuel', 'Coil:Heating:Electric', 'Coil:Heating:Water', 'Coil:Heating:Steam'], Field(default=...)]
    """works with gas, electric, hot water and steam heating coils"""

    Heating_Coil_Name: Annotated[str, Field(default=...)]

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:DX:SingleSpeed', 'CoilSystem:Cooling:DX:HeatExchangerAssisted'], Field(default=...)]
    """Only works with DX cooling coil types"""

    Cooling_Coil_Name: Annotated[str, Field(default=...)]

    Dehumidification_Control_Type: Annotated[Literal['None', 'Multimode', 'CoolReheat'], Field()]
    """None = meet sensible load only"""

    Reheat_Coil_Object_Type: Annotated[Literal['Coil:Heating:Fuel', 'Coil:Heating:Electric', 'Coil:Heating:Desuperheater', 'Coil:Heating:Water', 'Coil:Heating:Steam'], Field()]
    """Only required if dehumidification control type is "CoolReheat""""

    Reheat_Coil_Name: Annotated[str, Field()]
    """Only required if dehumidification control type is "CoolReheat""""