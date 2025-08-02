from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Simparameters(EpBunch):
    """Specifies certain parameters that control the Basement preprocessor ground heat"""

    F_Multiplier_for_the_ADI_solution: Annotated[str, Field()]
    """0<F<1.0,"""

    IYRS_Maximum_number_of_yearly_iterations: Annotated[str, Field(default='15')]
    """typically 15-30]"""