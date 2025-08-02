from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Heightvariation(EpBunch):
    """This object is used if the user requires advanced control over height-dependent"""

    Wind_Speed_Profile_Exponent: Annotated[float, Field(ge=0.0, default=0.22)]
    """Set to zero for no wind speed dependence on height."""

    Wind_Speed_Profile_Boundary_Layer_Thickness: Annotated[float, Field(gt=0.0, default=370.0)]

    Air_Temperature_Gradient_Coefficient: Annotated[float, Field(ge=0.0, default=0.0065)]
    """Set to zero for no air temperature dependence on height."""