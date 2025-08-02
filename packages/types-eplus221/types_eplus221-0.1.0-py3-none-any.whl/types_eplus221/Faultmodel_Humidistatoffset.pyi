from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Faultmodel_Humidistatoffset(EpBunch):
    """This object describes fault of humidistat offset"""

    Name: Annotated[str, Field(default=...)]
    """Enter the name of the fault"""

    Humidistat_Name: Annotated[str, Field(default=...)]
    """Enter the name of a ZoneControl:Humidistat object."""

    Humidistat_Offset_Type: Annotated[Literal['ThermostatOffsetIndependent', 'ThermostatOffsetDependent'], Field(default='ThermostatOffsetIndependent')]
    """Two types are available:"""

    Availability_Schedule_Name: Annotated[str, Field()]
    """This field is applicable for Type ThermostatOffsetIndependent"""

    Severity_Schedule_Name: Annotated[str, Field()]
    """This field is applicable for Type ThermostatOffsetIndependent"""

    Reference_Humidistat_Offset: Annotated[float, Field(gt=-20, lt=20, default=5)]
    """Required field for Type ThermostatOffsetIndependent"""

    Related_Thermostat_Offset_Fault_Name: Annotated[str, Field()]
    """Enter the name of a FaultModel:ThermostatOffset object"""