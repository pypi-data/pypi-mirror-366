from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Faultmodel_Temperaturesensoroffset_Coilsupplyair(EpBunch):
    """This object describes fault of coil supply air temperature sensor offset"""

    Name: Annotated[str, Field(default=...)]
    """Enter the name of the fault"""

    Availability_Schedule_Name: Annotated[str, Field()]

    Severity_Schedule_Name: Annotated[str, Field()]

    Coil_Object_Type: Annotated[Literal['AirLoopHVAC:UnitarySystem', 'Coil:Heating:Electric', 'Coil:Heating:Gas', 'Coil:Heating:Desuperheater', 'Coil:Heating:Steam', 'Coil:Heating:Water', 'Coil:Cooling:Water', 'Coil:Cooling:Water:Detailedgeometry', 'CoilSystem:Cooling:DX', 'CoilSystem:Heating:DX'], Field(default=...)]
    """Enter the type of the coil affected"""

    Coil_Object_Name: Annotated[str, Field(default=...)]
    """Enter the name of the coil affected"""

    Water_Coil_Controller_Name: Annotated[str, Field()]
    """Enter the name of controller for the water coil affected"""

    Reference_Sensor_Offset: Annotated[float, Field(gt=-10, lt=10, default=0.0)]