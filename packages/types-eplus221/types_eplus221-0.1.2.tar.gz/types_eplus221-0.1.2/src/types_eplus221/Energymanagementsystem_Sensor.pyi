from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Energymanagementsystem_Sensor(EpBunch):
    """Declares EMS variable as a sensor"""

    Name: Annotated[str, Field(default=...)]
    """This name becomes a variable for use in Erl programs"""

    OutputVariable_or_OutputMeter_Index_Key_Name: Annotated[str, Field()]

    OutputVariable_or_OutputMeter_Name: Annotated[str, Field(default=...)]