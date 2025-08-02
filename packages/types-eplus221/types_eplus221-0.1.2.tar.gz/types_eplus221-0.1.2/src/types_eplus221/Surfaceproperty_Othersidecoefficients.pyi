from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceproperty_Othersidecoefficients(EpBunch):
    """This object sets the other side conditions for a surface in a variety of ways."""

    Name: Annotated[str, Field(default=...)]

    Combined_ConvectiveRadiative_Film_Coefficient: Annotated[float, Field(default=...)]
    """if>0, this field becomes the exterior convective/radiative film coefficient"""

    Constant_Temperature: Annotated[float, Field(default=0)]
    """This parameter will be overwritten by the values from the Constant Temperature Schedule Name (below) if one is present"""

    Constant_Temperature_Coefficient: Annotated[str, Field(default='1')]
    """This coefficient is used even with a Schedule. It should normally be 1.0 in that case."""

    External_DryBulb_Temperature_Coefficient: Annotated[float, Field(default=0)]

    Ground_Temperature_Coefficient: Annotated[float, Field(default=0)]

    Wind_Speed_Coefficient: Annotated[float, Field(default=0)]

    Zone_Air_Temperature_Coefficient: Annotated[float, Field(default=0)]

    Constant_Temperature_Schedule_Name: Annotated[str, Field()]
    """Name of schedule for values of constant temperature."""

    Sinusoidal_Variation_of_Constant_Temperature_Coefficient: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Optionally used to vary Constant Temperature Coefficient with unitary sine wave"""

    Period_of_Sinusoidal_Variation: Annotated[float, Field(gt=0, default=24)]
    """Use with sinusoidal variation to define the time period"""

    Previous_Other_Side_Temperature_Coefficient: Annotated[float, Field(default=0)]
    """This coefficient multiplies the other side temperature result from the"""

    Minimum_Other_Side_Temperature_Limit: Annotated[float, Field()]
    """This field specifies a lower limit for the other side temperature result."""

    Maximum_Other_Side_Temperature_Limit: Annotated[float, Field()]
    """This field specifies an upper limit for the other side temperature result."""