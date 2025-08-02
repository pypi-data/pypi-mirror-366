from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Performanceprecisiontradeoffs(EpBunch):
    """This object enables users to choose certain options that speed up EnergyPlus simulation,"""

    Use_Coil_Direct_Solutions: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """If Yes, an analytical or empirical solution will be used to replace iterations in"""