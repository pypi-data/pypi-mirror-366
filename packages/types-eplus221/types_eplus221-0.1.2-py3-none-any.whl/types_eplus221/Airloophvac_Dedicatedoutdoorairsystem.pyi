from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac_Dedicatedoutdoorairsystem(EpBunch):
    """Defines a central forced air system to provide dedicated outdoor air to multiple"""

    Name: Annotated[str, Field(default=...)]

    AirLoopHVACOutdoorAirSystem_Name: Annotated[str, Field()]
    """Enter the name of an AirLoopHVAC:OutdoorAirSystem object."""

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    AirLoopHVACMixer_Name: Annotated[str, Field(default=...)]
    """Name of AirLoopHVAC:Mixer."""

    AirLoopHVACSplitter_Name: Annotated[str, Field(default=...)]
    """Name of AirLoopHVAC:Splitter."""

    Preheat_Design_Temperature: Annotated[float, Field(default=...)]

    Preheat_Design_Humidity_Ratio: Annotated[float, Field(default=...)]

    Precool_Design_Temperature: Annotated[float, Field(default=...)]

    Precool_Design_Humidity_Ratio: Annotated[float, Field(default=...)]

    Number_of_AirLoopHVAC: Annotated[int, Field(default=...)]
    """Enter the number of the AirLoopHAVC served by AirLoopHVAC:DedicatedOutdoorAirSystem"""

    AirLoopHVAC_1_Name: Annotated[str, Field()]
    """The rest of fields are extensible. It requires AirLoopHVAC names served by"""

    AirLoopHVAC_2_Name: Annotated[str, Field()]

    AirLoopHVAC_3_Name: Annotated[str, Field()]

    AirLoopHVAC_4_Name: Annotated[str, Field()]

    AirLoopHVAC_5_Name: Annotated[str, Field()]

    AirLoopHVAC_6_Name: Annotated[str, Field()]

    AirLoopHVAC_7_Name: Annotated[str, Field()]

    AirLoopHVAC_8_Name: Annotated[str, Field()]

    AirLoopHVAC_9_Name: Annotated[str, Field()]

    AirLoopHVAC_10_Name: Annotated[str, Field()]

    AirLoopHVAC_11_Name: Annotated[str, Field()]

    AirLoopHVAC_12_Name: Annotated[str, Field()]

    AirLoopHVAC_13_Name: Annotated[str, Field()]

    AirLoopHVAC_14_Name: Annotated[str, Field()]

    AirLoopHVAC_15_Name: Annotated[str, Field()]

    AirLoopHVAC_16_Name: Annotated[str, Field()]

    AirLoopHVAC_17_Name: Annotated[str, Field()]

    AirLoopHVAC_18_Name: Annotated[str, Field()]

    AirLoopHVAC_19_Name: Annotated[str, Field()]

    AirLoopHVAC_20_Name: Annotated[str, Field()]