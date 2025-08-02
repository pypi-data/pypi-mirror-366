from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Solarcollectorperformance_Photovoltaicthermal_Simple(EpBunch):
    """Thermal performance parameters for a hybrid photovoltaic-thermal (PVT) solar collector."""

    Name: Annotated[str, Field()]

    Fraction_of_Surface_Area_with_Active_Thermal_Collector: Annotated[float, Field(default=..., gt=0.0, le=1.0)]

    Thermal_Conversion_Efficiency_Input_Mode_Type: Annotated[Literal['Fixed', 'Scheduled'], Field()]

    Value_for_Thermal_Conversion_Efficiency_if_Fixed: Annotated[float, Field(ge=0.0, le=1.0)]
    """Efficiency = (thermal power generated [W])/(incident solar[W])"""

    Thermal_Conversion_Efficiency_Schedule_Name: Annotated[str, Field()]

    Front_Surface_Emittance: Annotated[float, Field(gt=0.00, lt=1.00, default=0.84)]