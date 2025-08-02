from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Interior(EpBunch):
    """Provides the information needed to simulate the inside boundary conditions for"""

    COND_Flag_Is_the_basement_conditioned: Annotated[Literal['TRUE', 'FALSE'], Field(default='TRUE')]
    """for EnergyPlus this should be TRUE"""

    HIN_Downward_convection_only_heat_transfer_coefficient: Annotated[str, Field(default='0.92')]

    HIN_Upward_convection_only_heat_transfer_coefficient: Annotated[str, Field(default='4.04')]

    HIN_Horizontal_convection_only_heat_transfer_coefficient: Annotated[str, Field(default='3.08')]

    HIN_Downward_combined_convection_and_radiation_heat_transfer_coefficient: Annotated[str, Field(default='6.13')]

    HIN_Upward_combined_convection_and_radiation_heat_transfer_coefficient: Annotated[str, Field(default='9.26')]

    HIN_Horizontal_combined_convection_and_radiation_heat_transfer_coefficient: Annotated[str, Field(default='8.29')]