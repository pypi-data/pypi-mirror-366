from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceproperty_Othersideconditionsmodel(EpBunch):
    """This object sets up modifying the other side conditions for a surface from other model results."""

    Name: Annotated[str, Field(default=...)]

    Type_of_Modeling: Annotated[Literal['GapConvectionRadiation', 'UndergroundPipingSystemSurface', 'GroundCoupledSurface', 'ConvectiveUnderwater'], Field(default='GapConvectionRadiation')]
    """GapConvectionRadiation provides boundary conditions for convection"""