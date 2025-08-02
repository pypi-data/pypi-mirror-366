from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Curve_Functional_Pressuredrop(EpBunch):
    """Sets up curve information for minor loss and/or friction"""

    Name: Annotated[str, Field(default=...)]

    Diameter: Annotated[float, Field(default=..., gt=0)]
    """"D" in above expression, used to also calculate local velocity"""

    Minor_Loss_Coefficient: Annotated[float, Field(gt=0)]
    """"K" in above expression"""

    Length: Annotated[float, Field(gt=0)]
    """"L" in above expression"""

    Roughness: Annotated[float, Field(gt=0)]
    """This will be used to calculate "f" from Moody-chart approximations"""

    Fixed_Friction_Factor: Annotated[str, Field()]
    """Optional way to set a constant value for "f", instead of using"""