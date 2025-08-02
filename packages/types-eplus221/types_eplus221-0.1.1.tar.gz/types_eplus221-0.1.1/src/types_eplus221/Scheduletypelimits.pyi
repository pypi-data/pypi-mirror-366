from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Scheduletypelimits(EpBunch):
    """ScheduleTypeLimits specifies the data types and limits for the values contained in schedules"""

    Name: Annotated[str, Field(default=...)]
    """used to validate schedule types in various schedule objects"""

    Lower_Limit_Value: Annotated[str, Field()]
    """lower limit (real or integer) for the Schedule Type. e.g. if fraction, this is 0.0"""

    Upper_Limit_Value: Annotated[str, Field()]
    """upper limit (real or integer) for the Schedule Type. e.g. if fraction, this is 1.0"""

    Numeric_Type: Annotated[Literal['Continuous', 'Discrete'], Field()]
    """Numeric type is either Continuous (all numbers within the min and"""

    Unit_Type: Annotated[Literal['Dimensionless', 'Temperature', 'DeltaTemperature', 'PrecipitationRate', 'Angle', 'ConvectionCoefficient', 'ActivityLevel', 'Velocity', 'Capacity', 'Power', 'Availability', 'Percent', 'Control', 'Mode'], Field(default='Dimensionless')]
    """Temperature (C or F)"""