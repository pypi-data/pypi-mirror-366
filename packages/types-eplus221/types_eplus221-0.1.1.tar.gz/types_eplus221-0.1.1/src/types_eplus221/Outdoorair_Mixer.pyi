from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Outdoorair_Mixer(EpBunch):
    """Outdoor air mixer. Node names cannot be duplicated within a single OutdoorAir:Mixer"""

    Name: Annotated[str, Field(default=...)]

    Mixed_Air_Node_Name: Annotated[str, Field(default=...)]
    """Name of Mixed Air Node"""

    Outdoor_Air_Stream_Node_Name: Annotated[str, Field(default=...)]
    """Name of Outdoor Air Stream Node"""

    Relief_Air_Stream_Node_Name: Annotated[str, Field(default=...)]
    """Name of Relief Air Stream Node"""

    Return_Air_Stream_Node_Name: Annotated[str, Field(default=...)]
    """Name of Return Air Stream Node"""