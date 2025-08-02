from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Faultmodel_Fouling_Airfilter(EpBunch):
    """This object describes fault of dirty air filters"""

    Name: Annotated[str, Field(default=...)]
    """Enter the name of the fault"""

    Fan_Object_Type: Annotated[Literal['Fan:OnOff', 'Fan:ConstantVolume', 'Fan:VariableVolume'], Field(default=...)]
    """Choose the type of the fan"""

    Fan_Name: Annotated[str, Field(default=...)]
    """Enter the name of a fan object"""

    Availability_Schedule_Name: Annotated[str, Field()]

    Pressure_Fraction_Schedule_Name: Annotated[str, Field(default=...)]
    """Enter the name of a schedule"""

    Fan_Curve_Name: Annotated[str, Field(default=...)]
    """The curve describes the relationship between"""