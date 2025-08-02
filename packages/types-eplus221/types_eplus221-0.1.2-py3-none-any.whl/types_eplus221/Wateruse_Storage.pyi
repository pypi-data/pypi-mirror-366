from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Wateruse_Storage(EpBunch):
    """A water storage tank. If the building model is to include any on-site"""

    Name: Annotated[str, Field(default=...)]

    Water_Quality_Subcategory: Annotated[str, Field()]

    Maximum_Capacity: Annotated[float, Field()]
    """Defaults to unlimited capacity."""

    Initial_Volume: Annotated[float, Field()]

    Design_In_Flow_Rate: Annotated[float, Field()]
    """Defaults to unlimited flow."""

    Design_Out_Flow_Rate: Annotated[float, Field()]
    """Defaults to unlimited flow."""

    Overflow_Destination: Annotated[str, Field()]
    """If blank, overflow is discarded"""

    Type_of_Supply_Controlled_by_Float_Valve: Annotated[Literal['None', 'Mains', 'GroundwaterWell', 'OtherTank'], Field()]

    Float_Valve_On_Capacity: Annotated[float, Field()]
    """Lower range of target storage level e.g. float valve kicks on"""

    Float_Valve_Off_Capacity: Annotated[float, Field()]
    """Upper range of target storage level e.g. float valve kicks off"""

    Backup_Mains_Capacity: Annotated[float, Field()]
    """Lower range of secondary target storage level"""

    Other_Tank_Name: Annotated[str, Field()]

    Water_Thermal_Mode: Annotated[Literal['ScheduledTemperature', 'ThermalModel'], Field()]

    Water_Temperature_Schedule_Name: Annotated[str, Field(default=...)]

    Ambient_Temperature_Indicator: Annotated[Literal['Schedule', 'Zone', 'Outdoors'], Field()]

    Ambient_Temperature_Schedule_Name: Annotated[str, Field()]

    Zone_Name: Annotated[str, Field()]

    Tank_Surface_Area: Annotated[float, Field()]

    Tank_U_Value: Annotated[float, Field()]

    Tank_Outside_Surface_Material_Name: Annotated[str, Field()]