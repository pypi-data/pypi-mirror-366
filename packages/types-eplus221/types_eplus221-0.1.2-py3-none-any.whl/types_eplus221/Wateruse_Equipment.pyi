from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Wateruse_Equipment(EpBunch):
    """A generalized object for simulating all water end uses. Hot and cold water uses are"""

    Name: Annotated[str, Field(default=...)]

    EndUse_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""

    Peak_Flow_Rate: Annotated[float, Field(default=..., ge=0.0)]

    Flow_Rate_Fraction_Schedule_Name: Annotated[str, Field()]
    """Defaults to 1.0 at all times"""

    Target_Temperature_Schedule_Name: Annotated[str, Field()]
    """Defaults to hot water supply temperature"""

    Hot_Water_Supply_Temperature_Schedule_Name: Annotated[str, Field()]
    """Defaults to cold water supply temperature"""

    Cold_Water_Supply_Temperature_Schedule_Name: Annotated[str, Field()]
    """Defaults to water temperatures calculated by Site:WaterMainsTemperature object"""

    Zone_Name: Annotated[str, Field()]

    Sensible_Fraction_Schedule_Name: Annotated[str, Field()]
    """Defaults to 0.0 at all times"""

    Latent_Fraction_Schedule_Name: Annotated[str, Field()]
    """Defaults to 0.0 at all times"""