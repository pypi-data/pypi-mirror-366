from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonecooltower_Shower(EpBunch):
    """A cooltower (sometimes referred to as a wind tower or a shower cooling tower)"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Zone_Name: Annotated[str, Field(default=...)]

    Water_Supply_Storage_Tank_Name: Annotated[str, Field()]
    """In case of stand alone tank or underground water, leave this input blank"""

    Flow_Control_Type: Annotated[Literal['WaterFlowSchedule', 'WindDrivenFlow'], Field(default='WindDrivenFlow')]
    """Water flow schedule should be selected when the water flow rate is known."""

    Pump_Flow_Rate_Schedule_Name: Annotated[str, Field(default=...)]

    Maximum_Water_Flow_Rate: Annotated[float, Field(default=...)]

    Effective_Tower_Height: Annotated[float, Field(default=...)]
    """This field is from either the spray or the wet pad to the top of the outlet."""

    Airflow_Outlet_Area: Annotated[float, Field(default=...)]
    """User have to specify effective area when outlet area is relatively bigger than the cross sectional area"""

    Maximum_Air_Flow_Rate: Annotated[float, Field(default=..., ge=0)]

    Minimum_Indoor_Temperature: Annotated[float, Field(default=..., ge=-100, le=100)]
    """This field is to specify the indoor temperature below which cooltower is shutoff."""

    Fraction_of_Water_Loss: Annotated[str, Field()]

    Fraction_of_Flow_Schedule: Annotated[str, Field()]

    Rated_Power_Consumption: Annotated[float, Field(default=...)]