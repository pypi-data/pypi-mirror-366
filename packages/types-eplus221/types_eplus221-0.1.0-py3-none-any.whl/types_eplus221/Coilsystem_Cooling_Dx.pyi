from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coilsystem_Cooling_Dx(EpBunch):
    """Virtual container component that consists of a DX cooling coil and its associated"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Dx_Cooling_Coil_System_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Dx_Cooling_Coil_System_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Dx_Cooling_Coil_System_Sensor_Node_Name: Annotated[str, Field(default=...)]

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:DX:SingleSpeed', 'CoilSystem:Cooling:DX:HeatExchangerAssisted', 'Coil:Cooling:DX:TwoSpeed', 'Coil:Cooling:DX:TwoStageWithHumidityControlMode', 'Coil:Cooling:DX:VariableSpeed', 'Coil:Cooling:DX:SingleSpeed:ThermalStorage'], Field(default=...)]

    Cooling_Coil_Name: Annotated[str, Field(default=...)]

    Dehumidification_Control_Type: Annotated[Literal['None', 'Multimode', 'CoolReheat'], Field()]
    """None = meet sensible load only"""

    Run_On_Sensible_Load: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """If Yes, unit will run if there is a sensible load."""

    Run_On_Latent_Load: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """If Yes, unit will run if there is a latent load."""

    Use_Outdoor_Air_Dx_Cooling_Coil: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """This input field is designed for use with DX cooling coils with low air flow"""

    Outdoor_Air_Dx_Cooling_Coil_Leaving_Minimum_Air_Temperature: Annotated[float, Field(ge=0.0, le=7.2, default=2.0)]
    """DX cooling coil leaving minimum air temperature defines the minimum DX cooling coil"""