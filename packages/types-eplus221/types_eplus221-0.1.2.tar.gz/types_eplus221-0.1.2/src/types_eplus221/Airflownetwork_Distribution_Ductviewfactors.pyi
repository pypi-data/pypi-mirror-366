from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Distribution_Ductviewfactors(EpBunch):
    """This object is used to allow user-defined view factors to be used for duct-surface radiation"""

    Linkage_Name: Annotated[str, Field(default=...)]

    Duct_Surface_Exposure_Fraction: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Duct_Surface_Emittance: Annotated[float, Field(ge=0.0, le=1.0, default=0.9)]

    Surface_1_Name: Annotated[str, Field()]

    Surface_1_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_2_Name: Annotated[str, Field()]

    Surface_2_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_3_Name: Annotated[str, Field()]

    Surface_3_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_4_Name: Annotated[str, Field()]

    Surface_4_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_5_Name: Annotated[str, Field()]

    Surface_5_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_6_Name: Annotated[str, Field()]

    Surface_6_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_7_Name: Annotated[str, Field()]

    Surface_7_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_8_Name: Annotated[str, Field()]

    Surface_8_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_9_Name: Annotated[str, Field()]

    Surface_9_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_10_Name: Annotated[str, Field()]

    Surface_10_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_11_Name: Annotated[str, Field()]

    Surface_11_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_12_Name: Annotated[str, Field()]

    Surface_12_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_13_Name: Annotated[str, Field()]

    Surface_13_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_14_Name: Annotated[str, Field()]

    Surface_14_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_15_Name: Annotated[str, Field()]

    Surface_15_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_16_Name: Annotated[str, Field()]

    Surface_16_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_17_Name: Annotated[str, Field()]

    Surface_17_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_18_Name: Annotated[str, Field()]

    Surface_18_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_19_Name: Annotated[str, Field()]

    Surface_19_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_20_Name: Annotated[str, Field()]

    Surface_20_View_Factor: Annotated[float, Field(ge=0.0, le=1.0)]