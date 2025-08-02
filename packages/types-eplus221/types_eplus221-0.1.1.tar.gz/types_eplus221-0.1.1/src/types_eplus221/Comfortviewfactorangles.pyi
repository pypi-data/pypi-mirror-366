from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Comfortviewfactorangles(EpBunch):
    """Used to specify radiant view factors for thermal comfort calculations."""

    Name: Annotated[str, Field()]

    Zone_Name: Annotated[str, Field()]

    Surface_1_Name: Annotated[str, Field()]

    Angle_Factor_1: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_2_Name: Annotated[str, Field()]

    Angle_Factor_2: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_3_Name: Annotated[str, Field()]

    Angle_Factor_3: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_4_Name: Annotated[str, Field()]

    Angle_Factor_4: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_5_Name: Annotated[str, Field()]

    Angle_Factor_5: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_6_Name: Annotated[str, Field()]

    Angle_Factor_6: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_7_Name: Annotated[str, Field()]

    Angle_Factor_7: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_8_Name: Annotated[str, Field()]

    Angle_Factor_8: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_9_Name: Annotated[str, Field()]

    Angle_Factor_9: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_10_Name: Annotated[str, Field()]

    Angle_Factor_10: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_11_Name: Annotated[str, Field()]

    Angle_Factor_11: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_12_Name: Annotated[str, Field()]

    Angle_Factor_12: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_13_Name: Annotated[str, Field()]

    Angle_Factor_13: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_14_Name: Annotated[str, Field()]

    Angle_Factor_14: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_15_Name: Annotated[str, Field()]

    Angle_Factor_15: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_16_Name: Annotated[str, Field()]

    Angle_Factor_16: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_17_Name: Annotated[str, Field()]

    Angle_Factor_17: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_18_Name: Annotated[str, Field()]

    Angle_Factor_18: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_19_Name: Annotated[str, Field()]

    Angle_Factor_19: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_20_Name: Annotated[str, Field()]

    Angle_Factor_20: Annotated[float, Field(ge=0.0, le=1.0)]