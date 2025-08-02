from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Distribution_Component_Terminalunit(EpBunch):
    """This object defines the name of a terminal unit in an air loop."""

    Terminal_Unit_Name: Annotated[str, Field(default=...)]
    """Enter the name of a terminal unit in the AirLoopHVAC."""

    Terminal_Unit_Object_Type: Annotated[Literal['AirTerminal:SingleDuct:ConstantVolume:Reheat', 'AirTerminal:SingleDuct:VAV:Reheat'], Field(default=...)]
    """Select the type of terminal unit corresponding to the name entered in the field above."""

    Air_Path_Length: Annotated[float, Field(default=..., gt=0)]
    """Enter the air path length (depth) for the terminal unit."""

    Air_Path_Hydraulic_Diameter: Annotated[float, Field(default=..., gt=0)]
    """Enter the hydraulic diameter of this terminal unit. The hydraulic diameter is"""