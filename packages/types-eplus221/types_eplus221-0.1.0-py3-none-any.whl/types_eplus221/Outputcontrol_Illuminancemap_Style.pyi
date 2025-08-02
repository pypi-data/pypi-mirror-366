from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Outputcontrol_Illuminancemap_Style(EpBunch):
    """default style for the Daylighting Illuminance Map is comma -- this works well for"""

    Column_Separator: Annotated[Literal['Comma', 'Tab', 'Fixed'], Field(default='Comma')]