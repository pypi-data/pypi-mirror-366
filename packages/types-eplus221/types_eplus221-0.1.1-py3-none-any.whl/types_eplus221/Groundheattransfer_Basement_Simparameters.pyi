from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Simparameters(EpBunch):
    """Specifies certain parameters that control the Basement preprocessor ground heat"""

    F__Multiplier_For_The_Adi_Solution: Annotated[str, Field()]
    """0<F<1.0,"""

    Iyrs__Maximum_Number_Of_Yearly_Iterations_: Annotated[str, Field(default='15')]
    """typically 15-30]"""