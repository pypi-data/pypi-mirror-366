from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac_Dedicatedoutdoorairsystem(EpBunch):
    """Defines a central forced air system to provide dedicated outdoor air to multiple"""

    Name: Annotated[str, Field(default=...)]

    Airloophvac_Outdoorairsystem_Name: Annotated[str, Field()]
    """Enter the name of an AirLoopHVAC:OutdoorAirSystem object."""

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Airloophvac_Mixer_Name: Annotated[str, Field(default=...)]
    """Name of AirLoopHVAC:Mixer."""

    Airloophvac_Splitter_Name: Annotated[str, Field(default=...)]
    """Name of AirLoopHVAC:Splitter."""

    Preheat_Design_Temperature: Annotated[float, Field(default=...)]

    Preheat_Design_Humidity_Ratio: Annotated[float, Field(default=...)]

    Precool_Design_Temperature: Annotated[float, Field(default=...)]

    Precool_Design_Humidity_Ratio: Annotated[float, Field(default=...)]

    Number_Of_Airloophvac: Annotated[int, Field(default=...)]
    """Enter the number of the AirLoopHAVC served by AirLoopHVAC:DedicatedOutdoorAirSystem"""

    Airloophvac_1_Name: Annotated[str, Field()]
    """The rest of fields are extensible. It requires AirLoopHVAC names served by"""

    Airloophvac_2_Name: Annotated[str, Field()]

    Airloophvac_3_Name: Annotated[str, Field()]

    Airloophvac_4_Name: Annotated[str, Field()]

    Airloophvac_5_Name: Annotated[str, Field()]

    Airloophvac_6_Name: Annotated[str, Field()]

    Airloophvac_7_Name: Annotated[str, Field()]

    Airloophvac_8_Name: Annotated[str, Field()]

    Airloophvac_9_Name: Annotated[str, Field()]

    Airloophvac_10_Name: Annotated[str, Field()]

    Airloophvac_11_Name: Annotated[str, Field()]

    Airloophvac_12_Name: Annotated[str, Field()]

    Airloophvac_13_Name: Annotated[str, Field()]

    Airloophvac_14_Name: Annotated[str, Field()]

    Airloophvac_15_Name: Annotated[str, Field()]

    Airloophvac_16_Name: Annotated[str, Field()]

    Airloophvac_17_Name: Annotated[str, Field()]

    Airloophvac_18_Name: Annotated[str, Field()]

    Airloophvac_19_Name: Annotated[str, Field()]

    Airloophvac_20_Name: Annotated[str, Field()]