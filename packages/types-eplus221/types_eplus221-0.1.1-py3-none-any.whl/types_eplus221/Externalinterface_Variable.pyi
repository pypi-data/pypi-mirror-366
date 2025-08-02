from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Externalinterface_Variable(EpBunch):
    """This input object is similar to EnergyManagementSystem:GlobalVariable. However, at"""

    Name: Annotated[str, Field(default=...)]
    """This name becomes a variable for use in Erl programs"""

    Initial_Value: Annotated[float, Field(default=...)]
    """Used during warm-up and system sizing."""