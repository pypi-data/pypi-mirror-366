from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac_Unitaryheatonly(EpBunch):
    """Unitary system, heating-only with constant volume supply fan (continuous or cycling)"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Unitary_System_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Unitary_System_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Supply_Air_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """A fan operating mode schedule value of 0 indicates cycling fan mode (supply air"""

    Maximum_Supply_Air_Temperature: Annotated[float, Field(default=80.0)]

    Heating_Supply_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """This value should be > 0 and <= than the fan air flow rate."""

    Controlling_Zone_Or_Thermostat_Location: Annotated[str, Field(default=...)]

    Supply_Fan_Object_Type: Annotated[Literal['Fan:OnOff', 'Fan:ConstantVolume'], Field(default=...)]
    """Fan:ConstantVolume only works with continuous fan operating mode (i.e. fan"""

    Supply_Fan_Name: Annotated[str, Field(default=...)]

    Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='BlowThrough')]

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:Fuel', 'Coil:Heating:Electric', 'Coil:Heating:Water', 'Coil:Heating:Steam'], Field(default=...)]
    """works with gas, electric, hot water and steam heating coils"""

    Heating_Coil_Name: Annotated[str, Field(default=...)]