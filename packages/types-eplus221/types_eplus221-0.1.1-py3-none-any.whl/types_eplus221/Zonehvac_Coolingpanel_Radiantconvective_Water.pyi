from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Coolingpanel_Radiantconvective_Water(EpBunch):
    """The number of surfaces can be expanded beyond 100, if necessary, by adding more"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field(default=...)]

    Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Rated_Inlet_Water_Temperature: Annotated[float, Field(default=5.0)]

    Rated_Inlet_Space_Temperature: Annotated[float, Field(default=24.0)]

    Rated_Water_Mass_Flow_Rate: Annotated[float, Field(gt=0.0, default=0.063)]

    Cooling_Design_Capacity_Method: Annotated[Literal['None', 'CoolingDesignCapacity', 'CapacityPerFloorArea', 'FractionOfAutosizedCoolingCapacity'], Field(default='CoolingDesignCapacity')]
    """Enter the method used to determine the cooling design capacity for scalable sizing."""

    Cooling_Design_Capacity: Annotated[float, Field(ge=0.0)]
    """Enter the design cooling capacity. Required field when the cooling design capacity method"""

    Cooling_Design_Capacity_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the cooling design capacity per total floor area of cooled zones served by the unit."""

    Fraction_Of_Autosized_Cooling_Design_Capacity: Annotated[float, Field(ge=0.0)]
    """Enter the fraction of auto-sized cooling design capacity. Required field when the cooling"""

    Maximum_Chilled_Water_Flow_Rate: Annotated[float, Field(default=...)]

    Control_Type: Annotated[Literal['MeanAirTemperature', 'MeanRadiantTemperature', 'OperativeTemperature', 'OutdoorDryBulbTemperature', 'OutdoorWetBulbTemperature'], Field(default='MeanAirTemperature')]
    """Temperature on which unit is controlled"""

    Cooling_Control_Throttling_Range: Annotated[str, Field(default='0.5')]

    Cooling_Control_Temperature_Schedule_Name: Annotated[str, Field()]

    Condensation_Control_Type: Annotated[Literal['Off', 'SimpleOff', 'VariableOff'], Field(default='SimpleOff')]

    Condensation_Control_Dewpoint_Offset: Annotated[str, Field(default='1.0')]

    Fraction_Radiant: Annotated[float, Field(default=..., ge=0, le=1)]

    Fraction_Of_Radiant_Energy_Incident_On_People: Annotated[float, Field(ge=0, le=1)]

    Surface_1_Name: Annotated[str, Field()]
    """Radiant energy may be distributed to specific surfaces"""

    Fraction_Of_Radiant_Energy_To_Surface_1: Annotated[float, Field(ge=0, le=1)]

    Surface_2_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_2: Annotated[float, Field(ge=0, le=1)]

    Surface_3_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_3: Annotated[float, Field(ge=0, le=1)]

    Surface_4_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_4: Annotated[float, Field(ge=0, le=1)]

    Surface_5_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_5: Annotated[float, Field(ge=0, le=1)]

    Surface_6_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_6: Annotated[float, Field(ge=0, le=1)]

    Surface_7_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_7: Annotated[float, Field(ge=0, le=1)]

    Surface_8_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_8: Annotated[float, Field(ge=0, le=1)]

    Surface_9_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_9: Annotated[float, Field(ge=0, le=1)]

    Surface_10_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_10: Annotated[float, Field(ge=0, le=1)]

    Surface_11_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_11: Annotated[float, Field(ge=0, le=1)]

    Surface_12_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_12: Annotated[float, Field(ge=0, le=1)]

    Surface_13_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_13: Annotated[float, Field(ge=0, le=1)]

    Surface_14_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_14: Annotated[float, Field(ge=0, le=1)]

    Surface_15_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_15: Annotated[float, Field(ge=0, le=1)]

    Surface_16_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_16: Annotated[float, Field(ge=0, le=1)]

    Surface_17_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_17: Annotated[float, Field(ge=0, le=1)]

    Surface_18_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_18: Annotated[float, Field(ge=0, le=1)]

    Surface_19_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_19: Annotated[float, Field(ge=0, le=1)]

    Surface_20_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_20: Annotated[float, Field(ge=0, le=1)]

    Surface_21_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_21: Annotated[float, Field(ge=0, le=1)]

    Surface_22_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_22: Annotated[float, Field(ge=0, le=1)]

    Surface_23_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_23: Annotated[float, Field(ge=0, le=1)]

    Surface_24_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_24: Annotated[float, Field(ge=0, le=1)]

    Surface_25_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_25: Annotated[float, Field(ge=0, le=1)]

    Surface_26_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_26: Annotated[float, Field(ge=0, le=1)]

    Surface_27_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_27: Annotated[float, Field(ge=0, le=1)]

    Surface_28_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_28: Annotated[float, Field(ge=0, le=1)]

    Surface_29_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_29: Annotated[float, Field(ge=0, le=1)]

    Surface_30_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_30: Annotated[float, Field(ge=0, le=1)]

    Surface_31_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_31: Annotated[float, Field(ge=0, le=1)]

    Surface_32_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_32: Annotated[float, Field(ge=0, le=1)]

    Surface_33_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_33: Annotated[float, Field(ge=0, le=1)]

    Surface_34_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_34: Annotated[float, Field(ge=0, le=1)]

    Surface_35_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_35: Annotated[float, Field(ge=0, le=1)]

    Surface_36_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_36: Annotated[float, Field(ge=0, le=1)]

    Surface_37_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_37: Annotated[float, Field(ge=0, le=1)]

    Surface_38_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_38: Annotated[float, Field(ge=0, le=1)]

    Surface_39_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_39: Annotated[float, Field(ge=0, le=1)]

    Surface_40_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_40: Annotated[float, Field(ge=0, le=1)]

    Surface_41_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_41: Annotated[float, Field(ge=0, le=1)]

    Surface_42_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_42: Annotated[float, Field(ge=0, le=1)]

    Surface_43_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_43: Annotated[float, Field(ge=0, le=1)]

    Surface_44_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_44: Annotated[float, Field(ge=0, le=1)]

    Surface_45_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_45: Annotated[float, Field(ge=0, le=1)]

    Surface_46_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_46: Annotated[float, Field(ge=0, le=1)]

    Surface_47_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_47: Annotated[float, Field(ge=0, le=1)]

    Surface_48_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_48: Annotated[float, Field(ge=0, le=1)]

    Surface_49_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_49: Annotated[float, Field(ge=0, le=1)]

    Surface_50_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_50: Annotated[float, Field(ge=0, le=1)]

    Surface_51_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_51: Annotated[float, Field(ge=0, le=1)]

    Surface_52_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_52: Annotated[float, Field(ge=0, le=1)]

    Surface_53_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_53: Annotated[float, Field(ge=0, le=1)]

    Surface_54_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_54: Annotated[float, Field(ge=0, le=1)]

    Surface_55_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_55: Annotated[float, Field(ge=0, le=1)]

    Surface_56_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_56: Annotated[float, Field(ge=0, le=1)]

    Surface_57_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_57: Annotated[float, Field(ge=0, le=1)]

    Surface_58_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_58: Annotated[float, Field(ge=0, le=1)]

    Surface_59_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_59: Annotated[float, Field(ge=0, le=1)]

    Surface_60_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_60: Annotated[float, Field(ge=0, le=1)]

    Surface_61_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_61: Annotated[float, Field(ge=0, le=1)]

    Surface_62_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_62: Annotated[float, Field(ge=0, le=1)]

    Surface_63_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_63: Annotated[float, Field(ge=0, le=1)]

    Surface_64_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_64: Annotated[float, Field(ge=0, le=1)]

    Surface_65_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_65: Annotated[float, Field(ge=0, le=1)]

    Surface_66_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_66: Annotated[float, Field(ge=0, le=1)]

    Surface_67_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_67: Annotated[float, Field(ge=0, le=1)]

    Surface_68_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_68: Annotated[float, Field(ge=0, le=1)]

    Surface_69_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_69: Annotated[float, Field(ge=0, le=1)]

    Surface_70_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_70: Annotated[float, Field(ge=0, le=1)]

    Surface_71_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_71: Annotated[float, Field(ge=0, le=1)]

    Surface_72_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_72: Annotated[float, Field(ge=0, le=1)]

    Surface_73_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_73: Annotated[float, Field(ge=0, le=1)]

    Surface_74_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_74: Annotated[float, Field(ge=0, le=1)]

    Surface_75_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_75: Annotated[float, Field(ge=0, le=1)]

    Surface_76_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_76: Annotated[float, Field(ge=0, le=1)]

    Surface_77_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_77: Annotated[float, Field(ge=0, le=1)]

    Surface_78_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_78: Annotated[float, Field(ge=0, le=1)]

    Surface_79_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_79: Annotated[float, Field(ge=0, le=1)]

    Surface_80_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_80: Annotated[float, Field(ge=0, le=1)]

    Surface_81_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_81: Annotated[float, Field(ge=0, le=1)]

    Surface_82_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_82: Annotated[float, Field(ge=0, le=1)]

    Surface_83_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_83: Annotated[float, Field(ge=0, le=1)]

    Surface_84_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_84: Annotated[float, Field(ge=0, le=1)]

    Surface_85_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_85: Annotated[float, Field(ge=0, le=1)]

    Surface_86_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_86: Annotated[float, Field(ge=0, le=1)]

    Surface_87_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_87: Annotated[float, Field(ge=0, le=1)]

    Surface_88_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_88: Annotated[float, Field(ge=0, le=1)]

    Surface_89_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_89: Annotated[float, Field(ge=0, le=1)]

    Surface_90_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_90: Annotated[float, Field(ge=0, le=1)]

    Surface_91_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_91: Annotated[float, Field(ge=0, le=1)]

    Surface_92_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_92: Annotated[float, Field(ge=0, le=1)]

    Surface_93_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_93: Annotated[float, Field(ge=0, le=1)]

    Surface_94_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_94: Annotated[float, Field(ge=0, le=1)]

    Surface_95_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_95: Annotated[float, Field(ge=0, le=1)]

    Surface_96_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_96: Annotated[float, Field(ge=0, le=1)]

    Surface_97_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_97: Annotated[float, Field(ge=0, le=1)]

    Surface_98_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_98: Annotated[float, Field(ge=0, le=1)]

    Surface_99_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_99: Annotated[float, Field(ge=0, le=1)]

    Surface_100_Name: Annotated[str, Field()]

    Fraction_Of_Radiant_Energy_To_Surface_100: Annotated[float, Field(ge=0, le=1)]