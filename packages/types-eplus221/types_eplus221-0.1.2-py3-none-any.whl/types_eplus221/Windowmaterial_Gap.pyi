from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowmaterial_Gap(EpBunch):
    """Used to define the gap between two layers in a complex fenestration system, where the"""

    Name: Annotated[str, Field(default=...)]

    Thickness: Annotated[float, Field(default=..., gt=0)]

    Gas_or_Gas_Mixture: Annotated[str, Field(default=...)]
    """This field should reference only WindowMaterial:Gas"""

    Pressure: Annotated[float, Field(default=101325)]

    Deflection_State: Annotated[str, Field()]
    """If left blank, it will be considered that gap is not deflected"""

    Support_Pillar: Annotated[str, Field()]
    """If left blank, it will be considered that gap does not have"""