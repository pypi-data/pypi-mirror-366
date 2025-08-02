from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac_Mixer(EpBunch):
    """Mix N inlet air streams from Relief Air Stream Node in OutdoorAir:Mixer objects"""

    Name: Annotated[str, Field(default=...)]

    Outlet_Node_Name: Annotated[str, Field(default=...)]

    Inlet_1_Node_Name: Annotated[str, Field(default=...)]

    Inlet_2_Node_Name: Annotated[str, Field()]

    Inlet_3_Node_Name: Annotated[str, Field()]

    Inlet_4_Node_Name: Annotated[str, Field()]

    Inlet_5_Node_Name: Annotated[str, Field()]

    Inlet_6_Node_Name: Annotated[str, Field()]

    Inlet_7_Node_Name: Annotated[str, Field()]

    Inlet_8_Node_Name: Annotated[str, Field()]

    Inlet_9_Node_Name: Annotated[str, Field()]

    Inlet_10_Node_Name: Annotated[str, Field()]

    Inlet_11_Node_Name: Annotated[str, Field()]

    Inlet_12_Node_Name: Annotated[str, Field()]

    Inlet_13_Node_Name: Annotated[str, Field()]

    Inlet_14_Node_Name: Annotated[str, Field()]

    Inlet_15_Node_Name: Annotated[str, Field()]

    Inlet_16_Node_Name: Annotated[str, Field()]

    Inlet_17_Node_Name: Annotated[str, Field()]

    Inlet_18_Node_Name: Annotated[str, Field()]

    Inlet_19_Node_Name: Annotated[str, Field()]

    Inlet_20_Node_Name: Annotated[str, Field()]

    Inlet_21_Node_Name: Annotated[str, Field()]

    Inlet_22_Node_Name: Annotated[str, Field()]

    Inlet_23_Node_Name: Annotated[str, Field()]

    Inlet_24_Node_Name: Annotated[str, Field()]

    Inlet_25_Node_Name: Annotated[str, Field()]

    Inlet_26_Node_Name: Annotated[str, Field()]

    Inlet_27_Node_Name: Annotated[str, Field()]

    Inlet_28_Node_Name: Annotated[str, Field()]

    Inlet_29_Node_Name: Annotated[str, Field()]

    Inlet_30_Node_Name: Annotated[str, Field()]

    Inlet_31_Node_Name: Annotated[str, Field()]

    Inlet_32_Node_Name: Annotated[str, Field()]

    Inlet_33_Node_Name: Annotated[str, Field()]

    Inlet_34_Node_Name: Annotated[str, Field()]

    Inlet_35_Node_Name: Annotated[str, Field()]

    Inlet_36_Node_Name: Annotated[str, Field()]

    Inlet_37_Node_Name: Annotated[str, Field()]

    Inlet_38_Node_Name: Annotated[str, Field()]

    Inlet_39_Node_Name: Annotated[str, Field()]

    Inlet_40_Node_Name: Annotated[str, Field()]

    Inlet_41_Node_Name: Annotated[str, Field()]

    Inlet_42_Node_Name: Annotated[str, Field()]

    Inlet_43_Node_Name: Annotated[str, Field()]

    Inlet_44_Node_Name: Annotated[str, Field()]

    Inlet_45_Node_Name: Annotated[str, Field()]

    Inlet_46_Node_Name: Annotated[str, Field()]

    Inlet_47_Node_Name: Annotated[str, Field()]

    Inlet_48_Node_Name: Annotated[str, Field()]

    Inlet_49_Node_Name: Annotated[str, Field()]

    Inlet_50_Node_Name: Annotated[str, Field()]