from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coilsystem_Heating_Dx(EpBunch):
    """Virtual container component that consists of a DX heating coil (heat pump) and its"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:DX:SingleSpeed', 'Coil:Heating:DX:VariableSpeed'], Field(default=...)]

    Heating_Coil_Name: Annotated[str, Field(default=...)]