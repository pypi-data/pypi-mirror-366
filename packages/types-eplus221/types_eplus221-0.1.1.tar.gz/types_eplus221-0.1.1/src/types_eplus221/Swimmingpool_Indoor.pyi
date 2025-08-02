from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Swimmingpool_Indoor(EpBunch):
    """Specifies an indoor swimming pools linked to a floor surface."""

    Name: Annotated[str, Field(default=...)]

    Surface_Name: Annotated[str, Field(default=...)]
    """Name of the floor surface where the pool is located."""

    Average_Depth: Annotated[float, Field(default=...)]

    Activity_Factor_Schedule_Name: Annotated[str, Field(default=...)]

    Make_Up_Water_Supply_Schedule_Name: Annotated[str, Field(default=...)]

    Cover_Schedule_Name: Annotated[str, Field(default=...)]

    Cover_Evaporation_Factor: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Cover_Convection_Factor: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Cover_Short_Wavelength_Radiation_Factor: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Cover_Long_Wavelength_Radiation_Factor: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Pool_Water_Inlet_Node: Annotated[str, Field(default=...)]

    Pool_Water_Outlet_Node: Annotated[str, Field(default=...)]

    Pool_Heating_System_Maximum_Water_Flow_Rate: Annotated[float, Field(ge=0.0)]

    Pool_Miscellaneous_Equipment_Power: Annotated[float, Field(ge=0.0)]
    """Power input per pool water flow rate"""

    Setpoint_Temperature_Schedule: Annotated[str, Field(default=...)]

    Maximum_Number_Of_People: Annotated[str, Field(default=...)]

    People_Schedule: Annotated[str, Field()]

    People_Heat_Gain_Schedule: Annotated[str, Field()]