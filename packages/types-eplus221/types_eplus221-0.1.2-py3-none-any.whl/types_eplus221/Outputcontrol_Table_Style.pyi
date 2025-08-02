from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Outputcontrol_Table_Style(EpBunch):
    """default style for the OutputControl:Table:Style is comma -- this works well for"""

    Column_Separator: Annotated[Literal['Comma', 'Tab', 'Fixed', 'HTML', 'XML', 'CommaAndHTML', 'CommaAndXML', 'TabAndHTML', 'XMLandHTML', 'All'], Field(default='Comma')]

    Unit_Conversion: Annotated[Literal['None', 'JtoKWH', 'JtoMJ', 'JtoGJ', 'InchPound'], Field()]