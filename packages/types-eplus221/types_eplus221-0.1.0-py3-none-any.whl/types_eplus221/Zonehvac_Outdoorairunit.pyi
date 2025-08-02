from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Outdoorairunit(EpBunch):
    """The zone outdoor air unit models a single-zone dedicated outdoor air system (DOAS)."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Zone_Name: Annotated[str, Field(default=...)]
    """(name of zone system is serving)"""

    Outdoor_Air_Flow_Rate: Annotated[str, Field(default=...)]

    Outdoor_Air_Schedule_Name: Annotated[str, Field(default=...)]

    Supply_Fan_Name: Annotated[str, Field(default=...)]
    """Allowable fan types are Fan:SystemModel and Fan:ConstantVolume and Fan:VariableVolume"""

    Supply_Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='DrawThrough')]

    Exhaust_Fan_Name: Annotated[str, Field()]
    """Allowable fan types are Fan:ConstantVolume and"""

    Exhaust_Air_Flow_Rate: Annotated[str, Field()]

    Exhaust_Air_Schedule_Name: Annotated[str, Field()]

    Unit_Control_Type: Annotated[Literal['NeutralControl', 'TemperatureControl'], Field(default='NeutralControl')]

    High_Air_Control_Temperature_Schedule_Name: Annotated[str, Field()]
    """Air and control temperatures for cooling. If outdoor air temperature"""

    Low_Air_Control_Temperature_Schedule_Name: Annotated[str, Field()]
    """Air and control temperatures for Heating. If outdoor air temperature"""

    Outdoor_Air_Node_Name: Annotated[str, Field(default=...)]

    Airoutlet_Node_Name: Annotated[str, Field(default=...)]

    Airinlet_Node_Name: Annotated[str, Field()]
    """air leaves zone"""

    Supply_Fanoutlet_Node_Name: Annotated[str, Field(default=...)]

    Outdoor_Air_Unit_List_Name: Annotated[str, Field(default=...)]
    """Enter the name of an ZoneHVAC:OutdoorAirUnit:EquipmentList object."""

    Availability_Manager_List_Name: Annotated[str, Field()]
    """Enter the name of an AvailabilityManagerAssignmentList object."""