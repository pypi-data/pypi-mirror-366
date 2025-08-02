from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Constructions(EpBunch):
    """Adds a report to the eio output file which shows details for each construction,"""

    Details_Type_1: Annotated[Literal['Constructions', 'Materials'], Field()]

    Details_Type_2: Annotated[Literal['Constructions', 'Materials'], Field()]