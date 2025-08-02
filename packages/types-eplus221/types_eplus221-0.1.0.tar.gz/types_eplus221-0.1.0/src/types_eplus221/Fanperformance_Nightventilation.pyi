from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Fanperformance_Nightventilation(EpBunch):
    """Specifies an alternate set of performance parameters for a fan. These alternate"""

    Fan_Name: Annotated[str, Field(default=...)]

    Fan_Total_Efficiency: Annotated[float, Field(default=..., gt=0.0, le=1.0)]

    Pressure_Rise: Annotated[str, Field(default=...)]

    Maximum_Flow_Rate: Annotated[str, Field()]

    Motor_Efficiency: Annotated[float, Field(default=..., gt=0, le=1.0)]

    Motor_In_Airstream_Fraction: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]
    """0.0 means fan motor outside of airstream"""