from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Availabilitymanager_Hybridventilation(EpBunch):
    """Depending on zone and outdoor conditions overrides window/door opening controls"""

    Name: Annotated[str, Field(default=...)]

    HVAC_Air_Loop_Name: Annotated[str, Field()]
    """Enter the name of an AirLoopHVAC or HVACTemplate:System:* object."""

    Control_Zone_Name: Annotated[str, Field(default=...)]
    """the zone name should be a zone where a thermostat or humidistat is located"""

    Ventilation_Control_Mode_Schedule_Name: Annotated[str, Field(default=...)]
    """The Ventilation control mode contains appropriate integer control types."""

    Use_Weather_File_Rain_Indicators: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """If Yes, ventilation is shutoff when there is rain"""

    Maximum_Wind_Speed: Annotated[float, Field(ge=0.0, le=40.0, default=40.0)]
    """this is the wind speed above which ventilation is shutoff"""

    Minimum_Outdoor_Temperature: Annotated[float, Field(ge=-100, le=100, default=-100)]
    """this is the outdoor temperature below which ventilation is shutoff"""

    Maximum_Outdoor_Temperature: Annotated[float, Field(ge=-100, le=100, default=100)]
    """this is the outdoor temperature above which ventilation is shutoff"""

    Minimum_Outdoor_Enthalpy: Annotated[float, Field(gt=0.0, lt=300000.0)]
    """this is the outdoor Enthalpy below which ventilation is shutoff"""

    Maximum_Outdoor_Enthalpy: Annotated[float, Field(gt=0, lt=300000.0)]
    """this is the outdoor Enthalpy above which ventilation is shutoff"""

    Minimum_Outdoor_Dewpoint: Annotated[float, Field(ge=-100, le=100, default=-100)]
    """this is the outdoor temperature below which ventilation is shutoff"""

    Maximum_Outdoor_Dewpoint: Annotated[float, Field(ge=-100, le=100, default=100)]
    """this is the outdoor dewpoint above which ventilation is shutoff"""

    Minimum_Outdoor_Ventilation_Air_Schedule_Name: Annotated[str, Field()]
    """Used only if Ventilation Control Mode = 4"""

    Opening_Factor_Function_of_Wind_Speed_Curve_Name: Annotated[str, Field()]
    """linear curve = a + b*WS"""

    AirflowNetwork_Control_Type_Schedule_Name: Annotated[str, Field()]
    """The schedule is used to incorporate operation of AirflowNetwork large opening"""

    Simple_Airflow_Control_Type_Schedule_Name: Annotated[str, Field()]
    """The schedule is used to incorporate operation of simple airflow objects and HVAC"""

    ZoneVentilation_Object_Name: Annotated[str, Field()]
    """This field has not been instrumented to work with"""

    Minimum_HVAC_Operation_Time: Annotated[float, Field(ge=0.0, default=0.0)]
    """Minimum operation time when HVAC system is forced on."""

    Minimum_Ventilation_Time: Annotated[float, Field(ge=0.0, default=0.0)]
    """Minimum ventilation time when natural ventilation is forced on."""