from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonemixing(EpBunch):
    """ZoneMixing is a simple air exchange from one zone to another. Note that this statement"""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]

    Design_Flow_Rate_Calculation_Method: Annotated[Literal['Flow/Zone', 'Flow/Area', 'Flow/Person', 'AirChanges/Hour'], Field(default='Flow/Zone')]
    """The entered calculation method is used to create the maximum amount of ventilation"""

    Design_Flow_Rate: Annotated[float, Field(ge=0)]

    Flow_Rate_per_Zone_Floor_Area: Annotated[float, Field(ge=0)]

    Flow_Rate_per_Person: Annotated[float, Field(ge=0)]

    Air_Changes_per_Hour: Annotated[float, Field(ge=0)]

    Source_Zone_Name: Annotated[str, Field(default=...)]

    Delta_Temperature: Annotated[float, Field(default=0)]
    """This field contains the constant temperature differential between source and"""

    Delta_Temperature_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the temperature differential between source and receiving"""

    Minimum_Zone_Temperature_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the zone dry-bulb temperature versus time below which"""

    Maximum_Zone_Temperature_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the zone dry-bulb temperature versus time above which"""

    Minimum_Source_Zone_Temperature_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the source zone dry-bulb temperature versus time below"""

    Maximum_Source_Zone_Temperature_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the source zone dry-bulb temperature versus time above"""

    Minimum_Outdoor_Temperature_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the outdoor temperature versus time below which"""

    Maximum_Outdoor_Temperature_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the outdoor temperature versus time above which"""