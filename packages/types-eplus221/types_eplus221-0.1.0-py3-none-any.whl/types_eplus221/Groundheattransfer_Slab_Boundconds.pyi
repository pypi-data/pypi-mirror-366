from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Slab_Boundconds(EpBunch):
    """Supplies some of the boundary conditions used in the ground heat transfer calculations."""

    Evtr__Is_Surface_Evapotranspiration_Modeled: Annotated[Literal['TRUE', 'FALSE'], Field(default=...)]
    """This field specifies whether or not to use the evapotransporation model."""

    Fixbc__Is_The_Lower_Boundary_At_A_Fixed_Temperature: Annotated[Literal['TRUE', 'FALSE'], Field(default=...)]
    """This field permits using a fixed temperature at the lower surface of the model"""

    Tdeepin: Annotated[str, Field()]
    """User input lower boundary temperature if FIXBC is TRUE"""

    Usrhflag__Is_The_Ground_Surface_H_Specified_By_The_User_: Annotated[Literal['TRUE', 'FALSE'], Field(default=...)]
    """This field flags the use of a user specified heat transfer coefficient"""

    Userh__User_Specified_Ground_Surface_Heat_Transfer_Coefficient: Annotated[str, Field()]
    """Used only if USRHflag is TRUE and the heat transfer coefficient value is"""