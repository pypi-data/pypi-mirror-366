from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Faultmodel_Temperaturesensoroffset_Condensersupplywater(EpBunch):
    """This object describes fault of condenser supply water temperature sensor offset"""

    Name: Annotated[str, Field(default=...)]
    """Enter the name of the fault"""

    Availability_Schedule_Name: Annotated[str, Field()]

    Severity_Schedule_Name: Annotated[str, Field()]

    Cooling_Tower_Object_Type: Annotated[Literal['CoolingTower:SingleSpeed', 'CoolingTower:TwoSpeed', 'CoolingTower:VariableSpeed', 'CoolingTower:VariableSpeed:MERKEL'], Field(default=...)]
    """Enter the type of the cooling tower affected"""

    Cooling_Tower_Object_Name: Annotated[str, Field(default=...)]
    """Enter the name of the cooling tower affected"""

    Reference_Sensor_Offset: Annotated[float, Field(gt=-10, lt=10, default=0.0)]