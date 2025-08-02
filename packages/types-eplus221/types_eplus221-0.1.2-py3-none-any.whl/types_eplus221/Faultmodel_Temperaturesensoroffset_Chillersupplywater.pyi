from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Faultmodel_Temperaturesensoroffset_Chillersupplywater(EpBunch):
    """This object describes fault of chiller supply water temperature sensor offset"""

    Name: Annotated[str, Field(default=...)]
    """Enter the name of the fault"""

    Availability_Schedule_Name: Annotated[str, Field()]

    Severity_Schedule_Name: Annotated[str, Field()]

    Chiller_Object_Type: Annotated[Literal['Chiller:Electric', 'Chiller:Electric:EIR', 'Chiller:Electric:ReformulatedEIR', 'Chiller:ConstantCOP', 'Chiller:EngineDriven', 'Chiller:CombustionTurbine', 'Chiller:Absorption', 'Chiller:Absorption:Indirect'], Field(default=...)]
    """Enter the type of a chiller object"""

    Chiller_Object_Name: Annotated[str, Field(default=...)]
    """Enter the name of a chiller object"""

    Reference_Sensor_Offset: Annotated[float, Field(gt=-10, lt=10, default=0.0)]