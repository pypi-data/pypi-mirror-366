from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Heating_Dx_Variablerefrigerantflow_Fluidtemperaturecontrol(EpBunch):
    """This is a key object in the new physics based VRF model applicable for Fluid"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule: Annotated[str, Field()]
    """Enter the name of a schedule that defines the availability of the coil"""

    Coil_Air_Inlet_Node: Annotated[str, Field(default=...)]
    """the inlet node to the coil"""

    Coil_Air_Outlet_Node: Annotated[str, Field(default=...)]
    """the outlet node to the coil"""

    Rated_Total_Heating_Capacity: Annotated[float, Field(default=..., gt=0.0)]
    """Supply air fan heat is not included"""

    Indoor_Unit_Reference_Subcooling: Annotated[float, Field(ge=0.0, default=5.0)]

    Indoor_Unit_Condensing_Temperature_Function_of_Subcooling_Curve_Name: Annotated[str, Field(default=...)]