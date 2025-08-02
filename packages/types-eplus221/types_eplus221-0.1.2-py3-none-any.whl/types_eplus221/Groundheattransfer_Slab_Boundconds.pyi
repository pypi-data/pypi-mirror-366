from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Slab_Boundconds(EpBunch):
    """Supplies some of the boundary conditions used in the ground heat transfer calculations."""

    EVTR_Is_surface_evapotranspiration_modeled: Annotated[Literal['TRUE', 'FALSE'], Field(default=...)]
    """This field specifies whether or not to use the evapotransporation model."""

    FIXBC_is_the_lower_boundary_at_a_fixed_temperature: Annotated[Literal['TRUE', 'FALSE'], Field(default=...)]
    """This field permits using a fixed temperature at the lower surface of the model"""

    TDEEPin: Annotated[str, Field()]
    """User input lower boundary temperature if FIXBC is TRUE"""

    USRHflag_Is_the_ground_surface_h_specified_by_the_user: Annotated[Literal['TRUE', 'FALSE'], Field(default=...)]
    """This field flags the use of a user specified heat transfer coefficient"""

    USERH_User_specified_ground_surface_heat_transfer_coefficient: Annotated[str, Field()]
    """Used only if USRHflag is TRUE and the heat transfer coefficient value is"""