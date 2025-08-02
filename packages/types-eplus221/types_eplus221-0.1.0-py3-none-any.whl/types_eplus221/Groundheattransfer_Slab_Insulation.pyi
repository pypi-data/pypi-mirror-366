from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Slab_Insulation(EpBunch):
    """This object supplies the information about insulation used around the slab."""

    Rins__R_Value_Of_Under_Slab_Insulation: Annotated[str, Field(default='0.0')]
    """This field provides the thermal resistance value"""

    Dins__Width_Of_Strip_Of_Under_Slab_Insulation: Annotated[str, Field(default='0.0')]
    """This specifies the width of the perimeter strip of insulation"""

    Rvins__R_Value_Of_Vertical_Insulation: Annotated[str, Field(default='0.0')]
    """This field specifies the thermal resistance of the vertical"""

    Zvins__Depth_Of_Vertical_Insulation: Annotated[str, Field(default='0')]
    """This field specifies the depth of the vertical insulation"""

    Ivins__Flag__Is_There_Vertical_Insulation: Annotated[Literal['0', '1'], Field(default='0')]
    """Specifies if the vertical insulation configuration is being used."""