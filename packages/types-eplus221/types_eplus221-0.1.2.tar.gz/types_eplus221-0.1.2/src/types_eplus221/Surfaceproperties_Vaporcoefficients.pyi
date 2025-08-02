from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceproperties_Vaporcoefficients(EpBunch):
    """The interior and external vapor transfer coefficients."""

    Surface_Name: Annotated[str, Field(default=...)]

    Constant_External_Vapor_Transfer_Coefficient: Annotated[Literal['Yes', 'No'], Field(default='No')]

    External_Vapor_Coefficient_Value: Annotated[str, Field(default='0')]

    Constant_Internal_vapor_Transfer_Coefficient: Annotated[Literal['Yes', 'No'], Field(default='No')]

    Internal_Vapor_Coefficient_Value: Annotated[str, Field(default='0')]