from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Shadingproperty_Reflectance(EpBunch):
    """If this object is not defined for a shading surface the default values"""

    Shading_Surface_Name: Annotated[str, Field(default=...)]

    Diffuse_Solar_Reflectance_Of_Unglazed_Part_Of_Shading_Surface: Annotated[str, Field(default='0.2')]

    Diffuse_Visible_Reflectance_Of_Unglazed_Part_Of_Shading_Surface: Annotated[str, Field(default='0.2')]

    Fraction_Of_Shading_Surface_That_Is_Glazed: Annotated[str, Field(default='0.0')]

    Glazing_Construction_Name: Annotated[str, Field()]
    """Required if Fraction of Shading Surface That Is Glazed > 0.0"""