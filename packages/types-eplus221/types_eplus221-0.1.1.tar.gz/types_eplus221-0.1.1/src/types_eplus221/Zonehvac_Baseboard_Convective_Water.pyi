from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Baseboard_Convective_Water(EpBunch):
    """Hot water baseboard heater, convection-only. Natural convection hydronic heating unit."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Inlet_Node_Name: Annotated[str, Field(default=...)]

    Outlet_Node_Name: Annotated[str, Field(default=...)]

    Heating_Design_Capacity_Method: Annotated[Literal['HeatingDesignCapacity', 'CapacityPerFloorArea', 'FractionOfAutosizedHeatingCapacity'], Field(default='HeatingDesignCapacity')]
    """Enter the method used to determine the heating design capacity."""

    Heating_Design_Capacity: Annotated[float, Field(ge=0.0, default=autosize)]
    """Enter the design heating capacity.Required field when the heating design capacity method"""

    Heating_Design_Capacity_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the heating design capacity per zone floor area.Required field when the heating design"""

    Fraction_Of_Autosized_Heating_Design_Capacity: Annotated[float, Field(ge=0.0, default=1.0)]
    """Enter the fraction of auto - sized heating design capacity.Required field when capacity the"""

    U_Factor_Times_Area_Value: Annotated[str, Field(default=...)]

    Maximum_Water_Flow_Rate: Annotated[str, Field(default=...)]

    Convergence_Tolerance: Annotated[float, Field(gt=0.0, default=0.001)]