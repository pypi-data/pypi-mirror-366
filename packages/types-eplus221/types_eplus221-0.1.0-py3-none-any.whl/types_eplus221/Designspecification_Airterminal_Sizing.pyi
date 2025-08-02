from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Designspecification_Airterminal_Sizing(EpBunch):
    """This object is used to scale the sizing of air terminal units."""

    Name: Annotated[str, Field(default=...)]
    """This name may be referenced by a ZoneHVAC:AirDistributionUnit or AirTerminal:SingleDuct:Uncontrolled object."""

    Fraction_Of_Design_Cooling_Load: Annotated[float, Field(ge=0.0, default=1.0)]
    """The fraction of the design sensible cooling load to be met by this terminal unit."""

    Cooling_Design_Supply_Air_Temperature_Difference_Ratio: Annotated[float, Field(gt=0.0, default=1.0)]
    """This ratio adjusts the supply air temperature difference used to calculate"""

    Fraction_Of_Design_Heating_Load: Annotated[float, Field(ge=0.0, default=1.0)]
    """The fraction of the design sensible heating load to be met by this terminal unit."""

    Heating_Design_Supply_Air_Temperature_Difference_Ratio: Annotated[float, Field(gt=0.0, default=1.0)]
    """This ratio adjusts the supply air temperature difference used to calculate"""

    Fraction_Of_Minimum_Outdoor_Air_Flow: Annotated[float, Field(ge=0.0, default=1.0)]
    """The fraction of the zone minimum outdoor air requirement to be met by this terminal unit."""