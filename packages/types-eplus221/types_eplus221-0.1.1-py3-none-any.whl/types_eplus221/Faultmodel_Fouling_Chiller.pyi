from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Faultmodel_Fouling_Chiller(EpBunch):
    """This object describes the fouling fault of chillers with water-cooled condensers"""

    Name: Annotated[str, Field(default=...)]
    """Enter the name of the fault"""

    Availability_Schedule_Name: Annotated[str, Field()]

    Severity_Schedule_Name: Annotated[str, Field()]

    Chiller_Object_Type: Annotated[Literal['Chiller:Electric', 'Chiller:Electric:EIR', 'Chiller:Electric:ReformulatedEIR', 'Chiller:ConstantCOP', 'Chiller:EngineDriven', 'Chiller:CombustionTurbine'], Field(default=...)]
    """Enter the type of a chiller object"""

    Chiller_Object_Name: Annotated[str, Field(default=...)]
    """Enter the name of a chiller object"""

    Fouling_Factor: Annotated[float, Field(gt=0, le=1, default=1)]
    """The factor indicates the decrease of the nominal capacity of the chiller"""