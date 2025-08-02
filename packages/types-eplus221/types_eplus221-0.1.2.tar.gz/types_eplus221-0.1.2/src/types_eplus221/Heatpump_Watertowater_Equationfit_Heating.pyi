from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Heatpump_Watertowater_Equationfit_Heating(EpBunch):
    """simple water-water hp curve-fit model"""

    Name: Annotated[str, Field(default=...)]

    Source_Side_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Source_Side_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Load_Side_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Load_Side_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Reference_Load_Side_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Reference_Source_Side_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Reference_Heating_Capacity: Annotated[float, Field(default=..., gt=0.0)]

    Reference_Heating_Power_Consumption: Annotated[float, Field(default=..., gt=0.0)]

    Heating_Capacity_Coefficient_1: Annotated[float, Field(default=...)]

    Heating_Capacity_Coefficient_2: Annotated[float, Field(default=...)]

    Heating_Capacity_Coefficient_3: Annotated[float, Field(default=...)]

    Heating_Capacity_Coefficient_4: Annotated[float, Field(default=...)]

    Heating_Capacity_Coefficient_5: Annotated[float, Field(default=...)]

    Heating_Compressor_Power_Coefficient_1: Annotated[float, Field(default=...)]

    Heating_Compressor_Power_Coefficient_2: Annotated[float, Field(default=...)]

    Heating_Compressor_Power_Coefficient_3: Annotated[float, Field(default=...)]

    Heating_Compressor_Power_Coefficient_4: Annotated[float, Field(default=...)]

    Heating_Compressor_Power_Coefficient_5: Annotated[float, Field(default=...)]

    Reference_Coefficient_of_Performance: Annotated[float, Field(gt=0.0, default=7.5)]
    """This optional field is used to autosize Reference Heating Power Consumption"""

    Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized capacity and flow rates"""

    Companion_Cooling_Heat_Pump_Name: Annotated[str, Field()]