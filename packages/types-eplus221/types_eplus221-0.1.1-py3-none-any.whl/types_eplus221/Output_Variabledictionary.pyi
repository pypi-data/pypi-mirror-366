from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Variabledictionary(EpBunch):
    """Produces a list summarizing the output variables and meters that are available for"""

    Key_Field: Annotated[Literal['IDF', 'regular'], Field(default='regular')]

    Sort_Option: Annotated[Literal['Name', 'Unsorted'], Field()]