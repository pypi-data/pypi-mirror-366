from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Generator_Fuelcell_Watersupply(EpBunch):
    """Used to provide details of the water supply subsystem for a fuel cell power generator."""

    Name: Annotated[str, Field(default=...)]

    Reformer_Water_Flow_Rate_Function_of_Fuel_Rate_Curve_Name: Annotated[str, Field()]

    Reformer_Water_Pump_Power_Function_of_Fuel_Rate_Curve_Name: Annotated[str, Field()]

    Pump_Heat_Loss_Factor: Annotated[str, Field()]

    Water_Temperature_Modeling_Mode: Annotated[Literal['TemperatureFromAirNode', 'TemperatureFromWaterNode', 'TemperatureFromSchedule', 'MainsWaterTemperature'], Field()]

    Water_Temperature_Reference_Node_Name: Annotated[str, Field()]

    Water_Temperature_Schedule_Name: Annotated[str, Field()]