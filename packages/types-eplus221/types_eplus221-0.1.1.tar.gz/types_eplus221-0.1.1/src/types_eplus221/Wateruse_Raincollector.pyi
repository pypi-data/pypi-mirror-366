from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Wateruse_Raincollector(EpBunch):
    """Used for harvesting rainwater falling on building surfaces. The rainwater is sent to a"""

    Name: Annotated[str, Field(default=...)]

    Storage_Tank_Name: Annotated[str, Field(default=...)]

    Loss_Factor_Mode: Annotated[Literal['Constant', 'Scheduled'], Field()]

    Collection_Loss_Factor: Annotated[float, Field()]
    """this is the portion of rain"""

    Collection_Loss_Factor_Schedule_Name: Annotated[str, Field()]

    Maximum_Collection_Rate: Annotated[float, Field()]
    """Defaults to unlimited flow."""

    Collection_Surface_1_Name: Annotated[str, Field(default=...)]

    Collection_Surface_2_Name: Annotated[str, Field()]

    Collection_Surface_3_Name: Annotated[str, Field()]

    Collection_Surface_4_Name: Annotated[str, Field()]

    Collection_Surface_5_Name: Annotated[str, Field()]

    Collection_Surface_6_Name: Annotated[str, Field()]

    Collection_Surface_7_Name: Annotated[str, Field()]

    Collection_Surface_8_Name: Annotated[str, Field()]

    Collection_Surface_9_Name: Annotated[str, Field()]

    Collection_Surface_10_Name: Annotated[str, Field()]