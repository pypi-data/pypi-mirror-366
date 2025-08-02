from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Multizone_Surface(EpBunch):
    """This object specifies the properties of a surface linkage through which air flows."""

    Surface_Name: Annotated[str, Field(default=...)]
    """Enter the name of a heat transfer surface."""

    Leakage_Component_Name: Annotated[str, Field(default=...)]
    """Enter the name of an Airflow Network leakage component. A leakage component is"""

    External_Node_Name: Annotated[str, Field()]
    """Used if Wind Pressure Coefficient Type = Input in the AirflowNetwork:SimulationControl object,"""

    Window_Door_Opening_Factor__Or_Crack_Factor: Annotated[float, Field(gt=0.0, le=1.0, default=1.0)]
    """This field specifies a multiplier for a crack, window, or door."""

    Ventilation_Control_Mode: Annotated[Literal['Temperature', 'Enthalpy', 'Constant', 'ASHRAE55Adaptive', 'CEN15251Adaptive', 'NoVent', 'ZoneLevel', 'AdjacentTemperature', 'AdjacentEnthalpy'], Field(default='ZoneLevel')]
    """When Ventilation Control Mode = Temperature or Enthalpy, the following"""

    Ventilation_Control_Zone_Temperature_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Used only if Ventilation Control Mode = Temperature or Enthalpy."""

    Minimum_Venting_Open_Factor: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Used only if Ventilation Control Mode = Temperature or Enthalpy."""

    Indoor_And_Outdoor_Temperature_Difference_Lower_Limit_For_Maximum_Venting_Open_Factor: Annotated[float, Field(ge=0.0, lt=100, default=0.0)]
    """Applicable only if Ventilation Control Mode = Temperature"""

    Indoor_And_Outdoor_Temperature_Difference_Upper_Limit_For_Minimum_Venting_Open_Factor: Annotated[float, Field(gt=0.0, default=100.0)]
    """Applicable only if Ventilation Control Mode = Temperature."""

    Indoor_And_Outdoor_Enthalpy_Difference_Lower_Limit_For_Maximum_Venting_Open_Factor: Annotated[float, Field(ge=0.0, lt=300000.0, default=0.0)]
    """Applicable only if Ventilation Control Mode = Enthalpy."""

    Indoor_And_Outdoor_Enthalpy_Difference_Upper_Limit_For_Minimum_Venting_Open_Factor: Annotated[float, Field(gt=0.0, default=300000.0)]
    """Applicable only if Ventilation Control Mode = Enthalpy."""

    Venting_Availability_Schedule_Name: Annotated[str, Field()]
    """Non-zero schedule value means venting is allowed if other venting control conditions are"""

    Occupant_Ventilation_Control_Name: Annotated[str, Field()]
    """Enter the name where Occupancy Ventilation Control is required."""

    Equivalent_Rectangle_Method: Annotated[Literal['PolygonHeight', 'BaseSurfaceAspectRatio', 'UserDefinedAspectRatio'], Field(default='PolygonHeight')]
    """This field is applied to a non-rectangular window or door. The equivalent shape has"""

    Equivalent_Rectangle_Aspect_Ratio: Annotated[float, Field(gt=0.0, default=1.0)]
    """This field is used when UserDefinedAspectRatio is entered in the Equivalent"""