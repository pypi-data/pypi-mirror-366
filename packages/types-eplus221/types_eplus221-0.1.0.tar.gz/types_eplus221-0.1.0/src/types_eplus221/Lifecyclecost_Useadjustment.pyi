from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Lifecyclecost_Useadjustment(EpBunch):
    """Used by advanced users to adjust the energy or water use costs for future years. This"""

    Name: Annotated[str, Field(default=...)]

    Resource: Annotated[Literal['Electricity', 'ElectricityPurchased', 'ElectricityProduced', 'ElectricitySurplusSold', 'ElectricityNet', 'NaturalGas', 'Steam', 'Gasoline', 'Diesel', 'Coal', 'FuelOil#1', 'FuelOil#2', 'Propane', 'OtherFuel1', 'OtherFuel2', 'Water'], Field(default=...)]

    Year_1_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_2_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_3_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_4_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_5_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_6_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_7_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_8_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_9_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_10_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_11_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_12_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_13_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_14_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_15_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_16_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_17_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_18_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_19_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_20_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_21_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_22_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_23_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_24_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_25_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_26_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_27_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_28_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_29_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_30_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_31_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_32_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_33_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_34_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_35_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_36_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_37_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_38_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_39_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_40_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_41_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_42_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_43_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_44_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_45_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_46_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_47_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_48_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_49_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_50_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_51_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_52_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_53_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_54_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_55_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_56_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_57_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_58_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_59_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_60_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_61_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_62_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_63_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_64_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_65_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_66_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_67_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_68_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_69_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_70_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_71_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_72_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_73_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_74_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_75_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_76_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_77_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_78_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_79_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_80_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_81_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_82_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_83_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_84_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_85_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_86_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_87_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_88_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_89_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_90_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_91_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_92_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_93_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_94_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_95_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_96_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_97_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_98_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_99_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""

    Year_100_Multiplier: Annotated[float, Field()]
    """The multiplier to be applied to the end-use cost for the first year in the service period."""