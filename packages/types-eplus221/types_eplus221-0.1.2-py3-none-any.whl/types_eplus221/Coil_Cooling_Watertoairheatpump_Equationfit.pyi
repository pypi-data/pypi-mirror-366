from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Cooling_Watertoairheatpump_Equationfit(EpBunch):
    """Direct expansion (DX) cooling coil for water-to-air heat pump (includes electric"""

    Name: Annotated[str, Field(default=...)]

    Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Rated_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Rated_Water_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(default=..., gt=0.0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Gross_Rated_Sensible_Cooling_Capacity: Annotated[float, Field(default=..., gt=0.0)]

    Gross_Rated_Cooling_COP: Annotated[float, Field(default=..., gt=0.0)]

    Total_Cooling_Capacity_Coefficient_1: Annotated[float, Field(default=...)]

    Total_Cooling_Capacity_Coefficient_2: Annotated[float, Field(default=...)]

    Total_Cooling_Capacity_Coefficient_3: Annotated[float, Field(default=...)]

    Total_Cooling_Capacity_Coefficient_4: Annotated[float, Field(default=...)]

    Total_Cooling_Capacity_Coefficient_5: Annotated[float, Field(default=...)]

    Sensible_Cooling_Capacity_Coefficient_1: Annotated[float, Field(default=...)]

    Sensible_Cooling_Capacity_Coefficient_2: Annotated[float, Field(default=...)]

    Sensible_Cooling_Capacity_Coefficient_3: Annotated[float, Field(default=...)]

    Sensible_Cooling_Capacity_Coefficient_4: Annotated[float, Field(default=...)]

    Sensible_Cooling_Capacity_Coefficient_5: Annotated[float, Field(default=...)]

    Sensible_Cooling_Capacity_Coefficient_6: Annotated[float, Field(default=...)]

    Cooling_Power_Consumption_Coefficient_1: Annotated[float, Field(default=...)]

    Cooling_Power_Consumption_Coefficient_2: Annotated[float, Field(default=...)]

    Cooling_Power_Consumption_Coefficient_3: Annotated[float, Field(default=...)]

    Cooling_Power_Consumption_Coefficient_4: Annotated[float, Field(default=...)]

    Cooling_Power_Consumption_Coefficient_5: Annotated[float, Field(default=...)]

    Nominal_Time_for_Condensate_Removal_to_Begin: Annotated[float, Field(ge=0.0, le=3000.0, default=0.0)]
    """The nominal time for condensate to begin leaving the coil's condensate"""

    Ratio_of_Initial_Moisture_Evaporation_Rate_and_Steady_State_Latent_Capacity: Annotated[float, Field(ge=0.0, le=5.0, default=0.0)]
    """Ratio of the initial moisture evaporation rate from the cooling coil (when"""