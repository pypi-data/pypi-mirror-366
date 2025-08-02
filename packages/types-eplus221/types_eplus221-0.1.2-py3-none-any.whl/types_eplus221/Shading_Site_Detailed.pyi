from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Shading_Site_Detailed(EpBunch):
    """used for shading elements such as trees"""

    Name: Annotated[str, Field(default=...)]

    Transmittance_Schedule_Name: Annotated[str, Field()]
    """Transmittance schedule for the shading device, defaults to zero (always opaque)"""

    Number_of_Vertices: Annotated[str, Field(default='autocalculate')]
    """shown with 6 vertex coordinates -- extensible object"""

    Vertex_1_Xcoordinate: Annotated[float, Field(default=...)]

    Vertex_1_Ycoordinate: Annotated[float, Field(default=...)]

    Vertex_1_Zcoordinate: Annotated[float, Field(default=...)]

    Vertex_2_Xcoordinate: Annotated[float, Field(default=...)]

    Vertex_2_Ycoordinate: Annotated[float, Field(default=...)]

    Vertex_2_Zcoordinate: Annotated[float, Field(default=...)]

    Vertex_3_Xcoordinate: Annotated[float, Field(default=...)]

    Vertex_3_Ycoordinate: Annotated[float, Field(default=...)]

    Vertex_3_Zcoordinate: Annotated[float, Field(default=...)]

    Vertex_4_Xcoordinate: Annotated[float, Field()]

    Vertex_4_Ycoordinate: Annotated[float, Field()]

    Vertex_4_Zcoordinate: Annotated[float, Field()]

    Vertex_5_Xcoordinate: Annotated[float, Field()]

    Vertex_5_Ycoordinate: Annotated[float, Field()]

    Vertex_5_Zcoordinate: Annotated[float, Field()]

    Vertex_6_Xcoordinate: Annotated[float, Field()]

    Vertex_6_Ycoordinate: Annotated[float, Field()]

    Vertex_6_Zcoordinate: Annotated[float, Field()]

    Vertex_7_Xcoordinate: Annotated[float, Field()]

    Vertex_7_Ycoordinate: Annotated[float, Field()]

    Vertex_7_Zcoordinate: Annotated[float, Field()]

    Vertex_8_Xcoordinate: Annotated[float, Field()]

    Vertex_8_Ycoordinate: Annotated[float, Field()]

    Vertex_8_Zcoordinate: Annotated[float, Field()]

    Vertex_9_Xcoordinate: Annotated[float, Field()]

    Vertex_9_Ycoordinate: Annotated[float, Field()]

    Vertex_9_Zcoordinate: Annotated[float, Field()]

    Vertex_10_Xcoordinate: Annotated[float, Field()]

    Vertex_10_Ycoordinate: Annotated[float, Field()]

    Vertex_10_Zcoordinate: Annotated[float, Field()]

    Vertex_11_Xcoordinate: Annotated[float, Field()]

    Vertex_11_Ycoordinate: Annotated[float, Field()]

    Vertex_11_Zcoordinate: Annotated[float, Field()]

    Vertex_12_Xcoordinate: Annotated[float, Field()]

    Vertex_12_Ycoordinate: Annotated[float, Field()]

    Vertex_12_Zcoordinate: Annotated[float, Field()]

    Vertex_13_Xcoordinate: Annotated[float, Field()]

    Vertex_13_Ycoordinate: Annotated[float, Field()]

    Vertex_13_Zcoordinate: Annotated[float, Field()]

    Vertex_14_Xcoordinate: Annotated[float, Field()]

    Vertex_14_Ycoordinate: Annotated[float, Field()]

    Vertex_14_Zcoordinate: Annotated[float, Field()]

    Vertex_15_Xcoordinate: Annotated[float, Field()]

    Vertex_15_Ycoordinate: Annotated[float, Field()]

    Vertex_15_Zcoordinate: Annotated[float, Field()]

    Vertex_16_Xcoordinate: Annotated[float, Field()]

    Vertex_16_Ycoordinate: Annotated[float, Field()]

    Vertex_16_Zcoordinate: Annotated[float, Field()]

    Vertex_17_Xcoordinate: Annotated[float, Field()]

    Vertex_17_Ycoordinate: Annotated[float, Field()]

    Vertex_17_Zcoordinate: Annotated[float, Field()]

    Vertex_18_Xcoordinate: Annotated[float, Field()]

    Vertex_18_Ycoordinate: Annotated[float, Field()]

    Vertex_18_Zcoordinate: Annotated[float, Field()]

    Vertex_19_Xcoordinate: Annotated[float, Field()]

    Vertex_19_Ycoordinate: Annotated[float, Field()]

    Vertex_19_Zcoordinate: Annotated[float, Field()]

    Vertex_20_Xcoordinate: Annotated[float, Field()]

    Vertex_20_Ycoordinate: Annotated[float, Field()]

    Vertex_20_Zcoordinate: Annotated[float, Field()]

    Vertex_21_Xcoordinate: Annotated[float, Field()]

    Vertex_21_Ycoordinate: Annotated[float, Field()]

    Vertex_21_Zcoordinate: Annotated[float, Field()]

    Vertex_22_Xcoordinate: Annotated[float, Field()]

    Vertex_22_Ycoordinate: Annotated[float, Field()]

    Vertex_22_Zcoordinate: Annotated[float, Field()]

    Vertex_23_Xcoordinate: Annotated[float, Field()]

    Vertex_23_Ycoordinate: Annotated[float, Field()]

    Vertex_23_Zcoordinate: Annotated[float, Field()]

    Vertex_24_Xcoordinate: Annotated[float, Field()]

    Vertex_24_Ycoordinate: Annotated[float, Field()]

    Vertex_24_Zcoordinate: Annotated[float, Field()]

    Vertex_25_Xcoordinate: Annotated[float, Field()]

    Vertex_25_Ycoordinate: Annotated[float, Field()]

    Vertex_25_Zcoordinate: Annotated[float, Field()]

    Vertex_26_Xcoordinate: Annotated[float, Field()]

    Vertex_26_Ycoordinate: Annotated[float, Field()]

    Vertex_26_Zcoordinate: Annotated[float, Field()]

    Vertex_27_Xcoordinate: Annotated[float, Field()]

    Vertex_27_Ycoordinate: Annotated[float, Field()]

    Vertex_27_Zcoordinate: Annotated[float, Field()]

    Vertex_28_Xcoordinate: Annotated[float, Field()]

    Vertex_28_Ycoordinate: Annotated[float, Field()]

    Vertex_28_Zcoordinate: Annotated[float, Field()]

    Vertex_29_Xcoordinate: Annotated[float, Field()]

    Vertex_29_Ycoordinate: Annotated[float, Field()]

    Vertex_29_Zcoordinate: Annotated[float, Field()]

    Vertex_30_Xcoordinate: Annotated[float, Field()]

    Vertex_30_Ycoordinate: Annotated[float, Field()]

    Vertex_30_Zcoordinate: Annotated[float, Field()]

    Vertex_31_Xcoordinate: Annotated[float, Field()]

    Vertex_31_Ycoordinate: Annotated[float, Field()]

    Vertex_31_Zcoordinate: Annotated[float, Field()]

    Vertex_32_Xcoordinate: Annotated[float, Field()]

    Vertex_32_Ycoordinate: Annotated[float, Field()]

    Vertex_32_Zcoordinate: Annotated[float, Field()]

    Vertex_33_Xcoordinate: Annotated[float, Field()]

    Vertex_33_Ycoordinate: Annotated[float, Field()]

    Vertex_33_Zcoordinate: Annotated[float, Field()]

    Vertex_34_Xcoordinate: Annotated[float, Field()]

    Vertex_34_Ycoordinate: Annotated[float, Field()]

    Vertex_34_Zcoordinate: Annotated[float, Field()]

    Vertex_35_Xcoordinate: Annotated[float, Field()]

    Vertex_35_Ycoordinate: Annotated[float, Field()]

    Vertex_35_Zcoordinate: Annotated[float, Field()]

    Vertex_36_Xcoordinate: Annotated[float, Field()]

    Vertex_36_Ycoordinate: Annotated[float, Field()]

    Vertex_36_Zcoordinate: Annotated[float, Field()]

    Vertex_37_Xcoordinate: Annotated[float, Field()]

    Vertex_37_Ycoordinate: Annotated[float, Field()]

    Vertex_37_Zcoordinate: Annotated[float, Field()]

    Vertex_38_Xcoordinate: Annotated[float, Field()]

    Vertex_38_Ycoordinate: Annotated[float, Field()]

    Vertex_38_Zcoordinate: Annotated[float, Field()]

    Vertex_39_Xcoordinate: Annotated[float, Field()]

    Vertex_39_Ycoordinate: Annotated[float, Field()]

    Vertex_39_Zcoordinate: Annotated[float, Field()]

    Vertex_40_Xcoordinate: Annotated[float, Field()]

    Vertex_40_Ycoordinate: Annotated[float, Field()]

    Vertex_40_Zcoordinate: Annotated[float, Field()]

    Vertex_41_Xcoordinate: Annotated[float, Field()]

    Vertex_41_Ycoordinate: Annotated[float, Field()]

    Vertex_41_Zcoordinate: Annotated[float, Field()]

    Vertex_42_Xcoordinate: Annotated[float, Field()]

    Vertex_42_Ycoordinate: Annotated[float, Field()]

    Vertex_42_Zcoordinate: Annotated[float, Field()]

    Vertex_43_Xcoordinate: Annotated[float, Field()]

    Vertex_43_Ycoordinate: Annotated[float, Field()]

    Vertex_43_Zcoordinate: Annotated[float, Field()]

    Vertex_44_Xcoordinate: Annotated[float, Field()]

    Vertex_44_Ycoordinate: Annotated[float, Field()]

    Vertex_44_Zcoordinate: Annotated[float, Field()]

    Vertex_45_Xcoordinate: Annotated[float, Field()]

    Vertex_45_Ycoordinate: Annotated[float, Field()]

    Vertex_45_Zcoordinate: Annotated[float, Field()]

    Vertex_46_Xcoordinate: Annotated[float, Field()]

    Vertex_46_Ycoordinate: Annotated[float, Field()]

    Vertex_46_Zcoordinate: Annotated[float, Field()]

    Vertex_47_Xcoordinate: Annotated[float, Field()]

    Vertex_47_Ycoordinate: Annotated[float, Field()]

    Vertex_47_Zcoordinate: Annotated[float, Field()]

    Vertex_48_Xcoordinate: Annotated[float, Field()]

    Vertex_48_Ycoordinate: Annotated[float, Field()]

    Vertex_48_Zcoordinate: Annotated[float, Field()]

    Vertex_49_Xcoordinate: Annotated[float, Field()]

    Vertex_49_Ycoordinate: Annotated[float, Field()]

    Vertex_49_Zcoordinate: Annotated[float, Field()]

    Vertex_50_Xcoordinate: Annotated[float, Field()]

    Vertex_50_Ycoordinate: Annotated[float, Field()]

    Vertex_50_Zcoordinate: Annotated[float, Field()]

    Vertex_51_Xcoordinate: Annotated[float, Field()]

    Vertex_51_Ycoordinate: Annotated[float, Field()]

    Vertex_51_Zcoordinate: Annotated[float, Field()]

    Vertex_52_Xcoordinate: Annotated[float, Field()]

    Vertex_52_Ycoordinate: Annotated[float, Field()]

    Vertex_52_Zcoordinate: Annotated[float, Field()]

    Vertex_53_Xcoordinate: Annotated[float, Field()]

    Vertex_53_Ycoordinate: Annotated[float, Field()]

    Vertex_53_Zcoordinate: Annotated[float, Field()]

    Vertex_54_Xcoordinate: Annotated[float, Field()]

    Vertex_54_Ycoordinate: Annotated[float, Field()]

    Vertex_54_Zcoordinate: Annotated[float, Field()]

    Vertex_55_Xcoordinate: Annotated[float, Field()]

    Vertex_55_Ycoordinate: Annotated[float, Field()]

    Vertex_55_Zcoordinate: Annotated[float, Field()]

    Vertex_56_Xcoordinate: Annotated[float, Field()]

    Vertex_56_Ycoordinate: Annotated[float, Field()]

    Vertex_56_Zcoordinate: Annotated[float, Field()]

    Vertex_57_Xcoordinate: Annotated[float, Field()]

    Vertex_57_Ycoordinate: Annotated[float, Field()]

    Vertex_57_Zcoordinate: Annotated[float, Field()]

    Vertex_58_Xcoordinate: Annotated[float, Field()]

    Vertex_58_Ycoordinate: Annotated[float, Field()]

    Vertex_58_Zcoordinate: Annotated[float, Field()]

    Vertex_59_Xcoordinate: Annotated[float, Field()]

    Vertex_59_Ycoordinate: Annotated[float, Field()]

    Vertex_59_Zcoordinate: Annotated[float, Field()]

    Vertex_60_Xcoordinate: Annotated[float, Field()]

    Vertex_60_Ycoordinate: Annotated[float, Field()]

    Vertex_60_Zcoordinate: Annotated[float, Field()]

    Vertex_61_Xcoordinate: Annotated[float, Field()]

    Vertex_61_Ycoordinate: Annotated[float, Field()]

    Vertex_61_Zcoordinate: Annotated[float, Field()]

    Vertex_62_Xcoordinate: Annotated[float, Field()]

    Vertex_62_Ycoordinate: Annotated[float, Field()]

    Vertex_62_Zcoordinate: Annotated[float, Field()]

    Vertex_63_Xcoordinate: Annotated[float, Field()]

    Vertex_63_Ycoordinate: Annotated[float, Field()]

    Vertex_63_Zcoordinate: Annotated[float, Field()]

    Vertex_64_Xcoordinate: Annotated[float, Field()]

    Vertex_64_Ycoordinate: Annotated[float, Field()]

    Vertex_64_Zcoordinate: Annotated[float, Field()]

    Vertex_65_Xcoordinate: Annotated[float, Field()]

    Vertex_65_Ycoordinate: Annotated[float, Field()]

    Vertex_65_Zcoordinate: Annotated[float, Field()]

    Vertex_66_Xcoordinate: Annotated[float, Field()]

    Vertex_66_Ycoordinate: Annotated[float, Field()]

    Vertex_66_Zcoordinate: Annotated[float, Field()]

    Vertex_67_Xcoordinate: Annotated[float, Field()]

    Vertex_67_Ycoordinate: Annotated[float, Field()]

    Vertex_67_Zcoordinate: Annotated[float, Field()]

    Vertex_68_Xcoordinate: Annotated[float, Field()]

    Vertex_68_Ycoordinate: Annotated[float, Field()]

    Vertex_68_Zcoordinate: Annotated[float, Field()]

    Vertex_69_Xcoordinate: Annotated[float, Field()]

    Vertex_69_Ycoordinate: Annotated[float, Field()]

    Vertex_69_Zcoordinate: Annotated[float, Field()]

    Vertex_70_Xcoordinate: Annotated[float, Field()]

    Vertex_70_Ycoordinate: Annotated[float, Field()]

    Vertex_70_Zcoordinate: Annotated[float, Field()]

    Vertex_71_Xcoordinate: Annotated[float, Field()]

    Vertex_71_Ycoordinate: Annotated[float, Field()]

    Vertex_71_Zcoordinate: Annotated[float, Field()]

    Vertex_72_Xcoordinate: Annotated[float, Field()]

    Vertex_72_Ycoordinate: Annotated[float, Field()]

    Vertex_72_Zcoordinate: Annotated[float, Field()]

    Vertex_73_Xcoordinate: Annotated[float, Field()]

    Vertex_73_Ycoordinate: Annotated[float, Field()]

    Vertex_73_Zcoordinate: Annotated[float, Field()]

    Vertex_74_Xcoordinate: Annotated[float, Field()]

    Vertex_74_Ycoordinate: Annotated[float, Field()]

    Vertex_74_Zcoordinate: Annotated[float, Field()]

    Vertex_75_Xcoordinate: Annotated[float, Field()]

    Vertex_75_Ycoordinate: Annotated[float, Field()]

    Vertex_75_Zcoordinate: Annotated[float, Field()]

    Vertex_76_Xcoordinate: Annotated[float, Field()]

    Vertex_76_Ycoordinate: Annotated[float, Field()]

    Vertex_76_Zcoordinate: Annotated[float, Field()]

    Vertex_77_Xcoordinate: Annotated[float, Field()]

    Vertex_77_Ycoordinate: Annotated[float, Field()]

    Vertex_77_Zcoordinate: Annotated[float, Field()]

    Vertex_78_Xcoordinate: Annotated[float, Field()]

    Vertex_78_Ycoordinate: Annotated[float, Field()]

    Vertex_78_Zcoordinate: Annotated[float, Field()]

    Vertex_79_Xcoordinate: Annotated[float, Field()]

    Vertex_79_Ycoordinate: Annotated[float, Field()]

    Vertex_79_Zcoordinate: Annotated[float, Field()]

    Vertex_80_Xcoordinate: Annotated[float, Field()]

    Vertex_80_Ycoordinate: Annotated[float, Field()]

    Vertex_80_Zcoordinate: Annotated[float, Field()]

    Vertex_81_Xcoordinate: Annotated[float, Field()]

    Vertex_81_Ycoordinate: Annotated[float, Field()]

    Vertex_81_Zcoordinate: Annotated[float, Field()]

    Vertex_82_Xcoordinate: Annotated[float, Field()]

    Vertex_82_Ycoordinate: Annotated[float, Field()]

    Vertex_82_Zcoordinate: Annotated[float, Field()]

    Vertex_83_Xcoordinate: Annotated[float, Field()]

    Vertex_83_Ycoordinate: Annotated[float, Field()]

    Vertex_83_Zcoordinate: Annotated[float, Field()]

    Vertex_84_Xcoordinate: Annotated[float, Field()]

    Vertex_84_Ycoordinate: Annotated[float, Field()]

    Vertex_84_Zcoordinate: Annotated[float, Field()]

    Vertex_85_Xcoordinate: Annotated[float, Field()]

    Vertex_85_Ycoordinate: Annotated[float, Field()]

    Vertex_85_Zcoordinate: Annotated[float, Field()]

    Vertex_86_Xcoordinate: Annotated[float, Field()]

    Vertex_86_Ycoordinate: Annotated[float, Field()]

    Vertex_86_Zcoordinate: Annotated[float, Field()]

    Vertex_87_Xcoordinate: Annotated[float, Field()]

    Vertex_87_Ycoordinate: Annotated[float, Field()]

    Vertex_87_Zcoordinate: Annotated[float, Field()]

    Vertex_88_Xcoordinate: Annotated[float, Field()]

    Vertex_88_Ycoordinate: Annotated[float, Field()]

    Vertex_88_Zcoordinate: Annotated[float, Field()]

    Vertex_89_Xcoordinate: Annotated[float, Field()]

    Vertex_89_Ycoordinate: Annotated[float, Field()]

    Vertex_89_Zcoordinate: Annotated[float, Field()]

    Vertex_90_Xcoordinate: Annotated[float, Field()]

    Vertex_90_Ycoordinate: Annotated[float, Field()]

    Vertex_90_Zcoordinate: Annotated[float, Field()]

    Vertex_91_Xcoordinate: Annotated[float, Field()]

    Vertex_91_Ycoordinate: Annotated[float, Field()]

    Vertex_91_Zcoordinate: Annotated[float, Field()]

    Vertex_92_Xcoordinate: Annotated[float, Field()]

    Vertex_92_Ycoordinate: Annotated[float, Field()]

    Vertex_92_Zcoordinate: Annotated[float, Field()]

    Vertex_93_Xcoordinate: Annotated[float, Field()]

    Vertex_93_Ycoordinate: Annotated[float, Field()]

    Vertex_93_Zcoordinate: Annotated[float, Field()]

    Vertex_94_Xcoordinate: Annotated[float, Field()]

    Vertex_94_Ycoordinate: Annotated[float, Field()]

    Vertex_94_Zcoordinate: Annotated[float, Field()]

    Vertex_95_Xcoordinate: Annotated[float, Field()]

    Vertex_95_Ycoordinate: Annotated[float, Field()]

    Vertex_95_Zcoordinate: Annotated[float, Field()]

    Vertex_96_Xcoordinate: Annotated[float, Field()]

    Vertex_96_Ycoordinate: Annotated[float, Field()]

    Vertex_96_Zcoordinate: Annotated[float, Field()]

    Vertex_97_Xcoordinate: Annotated[float, Field()]

    Vertex_97_Ycoordinate: Annotated[float, Field()]

    Vertex_97_Zcoordinate: Annotated[float, Field()]

    Vertex_98_Xcoordinate: Annotated[float, Field()]

    Vertex_98_Ycoordinate: Annotated[float, Field()]

    Vertex_98_Zcoordinate: Annotated[float, Field()]

    Vertex_99_Xcoordinate: Annotated[float, Field()]

    Vertex_99_Ycoordinate: Annotated[float, Field()]

    Vertex_99_Zcoordinate: Annotated[float, Field()]

    Vertex_100_Xcoordinate: Annotated[float, Field()]

    Vertex_100_Ycoordinate: Annotated[float, Field()]

    Vertex_100_Zcoordinate: Annotated[float, Field()]

    Vertex_101_Xcoordinate: Annotated[float, Field()]

    Vertex_101_Ycoordinate: Annotated[float, Field()]

    Vertex_101_Zcoordinate: Annotated[float, Field()]

    Vertex_102_Xcoordinate: Annotated[float, Field()]

    Vertex_102_Ycoordinate: Annotated[float, Field()]

    Vertex_102_Zcoordinate: Annotated[float, Field()]

    Vertex_103_Xcoordinate: Annotated[float, Field()]

    Vertex_103_Ycoordinate: Annotated[float, Field()]

    Vertex_103_Zcoordinate: Annotated[float, Field()]

    Vertex_104_Xcoordinate: Annotated[float, Field()]

    Vertex_104_Ycoordinate: Annotated[float, Field()]

    Vertex_104_Zcoordinate: Annotated[float, Field()]

    Vertex_105_Xcoordinate: Annotated[float, Field()]

    Vertex_105_Ycoordinate: Annotated[float, Field()]

    Vertex_105_Zcoordinate: Annotated[float, Field()]

    Vertex_106_Xcoordinate: Annotated[float, Field()]

    Vertex_106_Ycoordinate: Annotated[float, Field()]

    Vertex_106_Zcoordinate: Annotated[float, Field()]

    Vertex_107_Xcoordinate: Annotated[float, Field()]

    Vertex_107_Ycoordinate: Annotated[float, Field()]

    Vertex_107_Zcoordinate: Annotated[float, Field()]

    Vertex_108_Xcoordinate: Annotated[float, Field()]

    Vertex_108_Ycoordinate: Annotated[float, Field()]

    Vertex_108_Zcoordinate: Annotated[float, Field()]

    Vertex_109_Xcoordinate: Annotated[float, Field()]

    Vertex_109_Ycoordinate: Annotated[float, Field()]

    Vertex_109_Zcoordinate: Annotated[float, Field()]

    Vertex_110_Xcoordinate: Annotated[float, Field()]

    Vertex_110_Ycoordinate: Annotated[float, Field()]

    Vertex_110_Zcoordinate: Annotated[float, Field()]

    Vertex_111_Xcoordinate: Annotated[float, Field()]

    Vertex_111_Ycoordinate: Annotated[float, Field()]

    Vertex_111_Zcoordinate: Annotated[float, Field()]

    Vertex_112_Xcoordinate: Annotated[float, Field()]

    Vertex_112_Ycoordinate: Annotated[float, Field()]

    Vertex_112_Zcoordinate: Annotated[float, Field()]

    Vertex_113_Xcoordinate: Annotated[float, Field()]

    Vertex_113_Ycoordinate: Annotated[float, Field()]

    Vertex_113_Zcoordinate: Annotated[float, Field()]

    Vertex_114_Xcoordinate: Annotated[float, Field()]

    Vertex_114_Ycoordinate: Annotated[float, Field()]

    Vertex_114_Zcoordinate: Annotated[float, Field()]

    Vertex_115_Xcoordinate: Annotated[float, Field()]

    Vertex_115_Ycoordinate: Annotated[float, Field()]

    Vertex_115_Zcoordinate: Annotated[float, Field()]

    Vertex_116_Xcoordinate: Annotated[float, Field()]

    Vertex_116_Ycoordinate: Annotated[float, Field()]

    Vertex_116_Zcoordinate: Annotated[float, Field()]

    Vertex_117_Xcoordinate: Annotated[float, Field()]

    Vertex_117_Ycoordinate: Annotated[float, Field()]

    Vertex_117_Zcoordinate: Annotated[float, Field()]

    Vertex_118_Xcoordinate: Annotated[float, Field()]

    Vertex_118_Ycoordinate: Annotated[float, Field()]

    Vertex_118_Zcoordinate: Annotated[float, Field()]

    Vertex_119_Xcoordinate: Annotated[float, Field()]

    Vertex_119_Ycoordinate: Annotated[float, Field()]

    Vertex_119_Zcoordinate: Annotated[float, Field()]

    Vertex_120_Xcoordinate: Annotated[float, Field()]

    Vertex_120_Ycoordinate: Annotated[float, Field()]

    Vertex_120_Zcoordinate: Annotated[float, Field()]