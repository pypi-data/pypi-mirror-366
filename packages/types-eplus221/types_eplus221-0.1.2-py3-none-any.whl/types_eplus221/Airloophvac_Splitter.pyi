from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac_Splitter(EpBunch):
    """Split one air stream from AirLoopHVAC:DedicatedOutdoorAirSystem outlet node into N"""

    Name: Annotated[str, Field(default=...)]

    Inlet_Node_Name: Annotated[str, Field(default=...)]

    Outlet_1_Node_Name: Annotated[str, Field(default=...)]

    Outlet_2_Node_Name: Annotated[str, Field()]

    Outlet_3_Node_Name: Annotated[str, Field()]

    Outlet_4_Node_Name: Annotated[str, Field()]

    Outlet_5_Node_Name: Annotated[str, Field()]

    Outlet_6_Node_Name: Annotated[str, Field()]

    Outlet_7_Node_Name: Annotated[str, Field()]

    Outlet_8_Node_Name: Annotated[str, Field()]

    Outlet_9_Node_Name: Annotated[str, Field()]

    Outlet_10_Node_Name: Annotated[str, Field()]

    Outlet_11_Node_Name: Annotated[str, Field()]

    Outlet_12_Node_Name: Annotated[str, Field()]

    Outlet_13_Node_Name: Annotated[str, Field()]

    Outlet_14_Node_Name: Annotated[str, Field()]

    Outlet_15_Node_Name: Annotated[str, Field()]

    Outlet_16_Node_Name: Annotated[str, Field()]

    Outlet_17_Node_Name: Annotated[str, Field()]

    Outlet_18_Node_Name: Annotated[str, Field()]

    Outlet_19_Node_Name: Annotated[str, Field()]

    Outlet_20_Node_Name: Annotated[str, Field()]

    Outlet_21_Node_Name: Annotated[str, Field()]

    Outlet_22_Node_Name: Annotated[str, Field()]

    Outlet_23_Node_Name: Annotated[str, Field()]

    Outlet_24_Node_Name: Annotated[str, Field()]

    Outlet_25_Node_Name: Annotated[str, Field()]

    Outlet_26_Node_Name: Annotated[str, Field()]

    Outlet_27_Node_Name: Annotated[str, Field()]

    Outlet_28_Node_Name: Annotated[str, Field()]

    Outlet_29_Node_Name: Annotated[str, Field()]

    Outlet_30_Node_Name: Annotated[str, Field()]

    Outlet_31_Node_Name: Annotated[str, Field()]

    Outlet_32_Node_Name: Annotated[str, Field()]

    Outlet_33_Node_Name: Annotated[str, Field()]

    Outlet_34_Node_Name: Annotated[str, Field()]

    Outlet_35_Node_Name: Annotated[str, Field()]

    Outlet_36_Node_Name: Annotated[str, Field()]

    Outlet_37_Node_Name: Annotated[str, Field()]

    Outlet_38_Node_Name: Annotated[str, Field()]

    Outlet_39_Node_Name: Annotated[str, Field()]

    Outlet_40_Node_Name: Annotated[str, Field()]

    Outlet_41_Node_Name: Annotated[str, Field()]

    Outlet_42_Node_Name: Annotated[str, Field()]

    Outlet_43_Node_Name: Annotated[str, Field()]

    Outlet_44_Node_Name: Annotated[str, Field()]

    Outlet_45_Node_Name: Annotated[str, Field()]

    Outlet_46_Node_Name: Annotated[str, Field()]

    Outlet_47_Node_Name: Annotated[str, Field()]

    Outlet_48_Node_Name: Annotated[str, Field()]

    Outlet_49_Node_Name: Annotated[str, Field()]

    Outlet_50_Node_Name: Annotated[str, Field()]