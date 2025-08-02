from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_Plant_Boiler_Objectreference(EpBunch):
    """This object references a detailed boiler object and adds it to"""

    Name: Annotated[str, Field(default=...)]
    """The name of this object."""

    Boiler_Object_Type: Annotated[Literal['Boiler:HotWater'], Field(default='Boiler:HotWater')]

    Boiler_Name: Annotated[str, Field(default=...)]
    """The name of the detailed boiler object."""

    Priority: Annotated[str, Field()]
    """If Hot Water Plant Operation Scheme Type=Default"""

    Template_Plant_Loop_Type: Annotated[Literal['HotWater', 'MixedWater'], Field()]
    """Specifies if this boiler serves a template hot water loop or mixed water loop"""