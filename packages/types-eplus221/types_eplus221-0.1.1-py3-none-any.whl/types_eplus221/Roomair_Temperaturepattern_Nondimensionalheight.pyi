from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roomair_Temperaturepattern_Nondimensionalheight(EpBunch):
    """Defines a distribution pattern for air temperatures relative to the current mean air"""

    Name: Annotated[str, Field(default=...)]

    Control_Integer_For_Pattern_Control_Schedule_Name: Annotated[int, Field(default=...)]
    """this value should appear in as a schedule value"""

    Thermostat_Offset: Annotated[float, Field()]
    """= (Temp at thermostat- Mean Air Temp)"""

    Return_Air_Offset: Annotated[float, Field()]
    """= (Temp leaving - Mean Air Temp ) deg C"""

    Exhaust_Air_Offset: Annotated[float, Field()]
    """= (Temp exhaust - Mean Air Temp) deg C"""

    Pair_1_Zeta_Nondimensional_Height: Annotated[float, Field(default=...)]

    Pair_1_Delta_Adjacent_Air_Temperature: Annotated[float, Field(default=..., ge=-10.0, le=20.0)]

    Pair_2_Zeta_Nondimensional_Height: Annotated[float, Field(default=...)]

    Pair_2_Delta_Adjacent_Air_Temperature: Annotated[float, Field(default=..., ge=-10.0, le=20.0)]

    Pair_3_Zeta_Nondimensional_Height: Annotated[float, Field()]

    Pair_3_Delta_Adjacent_Air_Temperature: Annotated[float, Field(ge=-10.0, le=20.0)]

    Pair_4_Zeta_Nondimensional_Height: Annotated[float, Field()]

    Pair_4_Delta_Adjacent_Air_Temperature: Annotated[float, Field(ge=-10.0, le=20.0)]

    Pair_5_Zeta_Nondimensional_Height: Annotated[float, Field()]

    Pair_5_Delta_Adjacent_Air_Temperature: Annotated[float, Field(ge=-10.0, le=20.0)]

    Pair_6_Zeta_Nondimensional_Height: Annotated[float, Field()]

    Pair_6_Delta_Adjacent_Air_Temperature: Annotated[float, Field(ge=-10.0, le=20.0)]

    Pair_7_Zeta_Nondimensional_Height: Annotated[float, Field()]

    Pair_7_Delta_Adjacent_Air_Temperature: Annotated[float, Field(ge=-10.0, le=20.0)]

    Pair_8_Zeta_Nondimensional_Height: Annotated[float, Field()]

    Pair_8_Delta_Adjacent_Air_Temperature: Annotated[float, Field(ge=-10.0, le=20.0)]

    Pair_9_Zeta_Nondimensional_Height: Annotated[float, Field()]

    Pair_9_Delta_Adjacent_Air_Temperature: Annotated[float, Field(ge=-10.0, le=20.0)]

    Pair_10_Zeta_Nondimensional_Height: Annotated[float, Field()]

    Pair_10_Delta_Adjacent_Air_Temperature: Annotated[float, Field(ge=-10.0, le=20.0)]

    Pair_11_Zeta_Nondimensional_Height: Annotated[float, Field()]

    Pair_11_Delta_Adjacent_Air_Temperature: Annotated[float, Field(ge=-10.0, le=20.0)]

    Pair_12_Zeta_Nondimensional_Height: Annotated[float, Field()]

    Pair_12_Delta_Adjacent_Air_Temperature: Annotated[float, Field(ge=-10.0, le=20.0)]

    Pair_13_Zeta_Nondimensional_Height: Annotated[float, Field()]

    Pair_13_Delta_Adjacent_Air_Temperature: Annotated[float, Field(ge=-10.0, le=20.0)]

    Pair_14_Zeta_Nondimensional_Height: Annotated[float, Field()]

    Pair_14_Delta_Adjacent_Air_Temperature: Annotated[float, Field(ge=-10.0, le=20.0)]

    Pair_15_Zeta_Nondimensional_Height: Annotated[float, Field()]

    Pair_15_Delta_Adjacent_Air_Temperature: Annotated[float, Field(ge=-10.0, le=20.0)]

    Pair_16_Zeta_Nondimensional_Height: Annotated[float, Field()]

    Pair_16_Delta_Adjacent_Air_Temperature: Annotated[float, Field(ge=-10.0, le=20.0)]

    Pair_17_Zeta_Nondimensional_Height: Annotated[float, Field()]

    Pair_17_Delta_Adjacent_Air_Temperature: Annotated[float, Field(ge=-10.0, le=20.0)]

    Pair_18_Zeta_Nondimensional_Height: Annotated[float, Field()]

    Pair_18_Delta_Adjacent_Air_Temperature: Annotated[float, Field(ge=-10.0, le=20.0)]

    Pair_19_Zeta_Nondimensional_Height: Annotated[float, Field()]

    Pair_19_Delta_Adjacent_Air_Temperature: Annotated[float, Field(ge=-10.0, le=20.0)]