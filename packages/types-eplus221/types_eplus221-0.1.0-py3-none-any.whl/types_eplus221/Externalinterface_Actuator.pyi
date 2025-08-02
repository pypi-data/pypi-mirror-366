from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Externalinterface_Actuator(EpBunch):
    """Hardware portion of EMS used to set up actuators in the model"""

    Name: Annotated[str, Field(default=...)]
    """This name becomes a variable for use in Erl programs"""

    Actuated_Component_Unique_Name: Annotated[str, Field(default=...)]

    Actuated_Component_Type: Annotated[str, Field(default=...)]

    Actuated_Component_Control_Type: Annotated[str, Field(default=...)]

    Optional_Initial_Value: Annotated[float, Field()]
    """If specified, it is used during warm-up and system sizing."""