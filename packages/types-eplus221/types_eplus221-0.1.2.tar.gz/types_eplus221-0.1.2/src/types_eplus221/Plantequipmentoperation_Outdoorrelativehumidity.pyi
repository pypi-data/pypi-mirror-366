from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Plantequipmentoperation_Outdoorrelativehumidity(EpBunch):
    """Plant equipment operation scheme for outdoor relative humidity range operation."""

    Name: Annotated[str, Field(default=...)]

    Relative_Humidity_Range_1_Lower_Limit: Annotated[float, Field(default=..., ge=0.0, le=100.0)]

    Relative_Humidity_Range_1_Upper_Limit: Annotated[float, Field(default=..., ge=0.0, le=100.0)]

    Range_1_Equipment_List_Name: Annotated[str, Field(default=...)]

    Relative_Humidity_Range_2_Lower_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Relative_Humidity_Range_2_Upper_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Range_2_Equipment_List_Name: Annotated[str, Field()]

    Relative_Humidity_Range_3_Lower_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Relative_Humidity_Range_3_Upper_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Range_3_Equipment_List_Name: Annotated[str, Field()]

    Relative_Humidity_Range_4_Lower_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Relative_Humidity_Range_4_Upper_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Range_4_Equipment_List_Name: Annotated[str, Field()]

    Relative_Humidity_Range_5_Lower_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Relative_Humidity_Range_5_Upper_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Range_5_Equipment_List_Name: Annotated[str, Field()]

    Relative_Humidity_Range_6_Lower_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Relative_Humidity_Range_6_Upper_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Range_6_Equipment_List_Name: Annotated[str, Field()]

    Relative_Humidity_Range_7_Lower_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Relative_Humidity_Range_7_Upper_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Range_7_Equipment_List_Name: Annotated[str, Field()]

    Relative_Humidity_Range_8_Lower_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Relative_Humidity_Range_8_Upper_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Range_8_Equipment_List_Name: Annotated[str, Field()]

    Relative_Humidity_Range_9_Lower_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Relative_Humidity_Range_9_Upper_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Range_9_Equipment_List_Name: Annotated[str, Field()]

    Relative_Humidity_Range_10_Lower_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Relative_Humidity_Range_10_Upper_Limit: Annotated[float, Field(ge=0.0, le=100.0)]

    Range_10_Equipment_List_Name: Annotated[str, Field()]