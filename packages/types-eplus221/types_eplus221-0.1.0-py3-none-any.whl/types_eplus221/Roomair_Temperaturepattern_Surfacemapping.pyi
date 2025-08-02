from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roomair_Temperaturepattern_Surfacemapping(EpBunch):
    """Defines a distribution pattern for the air temperatures adjacent to individual surfaces."""

    Name: Annotated[str, Field(default=...)]

    Control_Integer_For_Pattern_Control_Schedule_Name: Annotated[int, Field(default=...)]
    """reference this entry in schedule"""

    Thermostat_Offset: Annotated[str, Field()]
    """= (Temp at thermostat- Mean Air Temp)"""

    Return_Air_Offset: Annotated[str, Field()]
    """= (Tleaving - Mean Air Temp ) deg C"""

    Exhaust_Air_Offset: Annotated[str, Field()]
    """= (Texhaust - Mean Air Temp) deg C"""

    Surface_Name_Pair_1: Annotated[str, Field(default=...)]

    Delta_Adjacent_Air_Temperature_Pair_1: Annotated[float, Field(default=...)]

    Surface_Name_Pair_2: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_2: Annotated[float, Field()]

    Surface_Name_Pair_3: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_3: Annotated[float, Field()]

    Surface_Name_Pair_4: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_4: Annotated[float, Field()]

    Surface_Name_Pair_5: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_5: Annotated[float, Field()]

    Surface_Name_Pair_6: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_6: Annotated[float, Field()]

    Surface_Name_Pair_7: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_7: Annotated[float, Field()]

    Surface_Name_Pair_8: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_8: Annotated[float, Field()]

    Surface_Name_Pair_9: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_9: Annotated[float, Field()]

    Surface_Name_Pair_10: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_10: Annotated[float, Field()]

    Surface_Name_Pair_11: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_11: Annotated[float, Field()]

    Surface_Name_Pair_12: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_12: Annotated[float, Field()]

    Surface_Name_Pair_13: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_13: Annotated[float, Field()]

    Surface_Name_Pair_14: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_14: Annotated[float, Field()]

    Surface_Name_Pair_15: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_15: Annotated[float, Field()]

    Surface_Name_Pair_16: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_16: Annotated[float, Field()]

    Surface_Name_Pair_17: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_17: Annotated[float, Field()]

    Surface_Name_Pair_18: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_18: Annotated[float, Field()]

    Surface_Name_Pair_19: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_19: Annotated[float, Field()]

    Surface_Name_Pair_20: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_20: Annotated[float, Field()]

    Surface_Name_Pair_21: Annotated[str, Field()]

    Delta_Adjacent_Air_Temperature_Pair_21: Annotated[float, Field()]