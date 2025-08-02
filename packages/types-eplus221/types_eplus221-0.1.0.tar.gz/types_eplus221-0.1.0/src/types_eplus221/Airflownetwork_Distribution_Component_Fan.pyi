from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Distribution_Component_Fan(EpBunch):
    """This object defines the name of the supply Air Fan used in an Air loop."""

    Fan_Name: Annotated[str, Field(default=...)]
    """Enter the name of the fan in the primary air loop."""

    Supply_Fan_Object_Type: Annotated[Literal['Fan:OnOff', 'Fan:ConstantVolume', 'Fan:VariableVolume', 'Fan:SystemModel'], Field(default='Fan:ConstantVolume')]