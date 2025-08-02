from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Multizone_Zone(EpBunch):
    """This object is used to simultaneously control a thermal zone's window and door openings,"""

    Zone_Name: Annotated[str, Field(default=...)]
    """Enter the zone name where ventilation control is required."""

    Ventilation_Control_Mode: Annotated[Literal['Temperature', 'Enthalpy', 'Constant', 'ASHRAE55Adaptive', 'CEN15251Adaptive', 'NoVent'], Field(default='NoVent')]
    """When Ventilation Control Mode = Temperature or Enthalpy, the following"""

    Ventilation_Control_Zone_Temperature_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Used only if Ventilation Control Mode = Temperature or Enthalpy."""

    Minimum_Venting_Open_Factor: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Used only if Ventilation Control Mode = Temperature or Enthalpy."""

    Indoor_and_Outdoor_Temperature_Difference_Lower_Limit_For_Maximum_Venting_Open_Factor: Annotated[float, Field(ge=0.0, lt=100.0, default=0.0)]
    """Applicable only if Ventilation Control Mode = Temperature."""

    Indoor_and_Outdoor_Temperature_Difference_Upper_Limit_for_Minimum_Venting_Open_Factor: Annotated[float, Field(gt=0.0, default=100.0)]
    """Applicable only if Ventilation Control Mode = Temperature."""

    Indoor_and_Outdoor_Enthalpy_Difference_Lower_Limit_For_Maximum_Venting_Open_Factor: Annotated[float, Field(ge=0.0, lt=300000.0, default=0.0)]
    """Applicable only if Ventilation Control Mode = Enthalpy."""

    Indoor_and_Outdoor_Enthalpy_Difference_Upper_Limit_for_Minimum_Venting_Open_Factor: Annotated[float, Field(gt=0.0, default=300000.0)]
    """Applicable only if Ventilation Control Mode = Enthalpy."""

    Venting_Availability_Schedule_Name: Annotated[str, Field()]
    """Non-zero Schedule value means venting is allowed if other venting control conditions are"""

    Single_Sided_Wind_Pressure_Coefficient_Algorithm: Annotated[Literal['Advanced', 'Standard'], Field(default='Standard')]
    """Selecting Advanced results in EnergyPlus calculating modified Wind Pressure Coefficients"""

    Facade_Width: Annotated[float, Field(ge=0.0, default=10.0)]
    """This is the whole building width along the direction of the facade of this zone."""

    Occupant_Ventilation_Control_Name: Annotated[str, Field()]
    """Enter the name where Occupancy Ventilation Control is required."""