from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_Plant_Chiller_Objectreference(EpBunch):
    """This object references a detailed chiller object and adds it to"""

    Name: Annotated[str, Field(default=...)]
    """The name of this object."""

    Chiller_Object_Type: Annotated[Literal['Chiller:Electric:EIR', 'Chiller:Electric:ReformulatedEIR'], Field(default='Chiller:Electric:EIR')]

    Chiller_Name: Annotated[str, Field(default=...)]
    """The name of the detailed chiller object."""

    Priority: Annotated[str, Field()]
    """If Chiller Plant Operation Scheme Type=Default"""