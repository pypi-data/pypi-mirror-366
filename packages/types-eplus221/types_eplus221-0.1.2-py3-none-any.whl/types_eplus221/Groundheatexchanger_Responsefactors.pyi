from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheatexchanger_Responsefactors(EpBunch):
    """Response factor definitions from third-party tool, commonly referred to a "g-functions""""

    Name: Annotated[str, Field(default=...)]

    GHEVerticalProperties_Object_Name: Annotated[str, Field(default=...)]

    Number_of_Boreholes: Annotated[int, Field(default=...)]

    GFunction_Reference_Ratio: Annotated[float, Field(gt=0.0, default=0.0005)]

    gFunction_LnTTs_Value_1: Annotated[float, Field(default=...)]

    gFunction_g_Value_1: Annotated[float, Field(default=...)]

    gFunction_LnTTs_Value_2: Annotated[float, Field()]

    gFunction_g_Value_2: Annotated[float, Field()]

    gFunction_LnTTs_Value_3: Annotated[float, Field()]

    gFunction_g_Value_3: Annotated[float, Field()]

    gFunction_LnTTs_Value_4: Annotated[float, Field()]

    gFunction_g_Value_4: Annotated[float, Field()]

    gFunction_LnTTs_Value_5: Annotated[float, Field()]

    gFunction_g_Value_5: Annotated[float, Field()]

    gFunction_LnTTs_Value_6: Annotated[float, Field()]

    gFunction_g_Value_6: Annotated[float, Field()]

    gFunction_LnTTs_Value_7: Annotated[float, Field()]

    gFunction_g_Value_7: Annotated[float, Field()]

    gFunction_LnTTs_Value_8: Annotated[float, Field()]

    gFunction_g_Value_8: Annotated[float, Field()]

    gFunction_LnTTs_Value_9: Annotated[float, Field()]

    gFunction_g_Value_9: Annotated[float, Field()]

    gFunction_LnTTs_Value_10: Annotated[float, Field()]

    gFunction_g_Value_10: Annotated[float, Field()]

    gFunction_LnTTs_Value_11: Annotated[float, Field()]

    gFunction_g_Value_11: Annotated[float, Field()]

    gFunction_LnTTs_Value_12: Annotated[float, Field()]

    gFunction_g_Value_12: Annotated[float, Field()]

    gFunction_LnTTs_Value_13: Annotated[float, Field()]

    gFunction_g_Value_13: Annotated[float, Field()]

    gFunction_LnTTs_Value_14: Annotated[float, Field()]

    gFunction_g_Value_14: Annotated[float, Field()]

    gFunction_LnTTs_Value_15: Annotated[float, Field()]

    gFunction_g_Value_15: Annotated[float, Field()]

    gFunction_LnTTs_Value_16: Annotated[float, Field()]

    gFunction_g_Value_16: Annotated[float, Field()]

    gFunction_LnTTs_Value_17: Annotated[float, Field()]

    gFunction_g_Value_17: Annotated[float, Field()]

    gFunction_LnTTs_Value_18: Annotated[float, Field()]

    gFunction_g_Value_18: Annotated[float, Field()]

    gFunction_LnTTs_Value_19: Annotated[float, Field()]

    gFunction_g_Value_19: Annotated[float, Field()]

    gFunction_LnTTs_Value_20: Annotated[float, Field()]

    gFunction_g_Value_20: Annotated[float, Field()]

    gFunction_LnTTs_Value_21: Annotated[float, Field()]

    gFunction_g_Value_21: Annotated[float, Field()]

    gFunction_LnTTs_Value_22: Annotated[float, Field()]

    gFunction_g_Value_22: Annotated[float, Field()]

    gFunction_LnTTs_Value_23: Annotated[float, Field()]

    gFunction_g_Value_23: Annotated[float, Field()]

    gFunction_LnTTs_Value_24: Annotated[float, Field()]

    gFunction_g_Value_24: Annotated[float, Field()]

    gFunction_LnTTs_Value_25: Annotated[float, Field()]

    gFunction_g_Value_25: Annotated[float, Field()]

    gFunction_LnTTs_Value_26: Annotated[float, Field()]

    gFunction_g_Value_26: Annotated[float, Field()]

    gFunction_LnTTs_Value_27: Annotated[float, Field()]

    gFunction_g_Value_27: Annotated[float, Field()]

    gFunction_LnTTs_Value_28: Annotated[float, Field()]

    gFunction_g_Value_28: Annotated[float, Field()]

    gFunction_LnTTs_Value_29: Annotated[float, Field()]

    gFunction_g_Value_29: Annotated[float, Field()]

    gFunction_LnTTs_Value_30: Annotated[float, Field()]

    gFunction_g_Value_30: Annotated[float, Field()]

    gFunction_LnTTs_Value_31: Annotated[float, Field()]

    gFunction_g_Value_31: Annotated[float, Field()]

    gFunction_LnTTs_Value_32: Annotated[float, Field()]

    gFunction_g_Value_32: Annotated[float, Field()]

    gFunction_LnTTs_Value_33: Annotated[float, Field()]

    gFunction_g_Value_33: Annotated[float, Field()]

    gFunction_LnTTs_Value_34: Annotated[float, Field()]

    gFunction_g_Value_34: Annotated[float, Field()]

    gFunction_LnTTs_Value_35: Annotated[float, Field()]

    gFunction_g_Value_35: Annotated[float, Field()]

    gFunction_LnTTs_Value_36: Annotated[float, Field()]

    gFunction_g_Value_36: Annotated[float, Field()]

    gFunction_LnTTs_Value_37: Annotated[float, Field()]

    gFunction_g_Value_37: Annotated[float, Field()]

    gFunction_LnTTs_Value_38: Annotated[float, Field()]

    gFunction_g_Value_38: Annotated[float, Field()]

    gFunction_LnTTs_Value_39: Annotated[float, Field()]

    gFunction_g_Value_39: Annotated[float, Field()]

    gFunction_LnTTs_Value_40: Annotated[float, Field()]

    gFunction_g_Value_40: Annotated[float, Field()]

    gFunction_LnTTs_Value_41: Annotated[float, Field()]

    gFunction_g_Value_41: Annotated[float, Field()]

    gFunction_LnTTs_Value_42: Annotated[float, Field()]

    gFunction_g_Value_42: Annotated[float, Field()]

    gFunction_LnTTs_Value_43: Annotated[float, Field()]

    gFunction_g_Value_43: Annotated[float, Field()]

    gFunction_LnTTs_Value_44: Annotated[float, Field()]

    gFunction_g_Value_44: Annotated[float, Field()]

    gFunction_LnTTs_Value_45: Annotated[float, Field()]

    gFunction_g_Value_45: Annotated[float, Field()]

    gFunction_LnTTs_Value_46: Annotated[float, Field()]

    gFunction_g_Value_46: Annotated[float, Field()]

    gFunction_LnTTs_Value_47: Annotated[float, Field()]

    gFunction_g_Value_47: Annotated[float, Field()]

    gFunction_LnTTs_Value_48: Annotated[float, Field()]

    gFunction_g_Value_48: Annotated[float, Field()]

    gFunction_LnTTs_Value_49: Annotated[float, Field()]

    gFunction_g_Value_49: Annotated[float, Field()]

    gFunction_LnTTs_Value_50: Annotated[float, Field()]

    gFunction_g_Value_50: Annotated[float, Field()]

    gFunction_LnTTs_Value_51: Annotated[float, Field()]

    gFunction_g_Value_51: Annotated[float, Field()]

    gFunction_LnTTs_Value_52: Annotated[float, Field()]

    gFunction_g_Value_52: Annotated[float, Field()]

    gFunction_LnTTs_Value_53: Annotated[float, Field()]

    gFunction_g_Value_53: Annotated[float, Field()]

    gFunction_LnTTs_Value_54: Annotated[float, Field()]

    gFunction_g_Value_54: Annotated[float, Field()]

    gFunction_LnTTs_Value_55: Annotated[float, Field()]

    gFunction_g_Value_55: Annotated[float, Field()]

    gFunction_LnTTs_Value_56: Annotated[float, Field()]

    gFunction_g_Value_56: Annotated[float, Field()]

    gFunction_LnTTs_Value_57: Annotated[float, Field()]

    gFunction_g_Value_57: Annotated[float, Field()]

    gFunction_LnTTs_Value_58: Annotated[float, Field()]

    gFunction_g_Value_58: Annotated[float, Field()]

    gFunction_LnTTs_Value_59: Annotated[float, Field()]

    gFunction_g_Value_59: Annotated[float, Field()]

    gFunction_LnTTs_Value_60: Annotated[float, Field()]

    gFunction_g_Value_60: Annotated[float, Field()]

    gFunction_LnTTs_Value_61: Annotated[float, Field()]

    gFunction_g_Value_61: Annotated[float, Field()]

    gFunction_LnTTs_Value_62: Annotated[float, Field()]

    gFunction_g_Value_62: Annotated[float, Field()]

    gFunction_LnTTs_Value_63: Annotated[float, Field()]

    gFunction_g_Value_63: Annotated[float, Field()]

    gFunction_LnTTs_Value_64: Annotated[float, Field()]

    gFunction_g_Value_64: Annotated[float, Field()]

    gFunction_LnTTs_Value_65: Annotated[float, Field()]

    gFunction_g_Value_65: Annotated[float, Field()]

    gFunction_LnTTs_Value_66: Annotated[float, Field()]

    gFunction_g_Value_66: Annotated[float, Field()]

    gFunction_LnTTs_Value_67: Annotated[float, Field()]

    gFunction_g_Value_67: Annotated[float, Field()]

    gFunction_LnTTs_Value_68: Annotated[float, Field()]

    gFunction_g_Value_68: Annotated[float, Field()]

    gFunction_LnTTs_Value_69: Annotated[float, Field()]

    gFunction_g_Value_69: Annotated[float, Field()]

    gFunction_LnTTs_Value_70: Annotated[float, Field()]

    gFunction_g_Value_70: Annotated[float, Field()]

    gFunction_LnTTs_Value_71: Annotated[float, Field()]

    gFunction_g_Value_71: Annotated[float, Field()]

    gFunction_LnTTs_Value_72: Annotated[float, Field()]

    gFunction_g_Value_72: Annotated[float, Field()]

    gFunction_LnTTs_Value_73: Annotated[float, Field()]

    gFunction_g_Value_73: Annotated[float, Field()]

    gFunction_LnTTs_Value_74: Annotated[float, Field()]

    gFunction_g_Value_74: Annotated[float, Field()]

    gFunction_LnTTs_Value_75: Annotated[float, Field()]

    gFunction_g_Value_75: Annotated[float, Field()]

    gFunction_LnTTs_Value_76: Annotated[float, Field()]

    gFunction_g_Value_76: Annotated[float, Field()]

    gFunction_LnTTs_Value_77: Annotated[float, Field()]

    gFunction_g_Value_77: Annotated[float, Field()]

    gFunction_LnTTs_Value_78: Annotated[float, Field()]

    gFunction_g_Value_78: Annotated[float, Field()]

    gFunction_LnTTs_Value_79: Annotated[float, Field()]

    gFunction_g_Value_79: Annotated[float, Field()]

    gFunction_LnTTs_Value_80: Annotated[float, Field()]

    gFunction_g_Value_80: Annotated[float, Field()]

    gFunction_LnTTs_Value_81: Annotated[float, Field()]

    gFunction_g_Value_81: Annotated[float, Field()]

    gFunction_LnTTs_Value_82: Annotated[float, Field()]

    gFunction_g_Value_82: Annotated[float, Field()]

    gFunction_LnTTs_Value_83: Annotated[float, Field()]

    gFunction_g_Value_83: Annotated[float, Field()]

    gFunction_LnTTs_Value_84: Annotated[float, Field()]

    gFunction_g_Value_84: Annotated[float, Field()]

    gFunction_LnTTs_Value_85: Annotated[float, Field()]

    gFunction_g_Value_85: Annotated[float, Field()]

    gFunction_LnTTs_Value_86: Annotated[float, Field()]

    gFunction_g_Value_86: Annotated[float, Field()]

    gFunction_LnTTs_Value_87: Annotated[float, Field()]

    gFunction_g_Value_87: Annotated[float, Field()]

    gFunction_LnTTs_Value_88: Annotated[float, Field()]

    gFunction_g_Value_88: Annotated[float, Field()]

    gFunction_LnTTs_Value_89: Annotated[float, Field()]

    gFunction_g_Value_89: Annotated[float, Field()]

    gFunction_LnTTs_Value_90: Annotated[float, Field()]

    gFunction_g_Value_90: Annotated[float, Field()]

    gFunction_LnTTs_Value_91: Annotated[float, Field()]

    gFunction_g_Value_91: Annotated[float, Field()]

    gFunction_LnTTs_Value_92: Annotated[float, Field()]

    gFunction_g_Value_92: Annotated[float, Field()]

    gFunction_LnTTs_Value_93: Annotated[float, Field()]

    gFunction_g_Value_93: Annotated[float, Field()]

    gFunction_LnTTs_Value_94: Annotated[float, Field()]

    gFunction_g_Value_94: Annotated[float, Field()]

    gFunction_LnTTs_Value_95: Annotated[float, Field()]

    gFunction_g_Value_95: Annotated[float, Field()]

    gFunction_LnTTs_Value_96: Annotated[float, Field()]

    gFunction_g_Value_96: Annotated[float, Field()]

    gFunction_LnTTs_Value_97: Annotated[float, Field()]

    gFunction_g_Value_97: Annotated[float, Field()]

    gFunction_LnTTs_Value_98: Annotated[float, Field()]

    gFunction_g_Value_98: Annotated[float, Field()]

    gFunction_LnTTs_Value_99: Annotated[float, Field()]

    gFunction_g_Value_99: Annotated[float, Field()]

    gFunction_LnTTs_Value_100: Annotated[float, Field()]

    gFunction_g_Value_100: Annotated[float, Field()]