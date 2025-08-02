from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Designspecification_Outdoorair(EpBunch):
    """This object is used to describe general outdoor air requirements which"""

    Name: Annotated[str, Field(default=...)]

    Outdoor_Air_Method: Annotated[Literal['Flow/Person', 'Flow/Area', 'Flow/Zone', 'AirChanges/Hour', 'Sum', 'Maximum', 'IndoorAirQualityProcedure', 'ProportionalControlBasedOnDesignOccupancy', 'ProportionalControlBasedonOccupancySchedule'], Field(default='Flow/Person')]
    """Flow/Person => Outdoor Air Flow per Person * Occupancy = Design Flow Rate,"""

    Outdoor_Air_Flow_per_Person: Annotated[float, Field(ge=0, default=0.00944)]
    """0.00944 m3/s is equivalent to 20 cfm per person"""

    Outdoor_Air_Flow_per_Zone_Floor_Area: Annotated[str, Field(default='0.0')]
    """This input is only used if the field Outdoor Air Method is Flow/Area, Sum, or Maximum"""

    Outdoor_Air_Flow_per_Zone: Annotated[float, Field(ge=0, default=0.0)]
    """This input is only used if the field Outdoor Air Method is Flow/Zone, Sum, or Maximum"""

    Outdoor_Air_Flow_Air_Changes_per_Hour: Annotated[float, Field(ge=0, default=0.0)]
    """This input is only used if the field Outdoor Air Method is AirChanges/Hour, Sum, or Maximum"""

    Outdoor_Air_Schedule_Name: Annotated[str, Field()]
    """Schedule values are multiplied by the Outdoor Air Flow rate calculated using"""

    Proportional_Control_Minimum_Outdoor_Air_Flow_Rate_Schedule_Name: Annotated[str, Field()]
    """This input is only used to calculate the minimum outdoor air flow rate when the field"""