from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Heatbalancesettings_Conductionfinitedifference(EpBunch):
    """Determines settings for the Conduction Finite Difference"""

    Difference_Scheme: Annotated[Literal['CrankNicholsonSecondOrder', 'FullyImplicitFirstOrder'], Field(default='FullyImplicitFirstOrder')]

    Space_Discretization_Constant: Annotated[float, Field(default=3)]
    """increase or decrease number of nodes"""

    Relaxation_Factor: Annotated[float, Field(ge=0.01, le=1.0, default=1.0)]

    Inside_Face_Surface_Temperature_Convergence_Criteria: Annotated[float, Field(ge=1.0E-7, le=0.01, default=0.002)]