from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zoneterminalunitlist(EpBunch):
    """List of variable refrigerant flow (VRF) terminal units served by a given VRF condensing"""

    Zone_Terminal_Unit_List_Name: Annotated[str, Field(default=...)]

    Zone_Terminal_Unit_Name_1: Annotated[str, Field(default=...)]

    Zone_Terminal_Unit_Name_2: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_3: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_4: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_5: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_6: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_7: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_8: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_9: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_10: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_11: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_12: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_13: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_14: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_15: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_16: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_17: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_18: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_19: Annotated[str, Field()]

    Zone_Terminal_Unit_Name_20: Annotated[str, Field()]