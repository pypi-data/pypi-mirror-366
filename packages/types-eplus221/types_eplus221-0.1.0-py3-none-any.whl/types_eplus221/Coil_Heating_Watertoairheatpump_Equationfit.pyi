from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Heating_Watertoairheatpump_Equationfit(EpBunch):
    """Direct expansion (DX) heating coil for water-to-air heat pump (includes electric"""

    Name: Annotated[str, Field(default=...)]

    Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Rated_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Rated_Water_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Gross_Rated_Heating_Capacity: Annotated[float, Field(default=..., gt=0.0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Gross_Rated_Heating_Cop: Annotated[float, Field(default=..., gt=0.0)]

    Heating_Capacity_Coefficient_1: Annotated[float, Field(default=...)]

    Heating_Capacity_Coefficient_2: Annotated[float, Field(default=...)]

    Heating_Capacity_Coefficient_3: Annotated[float, Field(default=...)]

    Heating_Capacity_Coefficient_4: Annotated[float, Field(default=...)]

    Heating_Capacity_Coefficient_5: Annotated[float, Field(default=...)]

    Heating_Power_Consumption_Coefficient_1: Annotated[float, Field(default=...)]

    Heating_Power_Consumption_Coefficient_2: Annotated[float, Field(default=...)]

    Heating_Power_Consumption_Coefficient_3: Annotated[float, Field(default=...)]

    Heating_Power_Consumption_Coefficient_4: Annotated[float, Field(default=...)]

    Heating_Power_Consumption_Coefficient_5: Annotated[float, Field(default=...)]