from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Plantequipmentoperation_Outdoordrybulb(EpBunch):
    """Plant equipment operation scheme for outdoor dry-bulb temperature range operation."""

    Name: Annotated[str, Field(default=...)]

    DryBulb_Temperature_Range_1_Lower_Limit: Annotated[float, Field(default=..., ge=-70, le=70)]

    DryBulb_Temperature_Range_1_Upper_Limit: Annotated[float, Field(default=..., ge=-70, le=70)]

    Range_1_Equipment_List_Name: Annotated[str, Field(default=...)]

    DryBulb_Temperature_Range_2_Lower_Limit: Annotated[float, Field(ge=-70, le=70)]

    DryBulb_Temperature_Range_2_Upper_Limit: Annotated[float, Field(ge=-70, le=70)]

    Range_2_Equipment_List_Name: Annotated[str, Field()]

    DryBulb_Temperature_Range_3_Lower_Limit: Annotated[float, Field(ge=-70, le=70)]

    DryBulb_Temperature_Range_3_Upper_Limit: Annotated[float, Field(ge=-70, le=70)]

    Range_3_Equipment_List_Name: Annotated[str, Field()]

    DryBulb_Temperature_Range_4_Lower_Limit: Annotated[float, Field(ge=-70, le=70)]

    DryBulb_Temperature_Range_4_Upper_Limit: Annotated[float, Field(ge=-70, le=70)]

    Range_4_Equipment_List_Name: Annotated[str, Field()]

    DryBulb_Temperature_Range_5_Lower_Limit: Annotated[float, Field(ge=-70, le=70)]

    DryBulb_Temperature_Range_5_Upper_Limit: Annotated[float, Field(ge=-70, le=70)]

    Range_5_Equipment_List_Name: Annotated[str, Field()]

    DryBulb_Temperature_Range_6_Lower_Limit: Annotated[float, Field(ge=-70, le=70)]

    DryBulb_Temperature_Range_6_Upper_Limit: Annotated[float, Field(ge=-70, le=70)]

    Range_6_Equipment_List_Name: Annotated[str, Field()]

    DryBulb_Temperature_Range_7_Lower_Limit: Annotated[float, Field(ge=-70, le=70)]

    DryBulb_Temperature_Range_7_Upper_Limit: Annotated[float, Field(ge=-70, le=70)]

    Range_7_Equipment_List_Name: Annotated[str, Field()]

    DryBulb_Temperature_Range_8_Lower_Limit: Annotated[float, Field(ge=-70, le=70)]

    DryBulb_Temperature_Range_8_Upper_Limit: Annotated[float, Field(ge=-70, le=70)]

    Range_8_Equipment_List_Name: Annotated[str, Field()]

    DryBulb_Temperature_Range_9_Lower_Limit: Annotated[float, Field(ge=-70, le=70)]

    DryBulb_Temperature_Range_9_Upper_Limit: Annotated[float, Field(ge=-70, le=70)]

    Range_9_Equipment_List_Name: Annotated[str, Field()]

    DryBulb_Temperature_Range_10_Lower_Limit: Annotated[float, Field(ge=-70, le=70)]

    DryBulb_Temperature_Range_10_Upper_Limit: Annotated[float, Field(ge=-70, le=70)]

    Range_10_Equipment_List_Name: Annotated[str, Field()]