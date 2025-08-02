from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Hightemperatureradiant(EpBunch):
    """The number of surfaces can be expanded beyond 100, if necessary, by adding more"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Zone_Name: Annotated[str, Field(default=...)]
    """Name of zone system is serving"""

    Heating_Design_Capacity_Method: Annotated[Literal['HeatingDesignCapacity', 'CapacityPerFloorArea', 'FractionOfAutosizedHeatingCapacity'], Field(default='HeatingDesignCapacity')]
    """Enter the method used to determine the maximum heating power input capacity."""

    Heating_Design_Capacity: Annotated[float, Field(ge=0.0, default=autosize)]
    """Enter the design heating capacity.Required field when the heating design capacity method"""

    Heating_Design_Capacity_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the heating design capacity per zone floor area.Required field when the heating design"""

    Fraction_of_Autosized_Heating_Design_Capacity: Annotated[float, Field(ge=0.0, default=1.0)]
    """Enter the fraction of auto - sized heating design capacity.Required field when capacity the"""

    Fuel_Type: Annotated[Literal['NaturalGas', 'Electricity'], Field(default=...)]
    """Natural gas or electricity"""

    Combustion_Efficiency: Annotated[str, Field(default='0.9')]
    """Not used for non-gas radiant heaters"""

    Fraction_of_Input_Converted_to_Radiant_Energy: Annotated[str, Field(default='0.7')]
    """Radiant+latent+lost fractions must sum to 1 or less, remainder is considered convective heat"""

    Fraction_of_Input_Converted_to_Latent_Energy: Annotated[str, Field(default='0.0')]

    Fraction_of_Input_that_Is_Lost: Annotated[str, Field(default='0.0')]
    """Fraction of input vented to outdoor environment"""

    Temperature_Control_Type: Annotated[Literal['MeanAirTemperature', 'MeanRadiantTemperature', 'OperativeTemperature', 'MeanAirTemperatureSetpoint', 'MeanRadiantTemperatureSetpoint', 'OperativeTemperatureSetpoint'], Field(default='OperativeTemperature')]
    """Temperature type used to control unit"""

    Heating_Throttling_Range: Annotated[str, Field(default='2.0')]

    Heating_Setpoint_Temperature_Schedule_Name: Annotated[str, Field()]
    """This setpoint is an "operative temperature" setpoint"""

    Fraction_of_Radiant_Energy_Incident_on_People: Annotated[str, Field()]
    """This will affect thermal comfort but from an energy balance standpoint this value"""

    Surface_1_Name: Annotated[str, Field()]
    """Radiant energy may be distributed to specific surfaces"""

    Fraction_of_Radiant_Energy_to_Surface_1: Annotated[str, Field()]

    Surface_2_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_2: Annotated[str, Field()]

    Surface_3_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_3: Annotated[str, Field()]

    Surface_4_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_4: Annotated[str, Field()]

    Surface_5_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_5: Annotated[str, Field()]

    Surface_6_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_6: Annotated[str, Field()]

    Surface_7_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_7: Annotated[str, Field()]

    Surface_8_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_8: Annotated[str, Field()]

    Surface_9_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_9: Annotated[str, Field()]

    Surface_10_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_10: Annotated[str, Field()]

    Surface_11_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_11: Annotated[str, Field()]

    Surface_12_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_12: Annotated[str, Field()]

    Surface_13_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_13: Annotated[str, Field()]

    Surface_14_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_14: Annotated[str, Field()]

    Surface_15_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_15: Annotated[str, Field()]

    Surface_16_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_16: Annotated[str, Field()]

    Surface_17_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_17: Annotated[str, Field()]

    Surface_18_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_18: Annotated[str, Field()]

    Surface_19_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_19: Annotated[str, Field()]

    Surface_20_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_20: Annotated[str, Field()]

    Surface_21_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_21: Annotated[str, Field()]

    Surface_22_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_22: Annotated[str, Field()]

    Surface_23_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_23: Annotated[str, Field()]

    Surface_24_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_24: Annotated[str, Field()]

    Surface_25_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_25: Annotated[str, Field()]

    Surface_26_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_26: Annotated[str, Field()]

    Surface_27_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_27: Annotated[str, Field()]

    Surface_28_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_28: Annotated[str, Field()]

    Surface_29_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_29: Annotated[str, Field()]

    Surface_30_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_30: Annotated[str, Field()]

    Surface_31_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_31: Annotated[str, Field()]

    Surface_32_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_32: Annotated[str, Field()]

    Surface_33_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_33: Annotated[str, Field()]

    Surface_34_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_34: Annotated[str, Field()]

    Surface_35_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_35: Annotated[str, Field()]

    Surface_36_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_36: Annotated[str, Field()]

    Surface_37_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_37: Annotated[str, Field()]

    Surface_38_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_38: Annotated[str, Field()]

    Surface_39_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_39: Annotated[str, Field()]

    Surface_40_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_40: Annotated[str, Field()]

    Surface_41_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_41: Annotated[str, Field()]

    Surface_42_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_42: Annotated[str, Field()]

    Surface_43_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_43: Annotated[str, Field()]

    Surface_44_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_44: Annotated[str, Field()]

    Surface_45_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_45: Annotated[str, Field()]

    Surface_46_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_46: Annotated[str, Field()]

    Surface_47_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_47: Annotated[str, Field()]

    Surface_48_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_48: Annotated[str, Field()]

    Surface_49_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_49: Annotated[str, Field()]

    Surface_50_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_50: Annotated[str, Field()]

    Surface_51_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_51: Annotated[str, Field()]

    Surface_52_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_52: Annotated[str, Field()]

    Surface_53_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_53: Annotated[str, Field()]

    Surface_54_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_54: Annotated[str, Field()]

    Surface_55_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_55: Annotated[str, Field()]

    Surface_56_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_56: Annotated[str, Field()]

    Surface_57_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_57: Annotated[str, Field()]

    Surface_58_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_58: Annotated[str, Field()]

    Surface_59_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_59: Annotated[str, Field()]

    Surface_60_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_60: Annotated[str, Field()]

    Surface_61_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_61: Annotated[str, Field()]

    Surface_62_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_62: Annotated[str, Field()]

    Surface_63_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_63: Annotated[str, Field()]

    Surface_64_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_64: Annotated[str, Field()]

    Surface_65_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_65: Annotated[str, Field()]

    Surface_66_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_66: Annotated[str, Field()]

    Surface_67_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_67: Annotated[str, Field()]

    Surface_68_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_68: Annotated[str, Field()]

    Surface_69_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_69: Annotated[str, Field()]

    Surface_70_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_70: Annotated[str, Field()]

    Surface_71_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_71: Annotated[str, Field()]

    Surface_72_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_72: Annotated[str, Field()]

    Surface_73_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_73: Annotated[str, Field()]

    Surface_74_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_74: Annotated[str, Field()]

    Surface_75_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_75: Annotated[str, Field()]

    Surface_76_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_76: Annotated[str, Field()]

    Surface_77_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_77: Annotated[str, Field()]

    Surface_78_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_78: Annotated[str, Field()]

    Surface_79_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_79: Annotated[str, Field()]

    Surface_80_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_80: Annotated[str, Field()]

    Surface_81_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_81: Annotated[str, Field()]

    Surface_82_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_82: Annotated[str, Field()]

    Surface_83_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_83: Annotated[str, Field()]

    Surface_84_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_84: Annotated[str, Field()]

    Surface_85_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_85: Annotated[str, Field()]

    Surface_86_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_86: Annotated[str, Field()]

    Surface_87_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_87: Annotated[str, Field()]

    Surface_88_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_88: Annotated[str, Field()]

    Surface_89_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_89: Annotated[str, Field()]

    Surface_90_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_90: Annotated[str, Field()]

    Surface_91_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_91: Annotated[str, Field()]

    Surface_92_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_92: Annotated[str, Field()]

    Surface_93_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_93: Annotated[str, Field()]

    Surface_94_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_94: Annotated[str, Field()]

    Surface_95_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_95: Annotated[str, Field()]

    Surface_96_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_96: Annotated[str, Field()]

    Surface_97_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_97: Annotated[str, Field()]

    Surface_98_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_98: Annotated[str, Field()]

    Surface_99_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_99: Annotated[str, Field()]

    Surface_100_Name: Annotated[str, Field()]

    Fraction_of_Radiant_Energy_to_Surface_100: Annotated[str, Field()]