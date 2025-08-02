from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Slab_Insulation(EpBunch):
    """This object supplies the information about insulation used around the slab."""

    RINS_R_value_of_under_slab_insulation: Annotated[str, Field(default='0.0')]
    """This field provides the thermal resistance value"""

    DINS_Width_of_strip_of_under_slab_insulation: Annotated[str, Field(default='0.0')]
    """This specifies the width of the perimeter strip of insulation"""

    RVINS_R_value_of_vertical_insulation: Annotated[str, Field(default='0.0')]
    """This field specifies the thermal resistance of the vertical"""

    ZVINS_Depth_of_vertical_insulation: Annotated[str, Field(default='0')]
    """This field specifies the depth of the vertical insulation"""

    IVINS_Flag_Is_there_vertical_insulation: Annotated[Literal['0', '1'], Field(default='0')]
    """Specifies if the vertical insulation configuration is being used."""