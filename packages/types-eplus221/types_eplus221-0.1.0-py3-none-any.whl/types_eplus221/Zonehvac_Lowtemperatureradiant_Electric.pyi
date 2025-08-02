from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Lowtemperatureradiant_Electric(EpBunch):
    """Electric resistance low temperature radiant system"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Zone_Name: Annotated[str, Field()]
    """Name of zone system is serving"""

    Surface_Name_Or_Radiant_Surface_Group_Name: Annotated[str, Field()]
    """Identifies surfaces that radiant system is embedded in."""

    Heating_Design_Capacity_Method: Annotated[Literal['HeatingDesignCapacity', 'CapacityPerFloorArea', 'FractionOfAutosizedHeatingCapacity'], Field(default='HeatingDesignCapacity')]
    """Enter the method used to determine the maximum electrical heating design capacity."""

    Heating_Design_Capacity: Annotated[float, Field(ge=0.0, default=autosize)]
    """Enter the design heating capacity.Required field when the heating design capacity method"""

    Heating_Design_Capacity_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the heating design capacity per zone floor area.Required field when the heating design"""

    Fraction_Of_Autosized_Heating_Design_Capacity: Annotated[float, Field(ge=0.0, default=1.0)]
    """Enter the fraction of auto - sized heating design capacity.Required field when capacity the"""

    Temperature_Control_Type: Annotated[Literal['MeanAirTemperature', 'MeanRadiantTemperature', 'OperativeTemperature', 'OutdoorDryBulbTemperature', 'OutdoorWetBulbTemperature'], Field(default='MeanAirTemperature')]
    """Temperature used to control unit"""

    Heating_Throttling_Range: Annotated[str, Field(default='0')]

    Heating_Setpoint_Temperature_Schedule_Name: Annotated[str, Field(default=...)]