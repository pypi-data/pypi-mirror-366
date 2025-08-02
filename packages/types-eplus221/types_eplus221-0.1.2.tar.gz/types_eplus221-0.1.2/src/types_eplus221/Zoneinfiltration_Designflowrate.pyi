from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zoneinfiltration_Designflowrate(EpBunch):
    """Infiltration is specified as a design level which is modified by a Schedule fraction, temperature difference and wind speed:"""

    Name: Annotated[str, Field(default=...)]

    Zone_or_ZoneList_Name: Annotated[str, Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]

    Design_Flow_Rate_Calculation_Method: Annotated[Literal['Flow/Zone', 'Flow/Area', 'Flow/ExteriorArea', 'Flow/ExteriorWallArea', 'AirChanges/Hour'], Field(default='Flow/Zone')]
    """The entered calculation method is used to create the maximum amount of infiltration"""

    Design_Flow_Rate: Annotated[float, Field(ge=0)]

    Flow_per_Zone_Floor_Area: Annotated[float, Field(ge=0)]

    Flow_per_Exterior_Surface_Area: Annotated[float, Field(ge=0)]
    """use key Flow/ExteriorArea for all exterior surface area"""

    Air_Changes_per_Hour: Annotated[float, Field(ge=0)]

    Constant_Term_Coefficient: Annotated[float, Field(default=1)]
    """"A" in Equation"""

    Temperature_Term_Coefficient: Annotated[float, Field(default=0)]
    """"B" in Equation"""

    Velocity_Term_Coefficient: Annotated[float, Field(default=0)]
    """"C" in Equation"""

    Velocity_Squared_Term_Coefficient: Annotated[float, Field(default=0)]
    """"D" in Equation"""