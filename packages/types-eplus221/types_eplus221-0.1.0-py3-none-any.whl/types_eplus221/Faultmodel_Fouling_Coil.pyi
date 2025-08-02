from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Faultmodel_Fouling_Coil(EpBunch):
    """This object describes fouling water heating or cooling coils"""

    Name: Annotated[str, Field(default=...)]

    Coil_Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]

    Severity_Schedule_Name: Annotated[str, Field()]

    Fouling_Input_Method: Annotated[Literal['FouledUARated', 'FoulingFactor'], Field(default='FouledUARated')]

    Uafouled: Annotated[float, Field(gt=0.0)]
    """Fouling coil UA value under rating conditions"""

    Water_Side_Fouling_Factor: Annotated[float, Field(ge=0.0, default=0.0)]
    """For Fouling Input Method: FoulingFactor"""

    Air_Side_Fouling_Factor: Annotated[float, Field(ge=0.0, default=0.0)]
    """For Fouling Input Method: FoulingFactor"""

    Outside_Coil_Surface_Area: Annotated[float, Field(gt=0.0)]
    """For Fouling Input Method: FoulingFactor"""

    Inside_To_Outside_Coil_Surface_Area_Ratio: Annotated[float, Field(gt=0.0, default=0.07)]
    """For Fouling Input Method: FoulingFactor"""