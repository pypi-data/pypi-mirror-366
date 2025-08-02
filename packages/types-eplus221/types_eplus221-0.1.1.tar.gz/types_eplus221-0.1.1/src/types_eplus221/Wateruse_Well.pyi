from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Wateruse_Well(EpBunch):
    """Simulates on-site water supply from a well. Well water is pumped out of the ground"""

    Name: Annotated[str, Field(default=...)]

    Storage_Tank_Name: Annotated[str, Field(default=...)]

    Pump_Depth: Annotated[float, Field()]

    Pump_Rated_Flow_Rate: Annotated[float, Field()]

    Pump_Rated_Head: Annotated[float, Field()]

    Pump_Rated_Power_Consumption: Annotated[float, Field()]

    Pump_Efficiency: Annotated[float, Field()]

    Well_Recovery_Rate: Annotated[float, Field()]

    Nominal_Well_Storage_Volume: Annotated[float, Field()]

    Water_Table_Depth_Mode: Annotated[Literal['Constant', 'Scheduled'], Field()]

    Water_Table_Depth: Annotated[float, Field()]

    Water_Table_Depth_Schedule_Name: Annotated[str, Field()]