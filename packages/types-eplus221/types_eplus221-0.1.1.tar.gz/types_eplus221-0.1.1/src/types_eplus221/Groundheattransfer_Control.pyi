from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Control(EpBunch):
    """Object determines if the Slab and Basement preprocessors"""

    Name: Annotated[str, Field()]
    """This field is included for consistency.11"""

    Run_Basement_Preprocessor: Annotated[Literal['Yes', 'No'], Field(default='No')]

    Run_Slab_Preprocessor: Annotated[Literal['Yes', 'No'], Field(default='No')]