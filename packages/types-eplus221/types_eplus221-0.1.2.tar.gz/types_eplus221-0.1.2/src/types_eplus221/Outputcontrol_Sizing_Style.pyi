from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Outputcontrol_Sizing_Style(EpBunch):
    """Default style for the Sizing output files is comma -- this works well for"""

    Column_Separator: Annotated[Literal['Comma', 'Tab', 'Fixed'], Field(default=...)]