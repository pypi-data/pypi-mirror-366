from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Shading_Zone_Detailed(EpBunch):
    """used For fins, overhangs, elements that shade the building, are attached to the building"""

    Name: Annotated[str, Field(default=...)]

    Base_Surface_Name: Annotated[str, Field(default=...)]

    Transmittance_Schedule_Name: Annotated[str, Field()]
    """Transmittance schedule for the shading device, defaults to zero (always opaque)"""

    Number_Of_Vertices: Annotated[str, Field(default='autocalculate')]
    """shown with 6 vertex coordinates -- extensible object"""

    Vertex_1_X_Coordinate: Annotated[float, Field(default=...)]

    Vertex_1_Y_Coordinate: Annotated[float, Field(default=...)]

    Vertex_1_Z_Coordinate: Annotated[float, Field(default=...)]

    Vertex_2_X_Coordinate: Annotated[float, Field(default=...)]

    Vertex_2_Y_Coordinate: Annotated[float, Field(default=...)]

    Vertex_2_Z_Coordinate: Annotated[float, Field(default=...)]

    Vertex_3_X_Coordinate: Annotated[float, Field(default=...)]

    Vertex_3_Y_Coordinate: Annotated[float, Field(default=...)]

    Vertex_3_Z_Coordinate: Annotated[float, Field(default=...)]

    Vertex_4_X_Coordinate: Annotated[float, Field()]

    Vertex_4_Y_Coordinate: Annotated[float, Field()]

    Vertex_4_Z_Coordinate: Annotated[float, Field()]

    Vertex_5_X_Coordinate: Annotated[float, Field()]

    Vertex_5_Y_Coordinate: Annotated[float, Field()]

    Vertex_5_Z_Coordinate: Annotated[float, Field()]

    Vertex_6_X_Coordinate: Annotated[float, Field()]

    Vertex_6_Y_Coordinate: Annotated[float, Field()]

    Vertex_6_Z_Coordinate: Annotated[float, Field()]

    Vertex_7_X_Coordinate: Annotated[float, Field()]

    Vertex_7_Y_Coordinate: Annotated[float, Field()]

    Vertex_7_Z_Coordinate: Annotated[float, Field()]

    Vertex_8_X_Coordinate: Annotated[float, Field()]

    Vertex_8_Y_Coordinate: Annotated[float, Field()]

    Vertex_8_Z_Coordinate: Annotated[float, Field()]

    Vertex_9_X_Coordinate: Annotated[float, Field()]

    Vertex_9_Y_Coordinate: Annotated[float, Field()]

    Vertex_9_Z_Coordinate: Annotated[float, Field()]

    Vertex_10_X_Coordinate: Annotated[float, Field()]

    Vertex_10_Y_Coordinate: Annotated[float, Field()]

    Vertex_10_Z_Coordinate: Annotated[float, Field()]

    Vertex_11_X_Coordinate: Annotated[float, Field()]

    Vertex_11_Y_Coordinate: Annotated[float, Field()]

    Vertex_11_Z_Coordinate: Annotated[float, Field()]

    Vertex_12_X_Coordinate: Annotated[float, Field()]

    Vertex_12_Y_Coordinate: Annotated[float, Field()]

    Vertex_12_Z_Coordinate: Annotated[float, Field()]

    Vertex_13_X_Coordinate: Annotated[float, Field()]

    Vertex_13_Y_Coordinate: Annotated[float, Field()]

    Vertex_13_Z_Coordinate: Annotated[float, Field()]

    Vertex_14_X_Coordinate: Annotated[float, Field()]

    Vertex_14_Y_Coordinate: Annotated[float, Field()]

    Vertex_14_Z_Coordinate: Annotated[float, Field()]

    Vertex_15_X_Coordinate: Annotated[float, Field()]

    Vertex_15_Y_Coordinate: Annotated[float, Field()]

    Vertex_15_Z_Coordinate: Annotated[float, Field()]

    Vertex_16_X_Coordinate: Annotated[float, Field()]

    Vertex_16_Y_Coordinate: Annotated[float, Field()]

    Vertex_16_Z_Coordinate: Annotated[float, Field()]

    Vertex_17_X_Coordinate: Annotated[float, Field()]

    Vertex_17_Y_Coordinate: Annotated[float, Field()]

    Vertex_17_Z_Coordinate: Annotated[float, Field()]

    Vertex_18_X_Coordinate: Annotated[float, Field()]

    Vertex_18_Y_Coordinate: Annotated[float, Field()]

    Vertex_18_Z_Coordinate: Annotated[float, Field()]

    Vertex_19_X_Coordinate: Annotated[float, Field()]

    Vertex_19_Y_Coordinate: Annotated[float, Field()]

    Vertex_19_Z_Coordinate: Annotated[float, Field()]

    Vertex_20_X_Coordinate: Annotated[float, Field()]

    Vertex_20_Y_Coordinate: Annotated[float, Field()]

    Vertex_20_Z_Coordinate: Annotated[float, Field()]

    Vertex_21_X_Coordinate: Annotated[float, Field()]

    Vertex_21_Y_Coordinate: Annotated[float, Field()]

    Vertex_21_Z_Coordinate: Annotated[float, Field()]

    Vertex_22_X_Coordinate: Annotated[float, Field()]

    Vertex_22_Y_Coordinate: Annotated[float, Field()]

    Vertex_22_Z_Coordinate: Annotated[float, Field()]

    Vertex_23_X_Coordinate: Annotated[float, Field()]

    Vertex_23_Y_Coordinate: Annotated[float, Field()]

    Vertex_23_Z_Coordinate: Annotated[float, Field()]

    Vertex_24_X_Coordinate: Annotated[float, Field()]

    Vertex_24_Y_Coordinate: Annotated[float, Field()]

    Vertex_24_Z_Coordinate: Annotated[float, Field()]

    Vertex_25_X_Coordinate: Annotated[float, Field()]

    Vertex_25_Y_Coordinate: Annotated[float, Field()]

    Vertex_25_Z_Coordinate: Annotated[float, Field()]

    Vertex_26_X_Coordinate: Annotated[float, Field()]

    Vertex_26_Y_Coordinate: Annotated[float, Field()]

    Vertex_26_Z_Coordinate: Annotated[float, Field()]

    Vertex_27_X_Coordinate: Annotated[float, Field()]

    Vertex_27_Y_Coordinate: Annotated[float, Field()]

    Vertex_27_Z_Coordinate: Annotated[float, Field()]

    Vertex_28_X_Coordinate: Annotated[float, Field()]

    Vertex_28_Y_Coordinate: Annotated[float, Field()]

    Vertex_28_Z_Coordinate: Annotated[float, Field()]

    Vertex_29_X_Coordinate: Annotated[float, Field()]

    Vertex_29_Y_Coordinate: Annotated[float, Field()]

    Vertex_29_Z_Coordinate: Annotated[float, Field()]

    Vertex_30_X_Coordinate: Annotated[float, Field()]

    Vertex_30_Y_Coordinate: Annotated[float, Field()]

    Vertex_30_Z_Coordinate: Annotated[float, Field()]

    Vertex_31_X_Coordinate: Annotated[float, Field()]

    Vertex_31_Y_Coordinate: Annotated[float, Field()]

    Vertex_31_Z_Coordinate: Annotated[float, Field()]

    Vertex_32_X_Coordinate: Annotated[float, Field()]

    Vertex_32_Y_Coordinate: Annotated[float, Field()]

    Vertex_32_Z_Coordinate: Annotated[float, Field()]

    Vertex_33_X_Coordinate: Annotated[float, Field()]

    Vertex_33_Y_Coordinate: Annotated[float, Field()]

    Vertex_33_Z_Coordinate: Annotated[float, Field()]

    Vertex_34_X_Coordinate: Annotated[float, Field()]

    Vertex_34_Y_Coordinate: Annotated[float, Field()]

    Vertex_34_Z_Coordinate: Annotated[float, Field()]

    Vertex_35_X_Coordinate: Annotated[float, Field()]

    Vertex_35_Y_Coordinate: Annotated[float, Field()]

    Vertex_35_Z_Coordinate: Annotated[float, Field()]

    Vertex_36_X_Coordinate: Annotated[float, Field()]

    Vertex_36_Y_Coordinate: Annotated[float, Field()]

    Vertex_36_Z_Coordinate: Annotated[float, Field()]

    Vertex_37_X_Coordinate: Annotated[float, Field()]

    Vertex_37_Y_Coordinate: Annotated[float, Field()]

    Vertex_37_Z_Coordinate: Annotated[float, Field()]

    Vertex_38_X_Coordinate: Annotated[float, Field()]

    Vertex_38_Y_Coordinate: Annotated[float, Field()]

    Vertex_38_Z_Coordinate: Annotated[float, Field()]

    Vertex_39_X_Coordinate: Annotated[float, Field()]

    Vertex_39_Y_Coordinate: Annotated[float, Field()]

    Vertex_39_Z_Coordinate: Annotated[float, Field()]

    Vertex_40_X_Coordinate: Annotated[float, Field()]

    Vertex_40_Y_Coordinate: Annotated[float, Field()]

    Vertex_40_Z_Coordinate: Annotated[float, Field()]

    Vertex_41_X_Coordinate: Annotated[float, Field()]

    Vertex_41_Y_Coordinate: Annotated[float, Field()]

    Vertex_41_Z_Coordinate: Annotated[float, Field()]

    Vertex_42_X_Coordinate: Annotated[float, Field()]

    Vertex_42_Y_Coordinate: Annotated[float, Field()]

    Vertex_42_Z_Coordinate: Annotated[float, Field()]

    Vertex_43_X_Coordinate: Annotated[float, Field()]

    Vertex_43_Y_Coordinate: Annotated[float, Field()]

    Vertex_43_Z_Coordinate: Annotated[float, Field()]

    Vertex_44_X_Coordinate: Annotated[float, Field()]

    Vertex_44_Y_Coordinate: Annotated[float, Field()]

    Vertex_44_Z_Coordinate: Annotated[float, Field()]

    Vertex_45_X_Coordinate: Annotated[float, Field()]

    Vertex_45_Y_Coordinate: Annotated[float, Field()]

    Vertex_45_Z_Coordinate: Annotated[float, Field()]

    Vertex_46_X_Coordinate: Annotated[float, Field()]

    Vertex_46_Y_Coordinate: Annotated[float, Field()]

    Vertex_46_Z_Coordinate: Annotated[float, Field()]

    Vertex_47_X_Coordinate: Annotated[float, Field()]

    Vertex_47_Y_Coordinate: Annotated[float, Field()]

    Vertex_47_Z_Coordinate: Annotated[float, Field()]

    Vertex_48_X_Coordinate: Annotated[float, Field()]

    Vertex_48_Y_Coordinate: Annotated[float, Field()]

    Vertex_48_Z_Coordinate: Annotated[float, Field()]

    Vertex_49_X_Coordinate: Annotated[float, Field()]

    Vertex_49_Y_Coordinate: Annotated[float, Field()]

    Vertex_49_Z_Coordinate: Annotated[float, Field()]

    Vertex_50_X_Coordinate: Annotated[float, Field()]

    Vertex_50_Y_Coordinate: Annotated[float, Field()]

    Vertex_50_Z_Coordinate: Annotated[float, Field()]

    Vertex_51_X_Coordinate: Annotated[float, Field()]

    Vertex_51_Y_Coordinate: Annotated[float, Field()]

    Vertex_51_Z_Coordinate: Annotated[float, Field()]

    Vertex_52_X_Coordinate: Annotated[float, Field()]

    Vertex_52_Y_Coordinate: Annotated[float, Field()]

    Vertex_52_Z_Coordinate: Annotated[float, Field()]

    Vertex_53_X_Coordinate: Annotated[float, Field()]

    Vertex_53_Y_Coordinate: Annotated[float, Field()]

    Vertex_53_Z_Coordinate: Annotated[float, Field()]

    Vertex_54_X_Coordinate: Annotated[float, Field()]

    Vertex_54_Y_Coordinate: Annotated[float, Field()]

    Vertex_54_Z_Coordinate: Annotated[float, Field()]

    Vertex_55_X_Coordinate: Annotated[float, Field()]

    Vertex_55_Y_Coordinate: Annotated[float, Field()]

    Vertex_55_Z_Coordinate: Annotated[float, Field()]

    Vertex_56_X_Coordinate: Annotated[float, Field()]

    Vertex_56_Y_Coordinate: Annotated[float, Field()]

    Vertex_56_Z_Coordinate: Annotated[float, Field()]

    Vertex_57_X_Coordinate: Annotated[float, Field()]

    Vertex_57_Y_Coordinate: Annotated[float, Field()]

    Vertex_57_Z_Coordinate: Annotated[float, Field()]

    Vertex_58_X_Coordinate: Annotated[float, Field()]

    Vertex_58_Y_Coordinate: Annotated[float, Field()]

    Vertex_58_Z_Coordinate: Annotated[float, Field()]

    Vertex_59_X_Coordinate: Annotated[float, Field()]

    Vertex_59_Y_Coordinate: Annotated[float, Field()]

    Vertex_59_Z_Coordinate: Annotated[float, Field()]

    Vertex_60_X_Coordinate: Annotated[float, Field()]

    Vertex_60_Y_Coordinate: Annotated[float, Field()]

    Vertex_60_Z_Coordinate: Annotated[float, Field()]

    Vertex_61_X_Coordinate: Annotated[float, Field()]

    Vertex_61_Y_Coordinate: Annotated[float, Field()]

    Vertex_61_Z_Coordinate: Annotated[float, Field()]

    Vertex_62_X_Coordinate: Annotated[float, Field()]

    Vertex_62_Y_Coordinate: Annotated[float, Field()]

    Vertex_62_Z_Coordinate: Annotated[float, Field()]

    Vertex_63_X_Coordinate: Annotated[float, Field()]

    Vertex_63_Y_Coordinate: Annotated[float, Field()]

    Vertex_63_Z_Coordinate: Annotated[float, Field()]

    Vertex_64_X_Coordinate: Annotated[float, Field()]

    Vertex_64_Y_Coordinate: Annotated[float, Field()]

    Vertex_64_Z_Coordinate: Annotated[float, Field()]

    Vertex_65_X_Coordinate: Annotated[float, Field()]

    Vertex_65_Y_Coordinate: Annotated[float, Field()]

    Vertex_65_Z_Coordinate: Annotated[float, Field()]

    Vertex_66_X_Coordinate: Annotated[float, Field()]

    Vertex_66_Y_Coordinate: Annotated[float, Field()]

    Vertex_66_Z_Coordinate: Annotated[float, Field()]

    Vertex_67_X_Coordinate: Annotated[float, Field()]

    Vertex_67_Y_Coordinate: Annotated[float, Field()]

    Vertex_67_Z_Coordinate: Annotated[float, Field()]

    Vertex_68_X_Coordinate: Annotated[float, Field()]

    Vertex_68_Y_Coordinate: Annotated[float, Field()]

    Vertex_68_Z_Coordinate: Annotated[float, Field()]

    Vertex_69_X_Coordinate: Annotated[float, Field()]

    Vertex_69_Y_Coordinate: Annotated[float, Field()]

    Vertex_69_Z_Coordinate: Annotated[float, Field()]

    Vertex_70_X_Coordinate: Annotated[float, Field()]

    Vertex_70_Y_Coordinate: Annotated[float, Field()]

    Vertex_70_Z_Coordinate: Annotated[float, Field()]

    Vertex_71_X_Coordinate: Annotated[float, Field()]

    Vertex_71_Y_Coordinate: Annotated[float, Field()]

    Vertex_71_Z_Coordinate: Annotated[float, Field()]

    Vertex_72_X_Coordinate: Annotated[float, Field()]

    Vertex_72_Y_Coordinate: Annotated[float, Field()]

    Vertex_72_Z_Coordinate: Annotated[float, Field()]

    Vertex_73_X_Coordinate: Annotated[float, Field()]

    Vertex_73_Y_Coordinate: Annotated[float, Field()]

    Vertex_73_Z_Coordinate: Annotated[float, Field()]

    Vertex_74_X_Coordinate: Annotated[float, Field()]

    Vertex_74_Y_Coordinate: Annotated[float, Field()]

    Vertex_74_Z_Coordinate: Annotated[float, Field()]

    Vertex_75_X_Coordinate: Annotated[float, Field()]

    Vertex_75_Y_Coordinate: Annotated[float, Field()]

    Vertex_75_Z_Coordinate: Annotated[float, Field()]

    Vertex_76_X_Coordinate: Annotated[float, Field()]

    Vertex_76_Y_Coordinate: Annotated[float, Field()]

    Vertex_76_Z_Coordinate: Annotated[float, Field()]

    Vertex_77_X_Coordinate: Annotated[float, Field()]

    Vertex_77_Y_Coordinate: Annotated[float, Field()]

    Vertex_77_Z_Coordinate: Annotated[float, Field()]

    Vertex_78_X_Coordinate: Annotated[float, Field()]

    Vertex_78_Y_Coordinate: Annotated[float, Field()]

    Vertex_78_Z_Coordinate: Annotated[float, Field()]

    Vertex_79_X_Coordinate: Annotated[float, Field()]

    Vertex_79_Y_Coordinate: Annotated[float, Field()]

    Vertex_79_Z_Coordinate: Annotated[float, Field()]

    Vertex_80_X_Coordinate: Annotated[float, Field()]

    Vertex_80_Y_Coordinate: Annotated[float, Field()]

    Vertex_80_Z_Coordinate: Annotated[float, Field()]

    Vertex_81_X_Coordinate: Annotated[float, Field()]

    Vertex_81_Y_Coordinate: Annotated[float, Field()]

    Vertex_81_Z_Coordinate: Annotated[float, Field()]

    Vertex_82_X_Coordinate: Annotated[float, Field()]

    Vertex_82_Y_Coordinate: Annotated[float, Field()]

    Vertex_82_Z_Coordinate: Annotated[float, Field()]

    Vertex_83_X_Coordinate: Annotated[float, Field()]

    Vertex_83_Y_Coordinate: Annotated[float, Field()]

    Vertex_83_Z_Coordinate: Annotated[float, Field()]

    Vertex_84_X_Coordinate: Annotated[float, Field()]

    Vertex_84_Y_Coordinate: Annotated[float, Field()]

    Vertex_84_Z_Coordinate: Annotated[float, Field()]

    Vertex_85_X_Coordinate: Annotated[float, Field()]

    Vertex_85_Y_Coordinate: Annotated[float, Field()]

    Vertex_85_Z_Coordinate: Annotated[float, Field()]

    Vertex_86_X_Coordinate: Annotated[float, Field()]

    Vertex_86_Y_Coordinate: Annotated[float, Field()]

    Vertex_86_Z_Coordinate: Annotated[float, Field()]

    Vertex_87_X_Coordinate: Annotated[float, Field()]

    Vertex_87_Y_Coordinate: Annotated[float, Field()]

    Vertex_87_Z_Coordinate: Annotated[float, Field()]

    Vertex_88_X_Coordinate: Annotated[float, Field()]

    Vertex_88_Y_Coordinate: Annotated[float, Field()]

    Vertex_88_Z_Coordinate: Annotated[float, Field()]

    Vertex_89_X_Coordinate: Annotated[float, Field()]

    Vertex_89_Y_Coordinate: Annotated[float, Field()]

    Vertex_89_Z_Coordinate: Annotated[float, Field()]

    Vertex_90_X_Coordinate: Annotated[float, Field()]

    Vertex_90_Y_Coordinate: Annotated[float, Field()]

    Vertex_90_Z_Coordinate: Annotated[float, Field()]

    Vertex_91_X_Coordinate: Annotated[float, Field()]

    Vertex_91_Y_Coordinate: Annotated[float, Field()]

    Vertex_91_Z_Coordinate: Annotated[float, Field()]

    Vertex_92_X_Coordinate: Annotated[float, Field()]

    Vertex_92_Y_Coordinate: Annotated[float, Field()]

    Vertex_92_Z_Coordinate: Annotated[float, Field()]

    Vertex_93_X_Coordinate: Annotated[float, Field()]

    Vertex_93_Y_Coordinate: Annotated[float, Field()]

    Vertex_93_Z_Coordinate: Annotated[float, Field()]

    Vertex_94_X_Coordinate: Annotated[float, Field()]

    Vertex_94_Y_Coordinate: Annotated[float, Field()]

    Vertex_94_Z_Coordinate: Annotated[float, Field()]

    Vertex_95_X_Coordinate: Annotated[float, Field()]

    Vertex_95_Y_Coordinate: Annotated[float, Field()]

    Vertex_95_Z_Coordinate: Annotated[float, Field()]

    Vertex_96_X_Coordinate: Annotated[float, Field()]

    Vertex_96_Y_Coordinate: Annotated[float, Field()]

    Vertex_96_Z_Coordinate: Annotated[float, Field()]

    Vertex_97_X_Coordinate: Annotated[float, Field()]

    Vertex_97_Y_Coordinate: Annotated[float, Field()]

    Vertex_97_Z_Coordinate: Annotated[float, Field()]

    Vertex_98_X_Coordinate: Annotated[float, Field()]

    Vertex_98_Y_Coordinate: Annotated[float, Field()]

    Vertex_98_Z_Coordinate: Annotated[float, Field()]

    Vertex_99_X_Coordinate: Annotated[float, Field()]

    Vertex_99_Y_Coordinate: Annotated[float, Field()]

    Vertex_99_Z_Coordinate: Annotated[float, Field()]

    Vertex_100_X_Coordinate: Annotated[float, Field()]

    Vertex_100_Y_Coordinate: Annotated[float, Field()]

    Vertex_100_Z_Coordinate: Annotated[float, Field()]

    Vertex_101_X_Coordinate: Annotated[float, Field()]

    Vertex_101_Y_Coordinate: Annotated[float, Field()]

    Vertex_101_Z_Coordinate: Annotated[float, Field()]

    Vertex_102_X_Coordinate: Annotated[float, Field()]

    Vertex_102_Y_Coordinate: Annotated[float, Field()]

    Vertex_102_Z_Coordinate: Annotated[float, Field()]

    Vertex_103_X_Coordinate: Annotated[float, Field()]

    Vertex_103_Y_Coordinate: Annotated[float, Field()]

    Vertex_103_Z_Coordinate: Annotated[float, Field()]

    Vertex_104_X_Coordinate: Annotated[float, Field()]

    Vertex_104_Y_Coordinate: Annotated[float, Field()]

    Vertex_104_Z_Coordinate: Annotated[float, Field()]

    Vertex_105_X_Coordinate: Annotated[float, Field()]

    Vertex_105_Y_Coordinate: Annotated[float, Field()]

    Vertex_105_Z_Coordinate: Annotated[float, Field()]

    Vertex_106_X_Coordinate: Annotated[float, Field()]

    Vertex_106_Y_Coordinate: Annotated[float, Field()]

    Vertex_106_Z_Coordinate: Annotated[float, Field()]

    Vertex_107_X_Coordinate: Annotated[float, Field()]

    Vertex_107_Y_Coordinate: Annotated[float, Field()]

    Vertex_107_Z_Coordinate: Annotated[float, Field()]

    Vertex_108_X_Coordinate: Annotated[float, Field()]

    Vertex_108_Y_Coordinate: Annotated[float, Field()]

    Vertex_108_Z_Coordinate: Annotated[float, Field()]

    Vertex_109_X_Coordinate: Annotated[float, Field()]

    Vertex_109_Y_Coordinate: Annotated[float, Field()]

    Vertex_109_Z_Coordinate: Annotated[float, Field()]

    Vertex_110_X_Coordinate: Annotated[float, Field()]

    Vertex_110_Y_Coordinate: Annotated[float, Field()]

    Vertex_110_Z_Coordinate: Annotated[float, Field()]

    Vertex_111_X_Coordinate: Annotated[float, Field()]

    Vertex_111_Y_Coordinate: Annotated[float, Field()]

    Vertex_111_Z_Coordinate: Annotated[float, Field()]

    Vertex_112_X_Coordinate: Annotated[float, Field()]

    Vertex_112_Y_Coordinate: Annotated[float, Field()]

    Vertex_112_Z_Coordinate: Annotated[float, Field()]

    Vertex_113_X_Coordinate: Annotated[float, Field()]

    Vertex_113_Y_Coordinate: Annotated[float, Field()]

    Vertex_113_Z_Coordinate: Annotated[float, Field()]

    Vertex_114_X_Coordinate: Annotated[float, Field()]

    Vertex_114_Y_Coordinate: Annotated[float, Field()]

    Vertex_114_Z_Coordinate: Annotated[float, Field()]

    Vertex_115_X_Coordinate: Annotated[float, Field()]

    Vertex_115_Y_Coordinate: Annotated[float, Field()]

    Vertex_115_Z_Coordinate: Annotated[float, Field()]

    Vertex_116_X_Coordinate: Annotated[float, Field()]

    Vertex_116_Y_Coordinate: Annotated[float, Field()]

    Vertex_116_Z_Coordinate: Annotated[float, Field()]

    Vertex_117_X_Coordinate: Annotated[float, Field()]

    Vertex_117_Y_Coordinate: Annotated[float, Field()]

    Vertex_117_Z_Coordinate: Annotated[float, Field()]

    Vertex_118_X_Coordinate: Annotated[float, Field()]

    Vertex_118_Y_Coordinate: Annotated[float, Field()]

    Vertex_118_Z_Coordinate: Annotated[float, Field()]

    Vertex_119_X_Coordinate: Annotated[float, Field()]

    Vertex_119_Y_Coordinate: Annotated[float, Field()]

    Vertex_119_Z_Coordinate: Annotated[float, Field()]

    Vertex_120_X_Coordinate: Annotated[float, Field()]

    Vertex_120_Y_Coordinate: Annotated[float, Field()]

    Vertex_120_Z_Coordinate: Annotated[float, Field()]