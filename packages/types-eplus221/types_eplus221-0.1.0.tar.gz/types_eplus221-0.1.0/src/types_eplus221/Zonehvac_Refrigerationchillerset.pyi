from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Refrigerationchillerset(EpBunch):
    """Works in conjunction with one or multiple air chillers, compressor racks,"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Zone_Name: Annotated[str, Field()]
    """This must be a controlled zone and appear in a ZoneHVAC:EquipmentConnections object."""

    Air_Inlet_Node_Name: Annotated[str, Field()]
    """Not used - reserved for future use"""

    Air_Outlet_Node_Name: Annotated[str, Field()]
    """Not used - reserved for future use"""

    Air_Chiller_1_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_2_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_3_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_4_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_5_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_6_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_7_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_8_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_9_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_10_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_11_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_12_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_13_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_14_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_15_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_16_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_17_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_18_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_19_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_20_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_21_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_22_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_23_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_24_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_25_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_26_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_27_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_28_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_29_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_30_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_31_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_32_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_33_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_34_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_35_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_36_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_37_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_38_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_39_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_40_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_41_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_42_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_43_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_44_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_45_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_46_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_47_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_48_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_49_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_50_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_51_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_52_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_53_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_54_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_55_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_56_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_57_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_58_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_59_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_60_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_61_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_62_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_63_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_64_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_65_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_66_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_67_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_68_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_69_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_70_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_71_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_72_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_73_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_74_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_75_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_76_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_77_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_78_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_79_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_80_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_81_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_82_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_83_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_84_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_85_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_86_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_87_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_88_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_89_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_90_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_91_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_92_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_93_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_94_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""

    Air_Chiller_95_Name: Annotated[str, Field()]
    """This is the first chiller turned on to meet the zone load"""