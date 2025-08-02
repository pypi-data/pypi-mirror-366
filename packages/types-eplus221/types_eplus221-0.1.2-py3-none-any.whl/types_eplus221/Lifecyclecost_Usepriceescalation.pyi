from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Lifecyclecost_Usepriceescalation(EpBunch):
    """Life cycle cost escalation factors. The values for this object may be found in the"""

    LCC_Price_Escalation_Name: Annotated[str, Field(default=...)]
    """The identifier used for the object. The name usually identifies the location (such as the"""

    Resource: Annotated[Literal['Electricity', 'ElectricityPurchased', 'ElectricityProduced', 'ElectricitySurplusSold', 'ElectricityNet', 'NaturalGas', 'Steam', 'Gasoline', 'Diesel', 'Coal', 'FuelOil#1', 'FuelOil#2', 'Propane', 'OtherFuel1', 'OtherFuel2', 'Water'], Field(default=...)]

    Escalation_Start_Year: Annotated[int, Field(ge=1900, le=2100)]
    """This field and the Escalation Start Month define the time that corresponds to Year 1 Escalation"""

    Escalation_Start_Month: Annotated[Literal['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], Field(default='January')]
    """This field and the Escalation Start Year define the time that corresponds to Year 1 Escalation"""

    Year_1_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_2_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_3_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_4_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_5_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_6_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_7_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_8_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_9_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_10_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_11_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_12_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_13_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_14_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_15_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_16_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_17_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_18_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_19_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_20_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_21_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_22_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_23_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_24_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_25_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_26_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_27_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_28_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_29_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_30_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_31_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_32_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_33_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_34_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_35_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_36_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_37_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_38_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_39_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_40_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_41_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_42_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_43_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_44_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_45_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_46_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_47_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_48_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_49_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_50_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_51_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_52_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_53_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_54_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_55_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_56_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_57_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_58_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_59_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_60_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_61_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_62_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_63_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_64_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_65_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_66_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_67_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_68_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_69_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_70_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_71_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_72_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_73_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_74_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_75_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_76_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_77_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_78_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_79_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_80_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_81_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_82_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_83_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_84_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_85_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_86_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_87_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_88_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_89_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_90_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_91_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_92_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_93_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_94_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_95_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_96_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_97_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_98_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_99_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""

    Year_100_Escalation: Annotated[float, Field()]
    """The escalation in price of the energy or water use for the first year expressed as a decimal."""