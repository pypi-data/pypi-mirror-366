from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Construction_Cfactorundergroundwall(EpBunch):
    """Alternate method of describing underground wall constructions"""

    Name: Annotated[str, Field(default=...)]

    C_Factor: Annotated[float, Field(default=..., gt=0.0)]
    """Enter C-Factor without film coefficients or soil"""

    Height: Annotated[float, Field(default=..., gt=0.0)]
    """Enter height of the underground wall"""