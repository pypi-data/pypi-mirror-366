from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheatexchanger_Responsefactors(EpBunch):
    """Response factor definitions from third-party tool, commonly referred to a "g-functions""""

    Name: Annotated[str, Field(default=...)]

    Ghe_Vertical_Properties_Object_Name: Annotated[str, Field(default=...)]

    Number_Of_Boreholes: Annotated[int, Field(default=...)]

    G_Function_Reference_Ratio: Annotated[float, Field(gt=0.0, default=0.0005)]

    G_Function_Ln_T_Ts__Value_1: Annotated[float, Field(default=...)]

    G_Function_G_Value_1: Annotated[float, Field(default=...)]

    G_Function_Ln_T_Ts__Value_2: Annotated[float, Field()]

    G_Function_G_Value_2: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_3: Annotated[float, Field()]

    G_Function_G_Value_3: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_4: Annotated[float, Field()]

    G_Function_G_Value_4: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_5: Annotated[float, Field()]

    G_Function_G_Value_5: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_6: Annotated[float, Field()]

    G_Function_G_Value_6: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_7: Annotated[float, Field()]

    G_Function_G_Value_7: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_8: Annotated[float, Field()]

    G_Function_G_Value_8: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_9: Annotated[float, Field()]

    G_Function_G_Value_9: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_10: Annotated[float, Field()]

    G_Function_G_Value_10: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_11: Annotated[float, Field()]

    G_Function_G_Value_11: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_12: Annotated[float, Field()]

    G_Function_G_Value_12: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_13: Annotated[float, Field()]

    G_Function_G_Value_13: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_14: Annotated[float, Field()]

    G_Function_G_Value_14: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_15: Annotated[float, Field()]

    G_Function_G_Value_15: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_16: Annotated[float, Field()]

    G_Function_G_Value_16: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_17: Annotated[float, Field()]

    G_Function_G_Value_17: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_18: Annotated[float, Field()]

    G_Function_G_Value_18: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_19: Annotated[float, Field()]

    G_Function_G_Value_19: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_20: Annotated[float, Field()]

    G_Function_G_Value_20: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_21: Annotated[float, Field()]

    G_Function_G_Value_21: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_22: Annotated[float, Field()]

    G_Function_G_Value_22: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_23: Annotated[float, Field()]

    G_Function_G_Value_23: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_24: Annotated[float, Field()]

    G_Function_G_Value_24: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_25: Annotated[float, Field()]

    G_Function_G_Value_25: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_26: Annotated[float, Field()]

    G_Function_G_Value_26: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_27: Annotated[float, Field()]

    G_Function_G_Value_27: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_28: Annotated[float, Field()]

    G_Function_G_Value_28: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_29: Annotated[float, Field()]

    G_Function_G_Value_29: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_30: Annotated[float, Field()]

    G_Function_G_Value_30: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_31: Annotated[float, Field()]

    G_Function_G_Value_31: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_32: Annotated[float, Field()]

    G_Function_G_Value_32: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_33: Annotated[float, Field()]

    G_Function_G_Value_33: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_34: Annotated[float, Field()]

    G_Function_G_Value_34: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_35: Annotated[float, Field()]

    G_Function_G_Value_35: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_36: Annotated[float, Field()]

    G_Function_G_Value_36: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_37: Annotated[float, Field()]

    G_Function_G_Value_37: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_38: Annotated[float, Field()]

    G_Function_G_Value_38: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_39: Annotated[float, Field()]

    G_Function_G_Value_39: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_40: Annotated[float, Field()]

    G_Function_G_Value_40: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_41: Annotated[float, Field()]

    G_Function_G_Value_41: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_42: Annotated[float, Field()]

    G_Function_G_Value_42: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_43: Annotated[float, Field()]

    G_Function_G_Value_43: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_44: Annotated[float, Field()]

    G_Function_G_Value_44: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_45: Annotated[float, Field()]

    G_Function_G_Value_45: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_46: Annotated[float, Field()]

    G_Function_G_Value_46: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_47: Annotated[float, Field()]

    G_Function_G_Value_47: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_48: Annotated[float, Field()]

    G_Function_G_Value_48: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_49: Annotated[float, Field()]

    G_Function_G_Value_49: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_50: Annotated[float, Field()]

    G_Function_G_Value_50: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_51: Annotated[float, Field()]

    G_Function_G_Value_51: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_52: Annotated[float, Field()]

    G_Function_G_Value_52: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_53: Annotated[float, Field()]

    G_Function_G_Value_53: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_54: Annotated[float, Field()]

    G_Function_G_Value_54: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_55: Annotated[float, Field()]

    G_Function_G_Value_55: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_56: Annotated[float, Field()]

    G_Function_G_Value_56: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_57: Annotated[float, Field()]

    G_Function_G_Value_57: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_58: Annotated[float, Field()]

    G_Function_G_Value_58: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_59: Annotated[float, Field()]

    G_Function_G_Value_59: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_60: Annotated[float, Field()]

    G_Function_G_Value_60: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_61: Annotated[float, Field()]

    G_Function_G_Value_61: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_62: Annotated[float, Field()]

    G_Function_G_Value_62: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_63: Annotated[float, Field()]

    G_Function_G_Value_63: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_64: Annotated[float, Field()]

    G_Function_G_Value_64: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_65: Annotated[float, Field()]

    G_Function_G_Value_65: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_66: Annotated[float, Field()]

    G_Function_G_Value_66: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_67: Annotated[float, Field()]

    G_Function_G_Value_67: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_68: Annotated[float, Field()]

    G_Function_G_Value_68: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_69: Annotated[float, Field()]

    G_Function_G_Value_69: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_70: Annotated[float, Field()]

    G_Function_G_Value_70: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_71: Annotated[float, Field()]

    G_Function_G_Value_71: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_72: Annotated[float, Field()]

    G_Function_G_Value_72: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_73: Annotated[float, Field()]

    G_Function_G_Value_73: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_74: Annotated[float, Field()]

    G_Function_G_Value_74: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_75: Annotated[float, Field()]

    G_Function_G_Value_75: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_76: Annotated[float, Field()]

    G_Function_G_Value_76: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_77: Annotated[float, Field()]

    G_Function_G_Value_77: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_78: Annotated[float, Field()]

    G_Function_G_Value_78: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_79: Annotated[float, Field()]

    G_Function_G_Value_79: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_80: Annotated[float, Field()]

    G_Function_G_Value_80: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_81: Annotated[float, Field()]

    G_Function_G_Value_81: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_82: Annotated[float, Field()]

    G_Function_G_Value_82: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_83: Annotated[float, Field()]

    G_Function_G_Value_83: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_84: Annotated[float, Field()]

    G_Function_G_Value_84: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_85: Annotated[float, Field()]

    G_Function_G_Value_85: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_86: Annotated[float, Field()]

    G_Function_G_Value_86: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_87: Annotated[float, Field()]

    G_Function_G_Value_87: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_88: Annotated[float, Field()]

    G_Function_G_Value_88: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_89: Annotated[float, Field()]

    G_Function_G_Value_89: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_90: Annotated[float, Field()]

    G_Function_G_Value_90: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_91: Annotated[float, Field()]

    G_Function_G_Value_91: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_92: Annotated[float, Field()]

    G_Function_G_Value_92: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_93: Annotated[float, Field()]

    G_Function_G_Value_93: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_94: Annotated[float, Field()]

    G_Function_G_Value_94: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_95: Annotated[float, Field()]

    G_Function_G_Value_95: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_96: Annotated[float, Field()]

    G_Function_G_Value_96: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_97: Annotated[float, Field()]

    G_Function_G_Value_97: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_98: Annotated[float, Field()]

    G_Function_G_Value_98: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_99: Annotated[float, Field()]

    G_Function_G_Value_99: Annotated[float, Field()]

    G_Function_Ln_T_Ts__Value_100: Annotated[float, Field()]

    G_Function_G_Value_100: Annotated[float, Field()]