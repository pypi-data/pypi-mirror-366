from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Complexfenestrationproperty_Solarabsorbedlayers(EpBunch):
    """Used to provide solar radiation absorbed in fenestration layers. References surface-construction pair"""

    Name: Annotated[str, Field(default=...)]

    Fenestration_Surface: Annotated[str, Field(default=...)]

    Construction_Name: Annotated[str, Field(default=...)]

    Layer_1_Solar_Radiation_Absorbed_Schedule_Name: Annotated[str, Field(default=...)]
    """Values in schedule are expected to be in W/m2"""

    Layer_2_Solar_Radiation_Absorbed_Schedule_Name: Annotated[str, Field()]
    """Values in schedule are expected to be in W/m2"""

    Layer_3_Solar_Radiation_Absorbed_Schedule_Name: Annotated[str, Field()]
    """Values in schedule are expected to be in W/m2"""

    Layer_4_Solar_Radiation_Absorbed_Schedule_Name: Annotated[str, Field()]
    """Values in schedule are expected to be in W/m2"""

    Layer_5_Solar_Radiation_Absorbed_Schedule_Name: Annotated[str, Field()]
    """Values in schedule are expected to be in W/m2"""