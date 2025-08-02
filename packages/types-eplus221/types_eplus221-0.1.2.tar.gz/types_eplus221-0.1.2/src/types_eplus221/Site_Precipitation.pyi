from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Precipitation(EpBunch):
    """Used to describe the amount of water precipitation at the building site."""

    Precipitation_Model_Type: Annotated[Literal['ScheduleAndDesignLevel'], Field()]

    Design_Level_for_Total_Annual_Precipitation: Annotated[str, Field()]
    """meters of water per year used for design level"""

    Precipitation_Rates_Schedule_Name: Annotated[str, Field()]
    """Schedule values in meters of water per hour"""

    Average_Total_Annual_Precipitation: Annotated[str, Field()]
    """meters of water per year from average weather statistics"""