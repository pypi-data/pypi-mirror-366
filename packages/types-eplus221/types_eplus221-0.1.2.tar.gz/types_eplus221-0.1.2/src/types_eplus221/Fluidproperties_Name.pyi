from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Fluidproperties_Name(EpBunch):
    """potential fluid name/type in the input file"""

    Fluid_Name: Annotated[str, Field(default=...)]

    Fluid_Type: Annotated[Literal['Refrigerant', 'Glycol'], Field(default=...)]