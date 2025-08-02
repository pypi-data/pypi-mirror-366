from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonecontrol_Thermostat_Temperatureandhumidity(EpBunch):
    """This object modifies a ZoneControl:Thermostat object to effect temperature control based on"""

    Thermostat_Name: Annotated[str, Field(default=...)]
    """Enter the name of a ZoneControl:Thermostat object whose operation is to be modified to"""

    Dehumidifying_Relative_Humidity_Setpoint_Schedule_Name: Annotated[str, Field(default=...)]
    """Schedule values should be in Relative Humidity (percent)"""

    Dehumidification_Control_Type: Annotated[Literal['Overcool', 'None'], Field(default='Overcool')]

    Overcool_Range_Input_Method: Annotated[Literal['Constant', 'Scheduled'], Field(default='Constant')]

    Overcool_Constant_Range: Annotated[float, Field(ge=0.0, le=3.0, default=1.7)]
    """Maximum Overcool temperature range for cooling setpoint reduction."""

    Overcool_Range_Schedule_Name: Annotated[str, Field()]
    """Schedule values of 0.0 indicates no zone temperature overcooling will be"""

    Overcool_Control_Ratio: Annotated[float, Field(ge=0.0, default=3.6)]
    """The value of this input field is used to adjust the cooling setpoint temperature"""