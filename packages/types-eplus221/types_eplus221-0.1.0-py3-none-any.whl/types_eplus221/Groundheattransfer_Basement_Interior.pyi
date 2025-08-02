from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Interior(EpBunch):
    """Provides the information needed to simulate the inside boundary conditions for"""

    Cond__Flag__Is_The_Basement_Conditioned_: Annotated[Literal['TRUE', 'FALSE'], Field(default='TRUE')]
    """for EnergyPlus this should be TRUE"""

    Hin__Downward_Convection_Only_Heat_Transfer_Coefficient: Annotated[str, Field(default='0.92')]

    Hin__Upward_Convection_Only_Heat_Transfer_Coefficient: Annotated[str, Field(default='4.04')]

    Hin__Horizontal_Convection_Only_Heat_Transfer_Coefficient: Annotated[str, Field(default='3.08')]

    Hin__Downward_Combined__Convection_And_Radiation__Heat_Transfer_Coefficient: Annotated[str, Field(default='6.13')]

    Hin__Upward_Combined__Convection_And_Radiation__Heat_Transfer_Coefficient: Annotated[str, Field(default='9.26')]

    Hin__Horizontal_Combined__Convection_And_Radiation__Heat_Transfer_Coefficient: Annotated[str, Field(default='8.29')]