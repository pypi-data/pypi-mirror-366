from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac_Outdoorairsystem_Equipmentlist(EpBunch):
    """List equipment in simulation order"""

    Name: Annotated[str, Field(default=...)]

    Component_1_Object_Type: Annotated[str, Field(default=...)]

    Component_1_Name: Annotated[str, Field(default=...)]

    Component_2_Object_Type: Annotated[str, Field()]

    Component_2_Name: Annotated[str, Field()]

    Component_3_Object_Type: Annotated[str, Field()]

    Component_3_Name: Annotated[str, Field()]

    Component_4_Object_Type: Annotated[str, Field()]

    Component_4_Name: Annotated[str, Field()]

    Component_5_Object_Type: Annotated[str, Field()]

    Component_5_Name: Annotated[str, Field()]

    Component_6_Object_Type: Annotated[str, Field()]

    Component_6_Name: Annotated[str, Field()]

    Component_7_Object_Type: Annotated[str, Field()]

    Component_7_Name: Annotated[str, Field()]

    Component_8_Object_Type: Annotated[str, Field()]

    Component_8_Name: Annotated[str, Field()]

    Component_9_Object_Type: Annotated[str, Field()]

    Component_9_Name: Annotated[str, Field()]