from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Dehumidifier_Dx(EpBunch):
    """This object calculates the performance of zone (room) air dehumidifiers."""

    Name: Annotated[str, Field(default=...)]
    """Unique name for this direct expansion (DX) zone dehumidifier object."""

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Air inlet node for the dehumidifier must be a zone air exhaust node."""

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """Air outlet node for the dehumidifier must be a zone air inlet node."""

    Rated_Water_Removal: Annotated[float, Field(default=..., gt=0.0)]
    """Rating point: air entering dehumidifier at 26.7 C (80 F) dry-bulb and 60% relative humidity."""

    Rated_Energy_Factor: Annotated[float, Field(default=..., gt=0.0)]
    """Rating point: air entering dehumidifier at 26.7 C (80 F) dry-bulb and 60% relative humidity."""

    Rated_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Water_Removal_Curve_Name: Annotated[str, Field(default=...)]
    """Name of a curve that describes the water removal rate (normalized to rated conditions)"""

    Energy_Factor_Curve_Name: Annotated[str, Field(default=...)]
    """Name of a curve that describes the energy factor (normalized to rated conditions)"""

    Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field(default=...)]
    """Name of a curve that describes the part load fraction (PLF) of the system as"""

    Minimum_Dry_Bulb_Temperature_For_Dehumidifier_Operation: Annotated[float, Field(default=10.0)]
    """Dehumidifier shut off if inlet air (zone) temperature is below this value."""

    Maximum_Dry_Bulb_Temperature_For_Dehumidifier_Operation: Annotated[float, Field(default=35.0)]
    """Dehumidifier shut off if inlet air (zone) temperature is above this value."""

    Off_Cycle_Parasitic_Electric_Load: Annotated[float, Field(ge=0.0, default=0.0)]
    """Parasitic electric power consumed when the dehumidifier is available to operate, but"""

    Condensate_Collection_Water_Storage_Tank_Name: Annotated[str, Field()]
    """Name of storage tank used to collect water removed by the dehumidifier."""