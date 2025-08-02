from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Schedule_Day_Interval(EpBunch):
    """A Schedule:Day:Interval contains a full day of values with specified end times for each value"""

    Name: Annotated[str, Field(default=...)]

    Schedule_Type_Limits_Name: Annotated[str, Field()]

    Interpolate_to_Timestep: Annotated[Literal['Average', 'Linear', 'No'], Field(default='No')]
    """when the interval does not match the user specified timestep a Average choice will average between the intervals request (to"""

    Time_1: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_1: Annotated[str, Field()]

    Time_2: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_2: Annotated[str, Field()]

    Time_3: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_3: Annotated[str, Field()]

    Time_4: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_4: Annotated[str, Field()]

    Time_5: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_5: Annotated[str, Field()]

    Time_6: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_6: Annotated[str, Field()]

    Time_7: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_7: Annotated[str, Field()]

    Time_8: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_8: Annotated[str, Field()]

    Time_9: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_9: Annotated[str, Field()]

    Time_10: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_10: Annotated[str, Field()]

    Time_11: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_11: Annotated[str, Field()]

    Time_12: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_12: Annotated[str, Field()]

    Time_13: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_13: Annotated[str, Field()]

    Time_14: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_14: Annotated[str, Field()]

    Time_15: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_15: Annotated[str, Field()]

    Time_16: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_16: Annotated[str, Field()]

    Time_17: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_17: Annotated[str, Field()]

    Time_18: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_18: Annotated[str, Field()]

    Time_19: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_19: Annotated[str, Field()]

    Time_20: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_20: Annotated[str, Field()]

    Time_21: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_21: Annotated[str, Field()]

    Time_22: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_22: Annotated[str, Field()]

    Time_23: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_23: Annotated[str, Field()]

    Time_24: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_24: Annotated[str, Field()]

    Time_25: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_25: Annotated[str, Field()]

    Time_26: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_26: Annotated[str, Field()]

    Time_27: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_27: Annotated[str, Field()]

    Time_28: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_28: Annotated[str, Field()]

    Time_29: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_29: Annotated[str, Field()]

    Time_30: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_30: Annotated[str, Field()]

    Time_31: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_31: Annotated[str, Field()]

    Time_32: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_32: Annotated[str, Field()]

    Time_33: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_33: Annotated[str, Field()]

    Time_34: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_34: Annotated[str, Field()]

    Time_35: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_35: Annotated[str, Field()]

    Time_36: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_36: Annotated[str, Field()]

    Time_37: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_37: Annotated[str, Field()]

    Time_38: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_38: Annotated[str, Field()]

    Time_39: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_39: Annotated[str, Field()]

    Time_40: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_40: Annotated[str, Field()]

    Time_41: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_41: Annotated[str, Field()]

    Time_42: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_42: Annotated[str, Field()]

    Time_43: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_43: Annotated[str, Field()]

    Time_44: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_44: Annotated[str, Field()]

    Time_45: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_45: Annotated[str, Field()]

    Time_46: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_46: Annotated[str, Field()]

    Time_47: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_47: Annotated[str, Field()]

    Time_48: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_48: Annotated[str, Field()]

    Time_49: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_49: Annotated[str, Field()]

    Time_50: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_50: Annotated[str, Field()]

    Time_51: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_51: Annotated[str, Field()]

    Time_52: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_52: Annotated[str, Field()]

    Time_53: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_53: Annotated[str, Field()]

    Time_54: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_54: Annotated[str, Field()]

    Time_55: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_55: Annotated[str, Field()]

    Time_56: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_56: Annotated[str, Field()]

    Time_57: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_57: Annotated[str, Field()]

    Time_58: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_58: Annotated[str, Field()]

    Time_59: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_59: Annotated[str, Field()]

    Time_60: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_60: Annotated[str, Field()]

    Time_61: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_61: Annotated[str, Field()]

    Time_62: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_62: Annotated[str, Field()]

    Time_63: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_63: Annotated[str, Field()]

    Time_64: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_64: Annotated[str, Field()]

    Time_65: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_65: Annotated[str, Field()]

    Time_66: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_66: Annotated[str, Field()]

    Time_67: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_67: Annotated[str, Field()]

    Time_68: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_68: Annotated[str, Field()]

    Time_69: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_69: Annotated[str, Field()]

    Time_70: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_70: Annotated[str, Field()]

    Time_71: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_71: Annotated[str, Field()]

    Time_72: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_72: Annotated[str, Field()]

    Time_73: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_73: Annotated[str, Field()]

    Time_74: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_74: Annotated[str, Field()]

    Time_75: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_75: Annotated[str, Field()]

    Time_76: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_76: Annotated[str, Field()]

    Time_77: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_77: Annotated[str, Field()]

    Time_78: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_78: Annotated[str, Field()]

    Time_79: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_79: Annotated[str, Field()]

    Time_80: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_80: Annotated[str, Field()]

    Time_81: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_81: Annotated[str, Field()]

    Time_82: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_82: Annotated[str, Field()]

    Time_83: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_83: Annotated[str, Field()]

    Time_84: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_84: Annotated[str, Field()]

    Time_85: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_85: Annotated[str, Field()]

    Time_86: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_86: Annotated[str, Field()]

    Time_87: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_87: Annotated[str, Field()]

    Time_88: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_88: Annotated[str, Field()]

    Time_89: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_89: Annotated[str, Field()]

    Time_90: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_90: Annotated[str, Field()]

    Time_91: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_91: Annotated[str, Field()]

    Time_92: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_92: Annotated[str, Field()]

    Time_93: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_93: Annotated[str, Field()]

    Time_94: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_94: Annotated[str, Field()]

    Time_95: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_95: Annotated[str, Field()]

    Time_96: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_96: Annotated[str, Field()]

    Time_97: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_97: Annotated[str, Field()]

    Time_98: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_98: Annotated[str, Field()]

    Time_99: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_99: Annotated[str, Field()]

    Time_100: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_100: Annotated[str, Field()]

    Time_101: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_101: Annotated[str, Field()]

    Time_102: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_102: Annotated[str, Field()]

    Time_103: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_103: Annotated[str, Field()]

    Time_104: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_104: Annotated[str, Field()]

    Time_105: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_105: Annotated[str, Field()]

    Time_106: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_106: Annotated[str, Field()]

    Time_107: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_107: Annotated[str, Field()]

    Time_108: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_108: Annotated[str, Field()]

    Time_109: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_109: Annotated[str, Field()]

    Time_110: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_110: Annotated[str, Field()]

    Time_111: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_111: Annotated[str, Field()]

    Time_112: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_112: Annotated[str, Field()]

    Time_113: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_113: Annotated[str, Field()]

    Time_114: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_114: Annotated[str, Field()]

    Time_115: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_115: Annotated[str, Field()]

    Time_116: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_116: Annotated[str, Field()]

    Time_117: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_117: Annotated[str, Field()]

    Time_118: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_118: Annotated[str, Field()]

    Time_119: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_119: Annotated[str, Field()]

    Time_120: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_120: Annotated[str, Field()]

    Time_121: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_121: Annotated[str, Field()]

    Time_122: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_122: Annotated[str, Field()]

    Time_123: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_123: Annotated[str, Field()]

    Time_124: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_124: Annotated[str, Field()]

    Time_125: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_125: Annotated[str, Field()]

    Time_126: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_126: Annotated[str, Field()]

    Time_127: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_127: Annotated[str, Field()]

    Time_128: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_128: Annotated[str, Field()]

    Time_129: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_129: Annotated[str, Field()]

    Time_130: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_130: Annotated[str, Field()]

    Time_131: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_131: Annotated[str, Field()]

    Time_132: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_132: Annotated[str, Field()]

    Time_133: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_133: Annotated[str, Field()]

    Time_134: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_134: Annotated[str, Field()]

    Time_135: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_135: Annotated[str, Field()]

    Time_136: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_136: Annotated[str, Field()]

    Time_137: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_137: Annotated[str, Field()]

    Time_138: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_138: Annotated[str, Field()]

    Time_139: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_139: Annotated[str, Field()]

    Time_140: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_140: Annotated[str, Field()]

    Time_141: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_141: Annotated[str, Field()]

    Time_142: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_142: Annotated[str, Field()]

    Time_143: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_143: Annotated[str, Field()]

    Time_144: Annotated[str, Field()]
    """"until" includes the time entered."""

    Value_Until_Time_144: Annotated[str, Field()]