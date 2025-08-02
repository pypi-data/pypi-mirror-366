from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Fluidproperties_Glycolconcentration(EpBunch):
    """glycol and what concentration it is"""

    Name: Annotated[str, Field(default=...)]

    Glycol_Type: Annotated[Literal['EthyleneGlycol', 'PropyleneGlycol', 'UserDefinedGlycolType'], Field(default=...)]
    """or UserDefined Fluid (must show up as a glycol in FluidProperties:Name object)"""

    User_Defined_Glycol_Name: Annotated[str, Field()]

    Glycol_Concentration: Annotated[float, Field(ge=0.0, le=1.0)]