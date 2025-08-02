from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_Plant_Tower_Objectreference(EpBunch):
    """This object references a detailed cooling tower object and adds it to"""

    Name: Annotated[str, Field(default=...)]
    """The name of this object."""

    Cooling_Tower_Object_Type: Annotated[Literal['CoolingTower:SingleSpeed', 'CoolingTower:TwoSpeed', 'CoolingTower:VariableSpeed'], Field(default='CoolingTower:SingleSpeed')]

    Cooling_Tower_Name: Annotated[str, Field(default=...)]
    """The name of the detailed cooling tower object."""

    Priority: Annotated[str, Field()]
    """If Condenser Plant Operation Scheme Type=Default"""

    Template_Plant_Loop_Type: Annotated[Literal['ChilledWater', 'MixedWater'], Field()]
    """Specifies if this tower serves a template chilled water loop or mixed water loop"""