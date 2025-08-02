from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Schedule_Day_Hourly(EpBunch):
    """A Schedule:Day:Hourly contains 24 values for each hour of the day."""

    Name: Annotated[str, Field(default=...)]

    Schedule_Type_Limits_Name: Annotated[str, Field()]

    Hour_1: Annotated[float, Field(default=0)]

    Hour_2: Annotated[float, Field(default=0)]

    Hour_3: Annotated[float, Field(default=0)]

    Hour_4: Annotated[float, Field(default=0)]

    Hour_5: Annotated[float, Field(default=0)]

    Hour_6: Annotated[float, Field(default=0)]

    Hour_7: Annotated[float, Field(default=0)]

    Hour_8: Annotated[float, Field(default=0)]

    Hour_9: Annotated[float, Field(default=0)]

    Hour_10: Annotated[float, Field(default=0)]

    Hour_11: Annotated[float, Field(default=0)]

    Hour_12: Annotated[float, Field(default=0)]

    Hour_13: Annotated[float, Field(default=0)]

    Hour_14: Annotated[float, Field(default=0)]

    Hour_15: Annotated[float, Field(default=0)]

    Hour_16: Annotated[float, Field(default=0)]

    Hour_17: Annotated[float, Field(default=0)]

    Hour_18: Annotated[float, Field(default=0)]

    Hour_19: Annotated[float, Field(default=0)]

    Hour_20: Annotated[float, Field(default=0)]

    Hour_21: Annotated[float, Field(default=0)]

    Hour_22: Annotated[float, Field(default=0)]

    Hour_23: Annotated[float, Field(default=0)]

    Hour_24: Annotated[float, Field(default=0)]