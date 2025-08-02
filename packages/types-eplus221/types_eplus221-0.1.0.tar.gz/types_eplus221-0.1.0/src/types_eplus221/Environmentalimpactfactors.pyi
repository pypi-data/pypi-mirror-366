from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Environmentalimpactfactors(EpBunch):
    """Used to help convert district and ideal energy use to a fuel type and provide total carbon equivalent with coefficients"""

    District_Heating_Efficiency: Annotated[str, Field(default='0.3')]
    """District heating efficiency used when converted to natural gas"""

    District_Cooling_Cop: Annotated[str, Field(default='3.0')]
    """District cooling COP used when converted to electricity"""

    Steam_Conversion_Efficiency: Annotated[str, Field(default='0.25')]
    """Steam conversion efficiency used to convert steam usage to natural gas"""

    Total_Carbon_Equivalent_Emission_Factor_From_N2O: Annotated[str, Field(default='80.7272')]

    Total_Carbon_Equivalent_Emission_Factor_From_Ch4: Annotated[str, Field(default='6.2727')]

    Total_Carbon_Equivalent_Emission_Factor_From_Co2: Annotated[str, Field(default='0.2727')]