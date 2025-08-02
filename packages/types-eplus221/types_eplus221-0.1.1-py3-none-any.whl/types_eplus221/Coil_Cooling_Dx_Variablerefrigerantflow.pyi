from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Cooling_Dx_Variablerefrigerantflow(EpBunch):
    """Variable refrigerant flow (VRF) direct expansion (DX) cooling coil. Used with"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(default=..., gt=0.0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(default=..., gt=0.0)]
    """Sensible heat ratio excluding supply air fan heat"""

    Rated_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Volume flow rate corresponding to rated total cooling capacity"""

    Cooling_Capacity_Ratio_Modifier_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]

    Cooling_Capacity_Modifier_Curve_Function_Of_Flow_Fraction_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""

    Coil_Air_Inlet_Node: Annotated[str, Field(default=...)]

    Coil_Air_Outlet_Node: Annotated[str, Field(default=...)]

    Name_Of_Water_Storage_Tank_For_Condensate_Collection: Annotated[str, Field()]