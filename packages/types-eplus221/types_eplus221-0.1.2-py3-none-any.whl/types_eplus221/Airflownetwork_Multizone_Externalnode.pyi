from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Multizone_Externalnode(EpBunch):
    """This object defines outdoor environmental conditions outside of the building."""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this object."""

    External_Node_Height: Annotated[float, Field(default=0.0)]
    """Designates the reference height used to calculate relative pressure."""

    Wind_Pressure_Coefficient_Curve_Name: Annotated[str, Field(default=...)]
    """The name of the AirflowNetwork:MultiZone:WindPressureCoefficientValues, curve, or table object specifying the wind pressure coefficient."""

    Symmetric_Wind_Pressure_Coefficient_Curve: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Specify whether the pressure curve is symmetric or not."""

    Wind_Angle_Type: Annotated[Literal['Absolute', 'Relative'], Field(default='Absolute')]
    """Specify whether the angle used to compute the wind pressure coefficient is absolute or relative"""