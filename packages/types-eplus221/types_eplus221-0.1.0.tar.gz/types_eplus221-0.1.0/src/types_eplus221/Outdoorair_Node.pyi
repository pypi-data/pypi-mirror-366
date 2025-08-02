from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Outdoorair_Node(EpBunch):
    """This object sets the temperature and humidity conditions"""

    Name: Annotated[str, Field(default=...)]

    Height_Above_Ground: Annotated[float, Field(default=-1.0)]
    """A value less than zero indicates that the height will be ignored and the weather file conditions will be used."""

    Drybulb_Temperature_Schedule_Name: Annotated[str, Field()]
    """Schedule values are real numbers, -100.0 to 100.0, units C"""

    Wetbulb_Temperature_Schedule_Name: Annotated[str, Field()]
    """Schedule values are real numbers, -100.0 to 100.0, units C"""

    Wind_Speed_Schedule_Name: Annotated[str, Field()]
    """Schedule values are real numbers, 0.0 to 40.0, units m/s"""

    Wind_Direction_Schedule_Name: Annotated[str, Field()]
    """Schedule values are real numbers, 0.0 to 360.0, units degree"""

    Wind_Pressure_Coefficient_Curve_Name: Annotated[str, Field()]
    """The name of the AirflowNetwork:MultiZone:WindPressureCoefficientValues, curve, or table object specifying the wind pressure coefficient."""

    Symmetric_Wind_Pressure_Coefficient_Curve: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Specify whether the pressure curve is symmetric or not."""

    Wind_Angle_Type: Annotated[Literal['Absolute', 'Relative'], Field(default='Absolute')]
    """Specify whether the angle used to compute the wind pressure coefficient is absolute or relative"""