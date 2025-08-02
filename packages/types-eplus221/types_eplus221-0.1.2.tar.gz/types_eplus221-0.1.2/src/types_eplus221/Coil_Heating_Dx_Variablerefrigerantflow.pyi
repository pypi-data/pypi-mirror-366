from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Heating_Dx_Variablerefrigerantflow(EpBunch):
    """Variable refrigerant flow (VRF) direct expansion (DX) heating coil (air-to-air heat"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Gross_Rated_Heating_Capacity: Annotated[float, Field(default=..., gt=0.0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Rated_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """volume flow rate corresponding to rated total capacity"""

    Coil_Air_Inlet_Node: Annotated[str, Field(default=...)]

    Coil_Air_Outlet_Node: Annotated[str, Field(default=...)]

    Heating_Capacity_Ratio_Modifier_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]

    Heating_Capacity_Modifier_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""