from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zoneproperty_Userviewfactors_Bysurfacename(EpBunch):
    """View factors for Surface to Surface in a zone."""

    Zone_Or_Zonelist_Name: Annotated[str, Field()]
    """View factors may be entered for a single zone or for a group of zones connected by Construction:AirBoundary"""

    From_Surface_1: Annotated[str, Field()]

    To_Surface_1: Annotated[str, Field()]

    View_Factor_1: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_2: Annotated[str, Field()]

    To_Surface_2: Annotated[str, Field()]

    View_Factor_2: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_3: Annotated[str, Field()]

    To_Surface_3: Annotated[str, Field()]

    View_Factor_3: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_4: Annotated[str, Field()]

    To_Surface_4: Annotated[str, Field()]

    View_Factor_4: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_5: Annotated[str, Field()]

    To_Surface_5: Annotated[str, Field()]

    View_Factor_5: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_6: Annotated[str, Field()]

    To_Surface_6: Annotated[str, Field()]

    View_Factor_6: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_7: Annotated[str, Field()]

    To_Surface_7: Annotated[str, Field()]

    View_Factor_7: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_8: Annotated[str, Field()]

    To_Surface_8: Annotated[str, Field()]

    View_Factor_8: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_9: Annotated[str, Field()]

    To_Surface_9: Annotated[str, Field()]

    View_Factor_9: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_10: Annotated[str, Field()]

    To_Surface_10: Annotated[str, Field()]

    View_Factor_10: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_11: Annotated[str, Field()]

    To_Surface_11: Annotated[str, Field()]

    View_Factor_11: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_12: Annotated[str, Field()]

    To_Surface_12: Annotated[str, Field()]

    View_Factor_12: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_13: Annotated[str, Field()]

    To_Surface_13: Annotated[str, Field()]

    View_Factor_13: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_14: Annotated[str, Field()]

    To_Surface_14: Annotated[str, Field()]

    View_Factor_14: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_15: Annotated[str, Field()]

    To_Surface_15: Annotated[str, Field()]

    View_Factor_15: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_16: Annotated[str, Field()]

    To_Surface_16: Annotated[str, Field()]

    View_Factor_16: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_17: Annotated[str, Field()]

    To_Surface_17: Annotated[str, Field()]

    View_Factor_17: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_18: Annotated[str, Field()]

    To_Surface_18: Annotated[str, Field()]

    View_Factor_18: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_19: Annotated[str, Field()]

    To_Surface_19: Annotated[str, Field()]

    View_Factor_19: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_20: Annotated[str, Field()]

    To_Surface_20: Annotated[str, Field()]

    View_Factor_20: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_21: Annotated[str, Field()]

    To_Surface_21: Annotated[str, Field()]

    View_Factor_21: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_22: Annotated[str, Field()]

    To_Surface_22: Annotated[str, Field()]

    View_Factor_22: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_23: Annotated[str, Field()]

    To_Surface_23: Annotated[str, Field()]

    View_Factor_23: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_24: Annotated[str, Field()]

    To_Surface_24: Annotated[str, Field()]

    View_Factor_24: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_25: Annotated[str, Field()]

    To_Surface_25: Annotated[str, Field()]

    View_Factor_25: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_26: Annotated[str, Field()]

    To_Surface_26: Annotated[str, Field()]

    View_Factor_26: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_27: Annotated[str, Field()]

    To_Surface_27: Annotated[str, Field()]

    View_Factor_27: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_28: Annotated[str, Field()]

    To_Surface_28: Annotated[str, Field()]

    View_Factor_28: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_29: Annotated[str, Field()]

    To_Surface_29: Annotated[str, Field()]

    View_Factor_29: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_30: Annotated[str, Field()]

    To_Surface_30: Annotated[str, Field()]

    View_Factor_30: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_31: Annotated[str, Field()]

    To_Surface_31: Annotated[str, Field()]

    View_Factor_31: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_32: Annotated[str, Field()]

    To_Surface_32: Annotated[str, Field()]

    View_Factor_32: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_33: Annotated[str, Field()]

    To_Surface_33: Annotated[str, Field()]

    View_Factor_33: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_34: Annotated[str, Field()]

    To_Surface_34: Annotated[str, Field()]

    View_Factor_34: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_35: Annotated[str, Field()]

    To_Surface_35: Annotated[str, Field()]

    View_Factor_35: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_36: Annotated[str, Field()]

    To_Surface_36: Annotated[str, Field()]

    View_Factor_36: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_37: Annotated[str, Field()]

    To_Surface_37: Annotated[str, Field()]

    View_Factor_37: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_38: Annotated[str, Field()]

    To_Surface_38: Annotated[str, Field()]

    View_Factor_38: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_39: Annotated[str, Field()]

    To_Surface_39: Annotated[str, Field()]

    View_Factor_39: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_40: Annotated[str, Field()]

    To_Surface_40: Annotated[str, Field()]

    View_Factor_40: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_41: Annotated[str, Field()]

    To_Surface_41: Annotated[str, Field()]

    View_Factor_41: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_42: Annotated[str, Field()]

    To_Surface_42: Annotated[str, Field()]

    View_Factor_42: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_43: Annotated[str, Field()]

    To_Surface_43: Annotated[str, Field()]

    View_Factor_43: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_44: Annotated[str, Field()]

    To_Surface_44: Annotated[str, Field()]

    View_Factor_44: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_45: Annotated[str, Field()]

    To_Surface_45: Annotated[str, Field()]

    View_Factor_45: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_46: Annotated[str, Field()]

    To_Surface_46: Annotated[str, Field()]

    View_Factor_46: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_47: Annotated[str, Field()]

    To_Surface_47: Annotated[str, Field()]

    View_Factor_47: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_48: Annotated[str, Field()]

    To_Surface_48: Annotated[str, Field()]

    View_Factor_48: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_49: Annotated[str, Field()]

    To_Surface_49: Annotated[str, Field()]

    View_Factor_49: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_50: Annotated[str, Field()]

    To_Surface_50: Annotated[str, Field()]

    View_Factor_50: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_51: Annotated[str, Field()]

    To_Surface_51: Annotated[str, Field()]

    View_Factor_51: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_52: Annotated[str, Field()]

    To_Surface_52: Annotated[str, Field()]

    View_Factor_52: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_53: Annotated[str, Field()]

    To_Surface_53: Annotated[str, Field()]

    View_Factor_53: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_54: Annotated[str, Field()]

    To_Surface_54: Annotated[str, Field()]

    View_Factor_54: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_55: Annotated[str, Field()]

    To_Surface_55: Annotated[str, Field()]

    View_Factor_55: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_56: Annotated[str, Field()]

    To_Surface_56: Annotated[str, Field()]

    View_Factor_56: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_57: Annotated[str, Field()]

    To_Surface_57: Annotated[str, Field()]

    View_Factor_57: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_58: Annotated[str, Field()]

    To_Surface_58: Annotated[str, Field()]

    View_Factor_58: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_59: Annotated[str, Field()]

    To_Surface_59: Annotated[str, Field()]

    View_Factor_59: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_60: Annotated[str, Field()]

    To_Surface_60: Annotated[str, Field()]

    View_Factor_60: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_61: Annotated[str, Field()]

    To_Surface_61: Annotated[str, Field()]

    View_Factor_61: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_62: Annotated[str, Field()]

    To_Surface_62: Annotated[str, Field()]

    View_Factor_62: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_63: Annotated[str, Field()]

    To_Surface_63: Annotated[str, Field()]

    View_Factor_63: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_64: Annotated[str, Field()]

    To_Surface_64: Annotated[str, Field()]

    View_Factor_64: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_65: Annotated[str, Field()]

    To_Surface_65: Annotated[str, Field()]

    View_Factor_65: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_66: Annotated[str, Field()]

    To_Surface_66: Annotated[str, Field()]

    View_Factor_66: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_67: Annotated[str, Field()]

    To_Surface_67: Annotated[str, Field()]

    View_Factor_67: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_68: Annotated[str, Field()]

    To_Surface_68: Annotated[str, Field()]

    View_Factor_68: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_69: Annotated[str, Field()]

    To_Surface_69: Annotated[str, Field()]

    View_Factor_69: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_70: Annotated[str, Field()]

    To_Surface_70: Annotated[str, Field()]

    View_Factor_70: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_71: Annotated[str, Field()]

    To_Surface_71: Annotated[str, Field()]

    View_Factor_71: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_72: Annotated[str, Field()]

    To_Surface_72: Annotated[str, Field()]

    View_Factor_72: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_73: Annotated[str, Field()]

    To_Surface_73: Annotated[str, Field()]

    View_Factor_73: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_74: Annotated[str, Field()]

    To_Surface_74: Annotated[str, Field()]

    View_Factor_74: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_75: Annotated[str, Field()]

    To_Surface_75: Annotated[str, Field()]

    View_Factor_75: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_76: Annotated[str, Field()]

    To_Surface_76: Annotated[str, Field()]

    View_Factor_76: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_77: Annotated[str, Field()]

    To_Surface_77: Annotated[str, Field()]

    View_Factor_77: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_78: Annotated[str, Field()]

    To_Surface_78: Annotated[str, Field()]

    View_Factor_78: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_79: Annotated[str, Field()]

    To_Surface_79: Annotated[str, Field()]

    View_Factor_79: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_80: Annotated[str, Field()]

    To_Surface_80: Annotated[str, Field()]

    View_Factor_80: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_81: Annotated[str, Field()]

    To_Surface_81: Annotated[str, Field()]

    View_Factor_81: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_82: Annotated[str, Field()]

    To_Surface_82: Annotated[str, Field()]

    View_Factor_82: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_83: Annotated[str, Field()]

    To_Surface_83: Annotated[str, Field()]

    View_Factor_83: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_84: Annotated[str, Field()]

    To_Surface_84: Annotated[str, Field()]

    View_Factor_84: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_85: Annotated[str, Field()]

    To_Surface_85: Annotated[str, Field()]

    View_Factor_85: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_86: Annotated[str, Field()]

    To_Surface_86: Annotated[str, Field()]

    View_Factor_86: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_87: Annotated[str, Field()]

    To_Surface_87: Annotated[str, Field()]

    View_Factor_87: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_88: Annotated[str, Field()]

    To_Surface_88: Annotated[str, Field()]

    View_Factor_88: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_89: Annotated[str, Field()]

    To_Surface_89: Annotated[str, Field()]

    View_Factor_89: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_90: Annotated[str, Field()]

    To_Surface_90: Annotated[str, Field()]

    View_Factor_90: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_91: Annotated[str, Field()]

    To_Surface_91: Annotated[str, Field()]

    View_Factor_91: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_92: Annotated[str, Field()]

    To_Surface_92: Annotated[str, Field()]

    View_Factor_92: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_93: Annotated[str, Field()]

    To_Surface_93: Annotated[str, Field()]

    View_Factor_93: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_94: Annotated[str, Field()]

    To_Surface_94: Annotated[str, Field()]

    View_Factor_94: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_95: Annotated[str, Field()]

    To_Surface_95: Annotated[str, Field()]

    View_Factor_95: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_96: Annotated[str, Field()]

    To_Surface_96: Annotated[str, Field()]

    View_Factor_96: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_97: Annotated[str, Field()]

    To_Surface_97: Annotated[str, Field()]

    View_Factor_97: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_98: Annotated[str, Field()]

    To_Surface_98: Annotated[str, Field()]

    View_Factor_98: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_99: Annotated[str, Field()]

    To_Surface_99: Annotated[str, Field()]

    View_Factor_99: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_100: Annotated[str, Field()]

    To_Surface_100: Annotated[str, Field()]

    View_Factor_100: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_101: Annotated[str, Field()]

    To_Surface_101: Annotated[str, Field()]

    View_Factor_101: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_102: Annotated[str, Field()]

    To_Surface_102: Annotated[str, Field()]

    View_Factor_102: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_103: Annotated[str, Field()]

    To_Surface_103: Annotated[str, Field()]

    View_Factor_103: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_104: Annotated[str, Field()]

    To_Surface_104: Annotated[str, Field()]

    View_Factor_104: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_105: Annotated[str, Field()]

    To_Surface_105: Annotated[str, Field()]

    View_Factor_105: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_106: Annotated[str, Field()]

    To_Surface_106: Annotated[str, Field()]

    View_Factor_106: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_107: Annotated[str, Field()]

    To_Surface_107: Annotated[str, Field()]

    View_Factor_107: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_108: Annotated[str, Field()]

    To_Surface_108: Annotated[str, Field()]

    View_Factor_108: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_109: Annotated[str, Field()]

    To_Surface_109: Annotated[str, Field()]

    View_Factor_109: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_110: Annotated[str, Field()]

    To_Surface_110: Annotated[str, Field()]

    View_Factor_110: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_111: Annotated[str, Field()]

    To_Surface_111: Annotated[str, Field()]

    View_Factor_111: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_112: Annotated[str, Field()]

    To_Surface_112: Annotated[str, Field()]

    View_Factor_112: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_113: Annotated[str, Field()]

    To_Surface_113: Annotated[str, Field()]

    View_Factor_113: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_114: Annotated[str, Field()]

    To_Surface_114: Annotated[str, Field()]

    View_Factor_114: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_115: Annotated[str, Field()]

    To_Surface_115: Annotated[str, Field()]

    View_Factor_115: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_116: Annotated[str, Field()]

    To_Surface_116: Annotated[str, Field()]

    View_Factor_116: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_117: Annotated[str, Field()]

    To_Surface_117: Annotated[str, Field()]

    View_Factor_117: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_118: Annotated[str, Field()]

    To_Surface_118: Annotated[str, Field()]

    View_Factor_118: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_119: Annotated[str, Field()]

    To_Surface_119: Annotated[str, Field()]

    View_Factor_119: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_120: Annotated[str, Field()]

    To_Surface_120: Annotated[str, Field()]

    View_Factor_120: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_121: Annotated[str, Field()]

    To_Surface_121: Annotated[str, Field()]

    View_Factor_121: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_122: Annotated[str, Field()]

    To_Surface_122: Annotated[str, Field()]

    View_Factor_122: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_123: Annotated[str, Field()]

    To_Surface_123: Annotated[str, Field()]

    View_Factor_123: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_124: Annotated[str, Field()]

    To_Surface_124: Annotated[str, Field()]

    View_Factor_124: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_125: Annotated[str, Field()]

    To_Surface_125: Annotated[str, Field()]

    View_Factor_125: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_126: Annotated[str, Field()]

    To_Surface_126: Annotated[str, Field()]

    View_Factor_126: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_127: Annotated[str, Field()]

    To_Surface_127: Annotated[str, Field()]

    View_Factor_127: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_128: Annotated[str, Field()]

    To_Surface_128: Annotated[str, Field()]

    View_Factor_128: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_129: Annotated[str, Field()]

    To_Surface_129: Annotated[str, Field()]

    View_Factor_129: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_130: Annotated[str, Field()]

    To_Surface_130: Annotated[str, Field()]

    View_Factor_130: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_131: Annotated[str, Field()]

    To_Surface_131: Annotated[str, Field()]

    View_Factor_131: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_132: Annotated[str, Field()]

    To_Surface_132: Annotated[str, Field()]

    View_Factor_132: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_133: Annotated[str, Field()]

    To_Surface_133: Annotated[str, Field()]

    View_Factor_133: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_134: Annotated[str, Field()]

    To_Surface_134: Annotated[str, Field()]

    View_Factor_134: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_135: Annotated[str, Field()]

    To_Surface_135: Annotated[str, Field()]

    View_Factor_135: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_136: Annotated[str, Field()]

    To_Surface_136: Annotated[str, Field()]

    View_Factor_136: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_137: Annotated[str, Field()]

    To_Surface_137: Annotated[str, Field()]

    View_Factor_137: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_138: Annotated[str, Field()]

    To_Surface_138: Annotated[str, Field()]

    View_Factor_138: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_139: Annotated[str, Field()]

    To_Surface_139: Annotated[str, Field()]

    View_Factor_139: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_140: Annotated[str, Field()]

    To_Surface_140: Annotated[str, Field()]

    View_Factor_140: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_141: Annotated[str, Field()]

    To_Surface_141: Annotated[str, Field()]

    View_Factor_141: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_142: Annotated[str, Field()]

    To_Surface_142: Annotated[str, Field()]

    View_Factor_142: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_143: Annotated[str, Field()]

    To_Surface_143: Annotated[str, Field()]

    View_Factor_143: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_144: Annotated[str, Field()]

    To_Surface_144: Annotated[str, Field()]

    View_Factor_144: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_145: Annotated[str, Field()]

    To_Surface_145: Annotated[str, Field()]

    View_Factor_145: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_146: Annotated[str, Field()]

    To_Surface_146: Annotated[str, Field()]

    View_Factor_146: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_147: Annotated[str, Field()]

    To_Surface_147: Annotated[str, Field()]

    View_Factor_147: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_148: Annotated[str, Field()]

    To_Surface_148: Annotated[str, Field()]

    View_Factor_148: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_149: Annotated[str, Field()]

    To_Surface_149: Annotated[str, Field()]

    View_Factor_149: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_150: Annotated[str, Field()]

    To_Surface_150: Annotated[str, Field()]

    View_Factor_150: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_151: Annotated[str, Field()]

    To_Surface_151: Annotated[str, Field()]

    View_Factor_151: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_152: Annotated[str, Field()]

    To_Surface_152: Annotated[str, Field()]

    View_Factor_152: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_153: Annotated[str, Field()]

    To_Surface_153: Annotated[str, Field()]

    View_Factor_153: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_154: Annotated[str, Field()]

    To_Surface_154: Annotated[str, Field()]

    View_Factor_154: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_155: Annotated[str, Field()]

    To_Surface_155: Annotated[str, Field()]

    View_Factor_155: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_156: Annotated[str, Field()]

    To_Surface_156: Annotated[str, Field()]

    View_Factor_156: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_157: Annotated[str, Field()]

    To_Surface_157: Annotated[str, Field()]

    View_Factor_157: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_158: Annotated[str, Field()]

    To_Surface_158: Annotated[str, Field()]

    View_Factor_158: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_159: Annotated[str, Field()]

    To_Surface_159: Annotated[str, Field()]

    View_Factor_159: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_160: Annotated[str, Field()]

    To_Surface_160: Annotated[str, Field()]

    View_Factor_160: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_161: Annotated[str, Field()]

    To_Surface_161: Annotated[str, Field()]

    View_Factor_161: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_162: Annotated[str, Field()]

    To_Surface_162: Annotated[str, Field()]

    View_Factor_162: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_163: Annotated[str, Field()]

    To_Surface_163: Annotated[str, Field()]

    View_Factor_163: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_164: Annotated[str, Field()]

    To_Surface_164: Annotated[str, Field()]

    View_Factor_164: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_165: Annotated[str, Field()]

    To_Surface_165: Annotated[str, Field()]

    View_Factor_165: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_166: Annotated[str, Field()]

    To_Surface_166: Annotated[str, Field()]

    View_Factor_166: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_167: Annotated[str, Field()]

    To_Surface_167: Annotated[str, Field()]

    View_Factor_167: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_168: Annotated[str, Field()]

    To_Surface_168: Annotated[str, Field()]

    View_Factor_168: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_169: Annotated[str, Field()]

    To_Surface_169: Annotated[str, Field()]

    View_Factor_169: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_170: Annotated[str, Field()]

    To_Surface_170: Annotated[str, Field()]

    View_Factor_170: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_171: Annotated[str, Field()]

    To_Surface_171: Annotated[str, Field()]

    View_Factor_171: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_172: Annotated[str, Field()]

    To_Surface_172: Annotated[str, Field()]

    View_Factor_172: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_173: Annotated[str, Field()]

    To_Surface_173: Annotated[str, Field()]

    View_Factor_173: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_174: Annotated[str, Field()]

    To_Surface_174: Annotated[str, Field()]

    View_Factor_174: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_175: Annotated[str, Field()]

    To_Surface_175: Annotated[str, Field()]

    View_Factor_175: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_176: Annotated[str, Field()]

    To_Surface_176: Annotated[str, Field()]

    View_Factor_176: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_177: Annotated[str, Field()]

    To_Surface_177: Annotated[str, Field()]

    View_Factor_177: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_178: Annotated[str, Field()]

    To_Surface_178: Annotated[str, Field()]

    View_Factor_178: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_179: Annotated[str, Field()]

    To_Surface_179: Annotated[str, Field()]

    View_Factor_179: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_180: Annotated[str, Field()]

    To_Surface_180: Annotated[str, Field()]

    View_Factor_180: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_181: Annotated[str, Field()]

    To_Surface_181: Annotated[str, Field()]

    View_Factor_181: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_182: Annotated[str, Field()]

    To_Surface_182: Annotated[str, Field()]

    View_Factor_182: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_183: Annotated[str, Field()]

    To_Surface_183: Annotated[str, Field()]

    View_Factor_183: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_184: Annotated[str, Field()]

    To_Surface_184: Annotated[str, Field()]

    View_Factor_184: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_185: Annotated[str, Field()]

    To_Surface_185: Annotated[str, Field()]

    View_Factor_185: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_186: Annotated[str, Field()]

    To_Surface_186: Annotated[str, Field()]

    View_Factor_186: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_187: Annotated[str, Field()]

    To_Surface_187: Annotated[str, Field()]

    View_Factor_187: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_188: Annotated[str, Field()]

    To_Surface_188: Annotated[str, Field()]

    View_Factor_188: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_189: Annotated[str, Field()]

    To_Surface_189: Annotated[str, Field()]

    View_Factor_189: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_190: Annotated[str, Field()]

    To_Surface_190: Annotated[str, Field()]

    View_Factor_190: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_191: Annotated[str, Field()]

    To_Surface_191: Annotated[str, Field()]

    View_Factor_191: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_192: Annotated[str, Field()]

    To_Surface_192: Annotated[str, Field()]

    View_Factor_192: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_193: Annotated[str, Field()]

    To_Surface_193: Annotated[str, Field()]

    View_Factor_193: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_194: Annotated[str, Field()]

    To_Surface_194: Annotated[str, Field()]

    View_Factor_194: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_195: Annotated[str, Field()]

    To_Surface_195: Annotated[str, Field()]

    View_Factor_195: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_196: Annotated[str, Field()]

    To_Surface_196: Annotated[str, Field()]

    View_Factor_196: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_197: Annotated[str, Field()]

    To_Surface_197: Annotated[str, Field()]

    View_Factor_197: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_198: Annotated[str, Field()]

    To_Surface_198: Annotated[str, Field()]

    View_Factor_198: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_199: Annotated[str, Field()]

    To_Surface_199: Annotated[str, Field()]

    View_Factor_199: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_200: Annotated[str, Field()]

    To_Surface_200: Annotated[str, Field()]

    View_Factor_200: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_201: Annotated[str, Field()]

    To_Surface_201: Annotated[str, Field()]

    View_Factor_201: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_202: Annotated[str, Field()]

    To_Surface_202: Annotated[str, Field()]

    View_Factor_202: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_203: Annotated[str, Field()]

    To_Surface_203: Annotated[str, Field()]

    View_Factor_203: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_204: Annotated[str, Field()]

    To_Surface_204: Annotated[str, Field()]

    View_Factor_204: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_205: Annotated[str, Field()]

    To_Surface_205: Annotated[str, Field()]

    View_Factor_205: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_206: Annotated[str, Field()]

    To_Surface_206: Annotated[str, Field()]

    View_Factor_206: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_207: Annotated[str, Field()]

    To_Surface_207: Annotated[str, Field()]

    View_Factor_207: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_208: Annotated[str, Field()]

    To_Surface_208: Annotated[str, Field()]

    View_Factor_208: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_209: Annotated[str, Field()]

    To_Surface_209: Annotated[str, Field()]

    View_Factor_209: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_210: Annotated[str, Field()]

    To_Surface_210: Annotated[str, Field()]

    View_Factor_210: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_211: Annotated[str, Field()]

    To_Surface_211: Annotated[str, Field()]

    View_Factor_211: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_212: Annotated[str, Field()]

    To_Surface_212: Annotated[str, Field()]

    View_Factor_212: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_213: Annotated[str, Field()]

    To_Surface_213: Annotated[str, Field()]

    View_Factor_213: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_214: Annotated[str, Field()]

    To_Surface_214: Annotated[str, Field()]

    View_Factor_214: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_215: Annotated[str, Field()]

    To_Surface_215: Annotated[str, Field()]

    View_Factor_215: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_216: Annotated[str, Field()]

    To_Surface_216: Annotated[str, Field()]

    View_Factor_216: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_217: Annotated[str, Field()]

    To_Surface_217: Annotated[str, Field()]

    View_Factor_217: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_218: Annotated[str, Field()]

    To_Surface_218: Annotated[str, Field()]

    View_Factor_218: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_219: Annotated[str, Field()]

    To_Surface_219: Annotated[str, Field()]

    View_Factor_219: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_220: Annotated[str, Field()]

    To_Surface_220: Annotated[str, Field()]

    View_Factor_220: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_221: Annotated[str, Field()]

    To_Surface_221: Annotated[str, Field()]

    View_Factor_221: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_222: Annotated[str, Field()]

    To_Surface_222: Annotated[str, Field()]

    View_Factor_222: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_223: Annotated[str, Field()]

    To_Surface_223: Annotated[str, Field()]

    View_Factor_223: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_224: Annotated[str, Field()]

    To_Surface_224: Annotated[str, Field()]

    View_Factor_224: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_225: Annotated[str, Field()]

    To_Surface_225: Annotated[str, Field()]

    View_Factor_225: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_226: Annotated[str, Field()]

    To_Surface_226: Annotated[str, Field()]

    View_Factor_226: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_227: Annotated[str, Field()]

    To_Surface_227: Annotated[str, Field()]

    View_Factor_227: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_228: Annotated[str, Field()]

    To_Surface_228: Annotated[str, Field()]

    View_Factor_228: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_229: Annotated[str, Field()]

    To_Surface_229: Annotated[str, Field()]

    View_Factor_229: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_230: Annotated[str, Field()]

    To_Surface_230: Annotated[str, Field()]

    View_Factor_230: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_231: Annotated[str, Field()]

    To_Surface_231: Annotated[str, Field()]

    View_Factor_231: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_232: Annotated[str, Field()]

    To_Surface_232: Annotated[str, Field()]

    View_Factor_232: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_233: Annotated[str, Field()]

    To_Surface_233: Annotated[str, Field()]

    View_Factor_233: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_234: Annotated[str, Field()]

    To_Surface_234: Annotated[str, Field()]

    View_Factor_234: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_235: Annotated[str, Field()]

    To_Surface_235: Annotated[str, Field()]

    View_Factor_235: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_236: Annotated[str, Field()]

    To_Surface_236: Annotated[str, Field()]

    View_Factor_236: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_237: Annotated[str, Field()]

    To_Surface_237: Annotated[str, Field()]

    View_Factor_237: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_238: Annotated[str, Field()]

    To_Surface_238: Annotated[str, Field()]

    View_Factor_238: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_239: Annotated[str, Field()]

    To_Surface_239: Annotated[str, Field()]

    View_Factor_239: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_240: Annotated[str, Field()]

    To_Surface_240: Annotated[str, Field()]

    View_Factor_240: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_241: Annotated[str, Field()]

    To_Surface_241: Annotated[str, Field()]

    View_Factor_241: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_242: Annotated[str, Field()]

    To_Surface_242: Annotated[str, Field()]

    View_Factor_242: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_243: Annotated[str, Field()]

    To_Surface_243: Annotated[str, Field()]

    View_Factor_243: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_244: Annotated[str, Field()]

    To_Surface_244: Annotated[str, Field()]

    View_Factor_244: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_245: Annotated[str, Field()]

    To_Surface_245: Annotated[str, Field()]

    View_Factor_245: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_246: Annotated[str, Field()]

    To_Surface_246: Annotated[str, Field()]

    View_Factor_246: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_247: Annotated[str, Field()]

    To_Surface_247: Annotated[str, Field()]

    View_Factor_247: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_248: Annotated[str, Field()]

    To_Surface_248: Annotated[str, Field()]

    View_Factor_248: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_249: Annotated[str, Field()]

    To_Surface_249: Annotated[str, Field()]

    View_Factor_249: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_250: Annotated[str, Field()]

    To_Surface_250: Annotated[str, Field()]

    View_Factor_250: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_251: Annotated[str, Field()]

    To_Surface_251: Annotated[str, Field()]

    View_Factor_251: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_252: Annotated[str, Field()]

    To_Surface_252: Annotated[str, Field()]

    View_Factor_252: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_253: Annotated[str, Field()]

    To_Surface_253: Annotated[str, Field()]

    View_Factor_253: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_254: Annotated[str, Field()]

    To_Surface_254: Annotated[str, Field()]

    View_Factor_254: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_255: Annotated[str, Field()]

    To_Surface_255: Annotated[str, Field()]

    View_Factor_255: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_256: Annotated[str, Field()]

    To_Surface_256: Annotated[str, Field()]

    View_Factor_256: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_257: Annotated[str, Field()]

    To_Surface_257: Annotated[str, Field()]

    View_Factor_257: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_258: Annotated[str, Field()]

    To_Surface_258: Annotated[str, Field()]

    View_Factor_258: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_259: Annotated[str, Field()]

    To_Surface_259: Annotated[str, Field()]

    View_Factor_259: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_260: Annotated[str, Field()]

    To_Surface_260: Annotated[str, Field()]

    View_Factor_260: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_261: Annotated[str, Field()]

    To_Surface_261: Annotated[str, Field()]

    View_Factor_261: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_262: Annotated[str, Field()]

    To_Surface_262: Annotated[str, Field()]

    View_Factor_262: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_263: Annotated[str, Field()]

    To_Surface_263: Annotated[str, Field()]

    View_Factor_263: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_264: Annotated[str, Field()]

    To_Surface_264: Annotated[str, Field()]

    View_Factor_264: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_265: Annotated[str, Field()]

    To_Surface_265: Annotated[str, Field()]

    View_Factor_265: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_266: Annotated[str, Field()]

    To_Surface_266: Annotated[str, Field()]

    View_Factor_266: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_267: Annotated[str, Field()]

    To_Surface_267: Annotated[str, Field()]

    View_Factor_267: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_268: Annotated[str, Field()]

    To_Surface_268: Annotated[str, Field()]

    View_Factor_268: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_269: Annotated[str, Field()]

    To_Surface_269: Annotated[str, Field()]

    View_Factor_269: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_270: Annotated[str, Field()]

    To_Surface_270: Annotated[str, Field()]

    View_Factor_270: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_271: Annotated[str, Field()]

    To_Surface_271: Annotated[str, Field()]

    View_Factor_271: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_272: Annotated[str, Field()]

    To_Surface_272: Annotated[str, Field()]

    View_Factor_272: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_273: Annotated[str, Field()]

    To_Surface_273: Annotated[str, Field()]

    View_Factor_273: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_274: Annotated[str, Field()]

    To_Surface_274: Annotated[str, Field()]

    View_Factor_274: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_275: Annotated[str, Field()]

    To_Surface_275: Annotated[str, Field()]

    View_Factor_275: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_276: Annotated[str, Field()]

    To_Surface_276: Annotated[str, Field()]

    View_Factor_276: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_277: Annotated[str, Field()]

    To_Surface_277: Annotated[str, Field()]

    View_Factor_277: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_278: Annotated[str, Field()]

    To_Surface_278: Annotated[str, Field()]

    View_Factor_278: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_279: Annotated[str, Field()]

    To_Surface_279: Annotated[str, Field()]

    View_Factor_279: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_280: Annotated[str, Field()]

    To_Surface_280: Annotated[str, Field()]

    View_Factor_280: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_281: Annotated[str, Field()]

    To_Surface_281: Annotated[str, Field()]

    View_Factor_281: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_282: Annotated[str, Field()]

    To_Surface_282: Annotated[str, Field()]

    View_Factor_282: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_283: Annotated[str, Field()]

    To_Surface_283: Annotated[str, Field()]

    View_Factor_283: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_284: Annotated[str, Field()]

    To_Surface_284: Annotated[str, Field()]

    View_Factor_284: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_285: Annotated[str, Field()]

    To_Surface_285: Annotated[str, Field()]

    View_Factor_285: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_286: Annotated[str, Field()]

    To_Surface_286: Annotated[str, Field()]

    View_Factor_286: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_287: Annotated[str, Field()]

    To_Surface_287: Annotated[str, Field()]

    View_Factor_287: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_288: Annotated[str, Field()]

    To_Surface_288: Annotated[str, Field()]

    View_Factor_288: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_289: Annotated[str, Field()]

    To_Surface_289: Annotated[str, Field()]

    View_Factor_289: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_290: Annotated[str, Field()]

    To_Surface_290: Annotated[str, Field()]

    View_Factor_290: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_291: Annotated[str, Field()]

    To_Surface_291: Annotated[str, Field()]

    View_Factor_291: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_292: Annotated[str, Field()]

    To_Surface_292: Annotated[str, Field()]

    View_Factor_292: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_293: Annotated[str, Field()]

    To_Surface_293: Annotated[str, Field()]

    View_Factor_293: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_294: Annotated[str, Field()]

    To_Surface_294: Annotated[str, Field()]

    View_Factor_294: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_295: Annotated[str, Field()]

    To_Surface_295: Annotated[str, Field()]

    View_Factor_295: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_296: Annotated[str, Field()]

    To_Surface_296: Annotated[str, Field()]

    View_Factor_296: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_297: Annotated[str, Field()]

    To_Surface_297: Annotated[str, Field()]

    View_Factor_297: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_298: Annotated[str, Field()]

    To_Surface_298: Annotated[str, Field()]

    View_Factor_298: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_299: Annotated[str, Field()]

    To_Surface_299: Annotated[str, Field()]

    View_Factor_299: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_300: Annotated[str, Field()]

    To_Surface_300: Annotated[str, Field()]

    View_Factor_300: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_301: Annotated[str, Field()]

    To_Surface_301: Annotated[str, Field()]

    View_Factor_301: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_302: Annotated[str, Field()]

    To_Surface_302: Annotated[str, Field()]

    View_Factor_302: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_303: Annotated[str, Field()]

    To_Surface_303: Annotated[str, Field()]

    View_Factor_303: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_304: Annotated[str, Field()]

    To_Surface_304: Annotated[str, Field()]

    View_Factor_304: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_305: Annotated[str, Field()]

    To_Surface_305: Annotated[str, Field()]

    View_Factor_305: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_306: Annotated[str, Field()]

    To_Surface_306: Annotated[str, Field()]

    View_Factor_306: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_307: Annotated[str, Field()]

    To_Surface_307: Annotated[str, Field()]

    View_Factor_307: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_308: Annotated[str, Field()]

    To_Surface_308: Annotated[str, Field()]

    View_Factor_308: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_309: Annotated[str, Field()]

    To_Surface_309: Annotated[str, Field()]

    View_Factor_309: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_310: Annotated[str, Field()]

    To_Surface_310: Annotated[str, Field()]

    View_Factor_310: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_311: Annotated[str, Field()]

    To_Surface_311: Annotated[str, Field()]

    View_Factor_311: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_312: Annotated[str, Field()]

    To_Surface_312: Annotated[str, Field()]

    View_Factor_312: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_313: Annotated[str, Field()]

    To_Surface_313: Annotated[str, Field()]

    View_Factor_313: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_314: Annotated[str, Field()]

    To_Surface_314: Annotated[str, Field()]

    View_Factor_314: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_315: Annotated[str, Field()]

    To_Surface_315: Annotated[str, Field()]

    View_Factor_315: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_316: Annotated[str, Field()]

    To_Surface_316: Annotated[str, Field()]

    View_Factor_316: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_317: Annotated[str, Field()]

    To_Surface_317: Annotated[str, Field()]

    View_Factor_317: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_318: Annotated[str, Field()]

    To_Surface_318: Annotated[str, Field()]

    View_Factor_318: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_319: Annotated[str, Field()]

    To_Surface_319: Annotated[str, Field()]

    View_Factor_319: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_320: Annotated[str, Field()]

    To_Surface_320: Annotated[str, Field()]

    View_Factor_320: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_321: Annotated[str, Field()]

    To_Surface_321: Annotated[str, Field()]

    View_Factor_321: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_322: Annotated[str, Field()]

    To_Surface_322: Annotated[str, Field()]

    View_Factor_322: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_323: Annotated[str, Field()]

    To_Surface_323: Annotated[str, Field()]

    View_Factor_323: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_324: Annotated[str, Field()]

    To_Surface_324: Annotated[str, Field()]

    View_Factor_324: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_325: Annotated[str, Field()]

    To_Surface_325: Annotated[str, Field()]

    View_Factor_325: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_326: Annotated[str, Field()]

    To_Surface_326: Annotated[str, Field()]

    View_Factor_326: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_327: Annotated[str, Field()]

    To_Surface_327: Annotated[str, Field()]

    View_Factor_327: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_328: Annotated[str, Field()]

    To_Surface_328: Annotated[str, Field()]

    View_Factor_328: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_329: Annotated[str, Field()]

    To_Surface_329: Annotated[str, Field()]

    View_Factor_329: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_330: Annotated[str, Field()]

    To_Surface_330: Annotated[str, Field()]

    View_Factor_330: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_331: Annotated[str, Field()]

    To_Surface_331: Annotated[str, Field()]

    View_Factor_331: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_332: Annotated[str, Field()]

    To_Surface_332: Annotated[str, Field()]

    View_Factor_332: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_333: Annotated[str, Field()]

    To_Surface_333: Annotated[str, Field()]

    View_Factor_333: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_334: Annotated[str, Field()]

    To_Surface_334: Annotated[str, Field()]

    View_Factor_334: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_335: Annotated[str, Field()]

    To_Surface_335: Annotated[str, Field()]

    View_Factor_335: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_336: Annotated[str, Field()]

    To_Surface_336: Annotated[str, Field()]

    View_Factor_336: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_337: Annotated[str, Field()]

    To_Surface_337: Annotated[str, Field()]

    View_Factor_337: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_338: Annotated[str, Field()]

    To_Surface_338: Annotated[str, Field()]

    View_Factor_338: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_339: Annotated[str, Field()]

    To_Surface_339: Annotated[str, Field()]

    View_Factor_339: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_340: Annotated[str, Field()]

    To_Surface_340: Annotated[str, Field()]

    View_Factor_340: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_341: Annotated[str, Field()]

    To_Surface_341: Annotated[str, Field()]

    View_Factor_341: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_342: Annotated[str, Field()]

    To_Surface_342: Annotated[str, Field()]

    View_Factor_342: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_343: Annotated[str, Field()]

    To_Surface_343: Annotated[str, Field()]

    View_Factor_343: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_344: Annotated[str, Field()]

    To_Surface_344: Annotated[str, Field()]

    View_Factor_344: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_345: Annotated[str, Field()]

    To_Surface_345: Annotated[str, Field()]

    View_Factor_345: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_346: Annotated[str, Field()]

    To_Surface_346: Annotated[str, Field()]

    View_Factor_346: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_347: Annotated[str, Field()]

    To_Surface_347: Annotated[str, Field()]

    View_Factor_347: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_348: Annotated[str, Field()]

    To_Surface_348: Annotated[str, Field()]

    View_Factor_348: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_349: Annotated[str, Field()]

    To_Surface_349: Annotated[str, Field()]

    View_Factor_349: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_350: Annotated[str, Field()]

    To_Surface_350: Annotated[str, Field()]

    View_Factor_350: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_351: Annotated[str, Field()]

    To_Surface_351: Annotated[str, Field()]

    View_Factor_351: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_352: Annotated[str, Field()]

    To_Surface_352: Annotated[str, Field()]

    View_Factor_352: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_353: Annotated[str, Field()]

    To_Surface_353: Annotated[str, Field()]

    View_Factor_353: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_354: Annotated[str, Field()]

    To_Surface_354: Annotated[str, Field()]

    View_Factor_354: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_355: Annotated[str, Field()]

    To_Surface_355: Annotated[str, Field()]

    View_Factor_355: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_356: Annotated[str, Field()]

    To_Surface_356: Annotated[str, Field()]

    View_Factor_356: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_357: Annotated[str, Field()]

    To_Surface_357: Annotated[str, Field()]

    View_Factor_357: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_358: Annotated[str, Field()]

    To_Surface_358: Annotated[str, Field()]

    View_Factor_358: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_359: Annotated[str, Field()]

    To_Surface_359: Annotated[str, Field()]

    View_Factor_359: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_360: Annotated[str, Field()]

    To_Surface_360: Annotated[str, Field()]

    View_Factor_360: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_361: Annotated[str, Field()]

    To_Surface_361: Annotated[str, Field()]

    View_Factor_361: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_362: Annotated[str, Field()]

    To_Surface_362: Annotated[str, Field()]

    View_Factor_362: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_363: Annotated[str, Field()]

    To_Surface_363: Annotated[str, Field()]

    View_Factor_363: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_364: Annotated[str, Field()]

    To_Surface_364: Annotated[str, Field()]

    View_Factor_364: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_365: Annotated[str, Field()]

    To_Surface_365: Annotated[str, Field()]

    View_Factor_365: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_366: Annotated[str, Field()]

    To_Surface_366: Annotated[str, Field()]

    View_Factor_366: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_367: Annotated[str, Field()]

    To_Surface_367: Annotated[str, Field()]

    View_Factor_367: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_368: Annotated[str, Field()]

    To_Surface_368: Annotated[str, Field()]

    View_Factor_368: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_369: Annotated[str, Field()]

    To_Surface_369: Annotated[str, Field()]

    View_Factor_369: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_370: Annotated[str, Field()]

    To_Surface_370: Annotated[str, Field()]

    View_Factor_370: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_371: Annotated[str, Field()]

    To_Surface_371: Annotated[str, Field()]

    View_Factor_371: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_372: Annotated[str, Field()]

    To_Surface_372: Annotated[str, Field()]

    View_Factor_372: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_373: Annotated[str, Field()]

    To_Surface_373: Annotated[str, Field()]

    View_Factor_373: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_374: Annotated[str, Field()]

    To_Surface_374: Annotated[str, Field()]

    View_Factor_374: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_375: Annotated[str, Field()]

    To_Surface_375: Annotated[str, Field()]

    View_Factor_375: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_376: Annotated[str, Field()]

    To_Surface_376: Annotated[str, Field()]

    View_Factor_376: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_377: Annotated[str, Field()]

    To_Surface_377: Annotated[str, Field()]

    View_Factor_377: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_378: Annotated[str, Field()]

    To_Surface_378: Annotated[str, Field()]

    View_Factor_378: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_379: Annotated[str, Field()]

    To_Surface_379: Annotated[str, Field()]

    View_Factor_379: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_380: Annotated[str, Field()]

    To_Surface_380: Annotated[str, Field()]

    View_Factor_380: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_381: Annotated[str, Field()]

    To_Surface_381: Annotated[str, Field()]

    View_Factor_381: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_382: Annotated[str, Field()]

    To_Surface_382: Annotated[str, Field()]

    View_Factor_382: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_383: Annotated[str, Field()]

    To_Surface_383: Annotated[str, Field()]

    View_Factor_383: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_384: Annotated[str, Field()]

    To_Surface_384: Annotated[str, Field()]

    View_Factor_384: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_385: Annotated[str, Field()]

    To_Surface_385: Annotated[str, Field()]

    View_Factor_385: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_386: Annotated[str, Field()]

    To_Surface_386: Annotated[str, Field()]

    View_Factor_386: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_387: Annotated[str, Field()]

    To_Surface_387: Annotated[str, Field()]

    View_Factor_387: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_388: Annotated[str, Field()]

    To_Surface_388: Annotated[str, Field()]

    View_Factor_388: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_389: Annotated[str, Field()]

    To_Surface_389: Annotated[str, Field()]

    View_Factor_389: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_390: Annotated[str, Field()]

    To_Surface_390: Annotated[str, Field()]

    View_Factor_390: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_391: Annotated[str, Field()]

    To_Surface_391: Annotated[str, Field()]

    View_Factor_391: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_392: Annotated[str, Field()]

    To_Surface_392: Annotated[str, Field()]

    View_Factor_392: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_393: Annotated[str, Field()]

    To_Surface_393: Annotated[str, Field()]

    View_Factor_393: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_394: Annotated[str, Field()]

    To_Surface_394: Annotated[str, Field()]

    View_Factor_394: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_395: Annotated[str, Field()]

    To_Surface_395: Annotated[str, Field()]

    View_Factor_395: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_396: Annotated[str, Field()]

    To_Surface_396: Annotated[str, Field()]

    View_Factor_396: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_397: Annotated[str, Field()]

    To_Surface_397: Annotated[str, Field()]

    View_Factor_397: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_398: Annotated[str, Field()]

    To_Surface_398: Annotated[str, Field()]

    View_Factor_398: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_399: Annotated[str, Field()]

    To_Surface_399: Annotated[str, Field()]

    View_Factor_399: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_400: Annotated[str, Field()]

    To_Surface_400: Annotated[str, Field()]

    View_Factor_400: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_401: Annotated[str, Field()]

    To_Surface_401: Annotated[str, Field()]

    View_Factor_401: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_402: Annotated[str, Field()]

    To_Surface_402: Annotated[str, Field()]

    View_Factor_402: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_403: Annotated[str, Field()]

    To_Surface_403: Annotated[str, Field()]

    View_Factor_403: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_404: Annotated[str, Field()]

    To_Surface_404: Annotated[str, Field()]

    View_Factor_404: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_405: Annotated[str, Field()]

    To_Surface_405: Annotated[str, Field()]

    View_Factor_405: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_406: Annotated[str, Field()]

    To_Surface_406: Annotated[str, Field()]

    View_Factor_406: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_407: Annotated[str, Field()]

    To_Surface_407: Annotated[str, Field()]

    View_Factor_407: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_408: Annotated[str, Field()]

    To_Surface_408: Annotated[str, Field()]

    View_Factor_408: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_409: Annotated[str, Field()]

    To_Surface_409: Annotated[str, Field()]

    View_Factor_409: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_410: Annotated[str, Field()]

    To_Surface_410: Annotated[str, Field()]

    View_Factor_410: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_411: Annotated[str, Field()]

    To_Surface_411: Annotated[str, Field()]

    View_Factor_411: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_412: Annotated[str, Field()]

    To_Surface_412: Annotated[str, Field()]

    View_Factor_412: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_413: Annotated[str, Field()]

    To_Surface_413: Annotated[str, Field()]

    View_Factor_413: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_414: Annotated[str, Field()]

    To_Surface_414: Annotated[str, Field()]

    View_Factor_414: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_415: Annotated[str, Field()]

    To_Surface_415: Annotated[str, Field()]

    View_Factor_415: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_416: Annotated[str, Field()]

    To_Surface_416: Annotated[str, Field()]

    View_Factor_416: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_417: Annotated[str, Field()]

    To_Surface_417: Annotated[str, Field()]

    View_Factor_417: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_418: Annotated[str, Field()]

    To_Surface_418: Annotated[str, Field()]

    View_Factor_418: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_419: Annotated[str, Field()]

    To_Surface_419: Annotated[str, Field()]

    View_Factor_419: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_420: Annotated[str, Field()]

    To_Surface_420: Annotated[str, Field()]

    View_Factor_420: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_421: Annotated[str, Field()]

    To_Surface_421: Annotated[str, Field()]

    View_Factor_421: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_422: Annotated[str, Field()]

    To_Surface_422: Annotated[str, Field()]

    View_Factor_422: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_423: Annotated[str, Field()]

    To_Surface_423: Annotated[str, Field()]

    View_Factor_423: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_424: Annotated[str, Field()]

    To_Surface_424: Annotated[str, Field()]

    View_Factor_424: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_425: Annotated[str, Field()]

    To_Surface_425: Annotated[str, Field()]

    View_Factor_425: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_426: Annotated[str, Field()]

    To_Surface_426: Annotated[str, Field()]

    View_Factor_426: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_427: Annotated[str, Field()]

    To_Surface_427: Annotated[str, Field()]

    View_Factor_427: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_428: Annotated[str, Field()]

    To_Surface_428: Annotated[str, Field()]

    View_Factor_428: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_429: Annotated[str, Field()]

    To_Surface_429: Annotated[str, Field()]

    View_Factor_429: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_430: Annotated[str, Field()]

    To_Surface_430: Annotated[str, Field()]

    View_Factor_430: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_431: Annotated[str, Field()]

    To_Surface_431: Annotated[str, Field()]

    View_Factor_431: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_432: Annotated[str, Field()]

    To_Surface_432: Annotated[str, Field()]

    View_Factor_432: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_433: Annotated[str, Field()]

    To_Surface_433: Annotated[str, Field()]

    View_Factor_433: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_434: Annotated[str, Field()]

    To_Surface_434: Annotated[str, Field()]

    View_Factor_434: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_435: Annotated[str, Field()]

    To_Surface_435: Annotated[str, Field()]

    View_Factor_435: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_436: Annotated[str, Field()]

    To_Surface_436: Annotated[str, Field()]

    View_Factor_436: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_437: Annotated[str, Field()]

    To_Surface_437: Annotated[str, Field()]

    View_Factor_437: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_438: Annotated[str, Field()]

    To_Surface_438: Annotated[str, Field()]

    View_Factor_438: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_439: Annotated[str, Field()]

    To_Surface_439: Annotated[str, Field()]

    View_Factor_439: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_440: Annotated[str, Field()]

    To_Surface_440: Annotated[str, Field()]

    View_Factor_440: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_441: Annotated[str, Field()]

    To_Surface_441: Annotated[str, Field()]

    View_Factor_441: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_442: Annotated[str, Field()]

    To_Surface_442: Annotated[str, Field()]

    View_Factor_442: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_443: Annotated[str, Field()]

    To_Surface_443: Annotated[str, Field()]

    View_Factor_443: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_444: Annotated[str, Field()]

    To_Surface_444: Annotated[str, Field()]

    View_Factor_444: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_445: Annotated[str, Field()]

    To_Surface_445: Annotated[str, Field()]

    View_Factor_445: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_446: Annotated[str, Field()]

    To_Surface_446: Annotated[str, Field()]

    View_Factor_446: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_447: Annotated[str, Field()]

    To_Surface_447: Annotated[str, Field()]

    View_Factor_447: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_448: Annotated[str, Field()]

    To_Surface_448: Annotated[str, Field()]

    View_Factor_448: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_449: Annotated[str, Field()]

    To_Surface_449: Annotated[str, Field()]

    View_Factor_449: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_450: Annotated[str, Field()]

    To_Surface_450: Annotated[str, Field()]

    View_Factor_450: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_451: Annotated[str, Field()]

    To_Surface_451: Annotated[str, Field()]

    View_Factor_451: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_452: Annotated[str, Field()]

    To_Surface_452: Annotated[str, Field()]

    View_Factor_452: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_453: Annotated[str, Field()]

    To_Surface_453: Annotated[str, Field()]

    View_Factor_453: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_454: Annotated[str, Field()]

    To_Surface_454: Annotated[str, Field()]

    View_Factor_454: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_455: Annotated[str, Field()]

    To_Surface_455: Annotated[str, Field()]

    View_Factor_455: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_456: Annotated[str, Field()]

    To_Surface_456: Annotated[str, Field()]

    View_Factor_456: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_457: Annotated[str, Field()]

    To_Surface_457: Annotated[str, Field()]

    View_Factor_457: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_458: Annotated[str, Field()]

    To_Surface_458: Annotated[str, Field()]

    View_Factor_458: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_459: Annotated[str, Field()]

    To_Surface_459: Annotated[str, Field()]

    View_Factor_459: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_460: Annotated[str, Field()]

    To_Surface_460: Annotated[str, Field()]

    View_Factor_460: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_461: Annotated[str, Field()]

    To_Surface_461: Annotated[str, Field()]

    View_Factor_461: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_462: Annotated[str, Field()]

    To_Surface_462: Annotated[str, Field()]

    View_Factor_462: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_463: Annotated[str, Field()]

    To_Surface_463: Annotated[str, Field()]

    View_Factor_463: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_464: Annotated[str, Field()]

    To_Surface_464: Annotated[str, Field()]

    View_Factor_464: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_465: Annotated[str, Field()]

    To_Surface_465: Annotated[str, Field()]

    View_Factor_465: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_466: Annotated[str, Field()]

    To_Surface_466: Annotated[str, Field()]

    View_Factor_466: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_467: Annotated[str, Field()]

    To_Surface_467: Annotated[str, Field()]

    View_Factor_467: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_468: Annotated[str, Field()]

    To_Surface_468: Annotated[str, Field()]

    View_Factor_468: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_469: Annotated[str, Field()]

    To_Surface_469: Annotated[str, Field()]

    View_Factor_469: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_470: Annotated[str, Field()]

    To_Surface_470: Annotated[str, Field()]

    View_Factor_470: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_471: Annotated[str, Field()]

    To_Surface_471: Annotated[str, Field()]

    View_Factor_471: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_472: Annotated[str, Field()]

    To_Surface_472: Annotated[str, Field()]

    View_Factor_472: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_473: Annotated[str, Field()]

    To_Surface_473: Annotated[str, Field()]

    View_Factor_473: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_474: Annotated[str, Field()]

    To_Surface_474: Annotated[str, Field()]

    View_Factor_474: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_475: Annotated[str, Field()]

    To_Surface_475: Annotated[str, Field()]

    View_Factor_475: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_476: Annotated[str, Field()]

    To_Surface_476: Annotated[str, Field()]

    View_Factor_476: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_477: Annotated[str, Field()]

    To_Surface_477: Annotated[str, Field()]

    View_Factor_477: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_478: Annotated[str, Field()]

    To_Surface_478: Annotated[str, Field()]

    View_Factor_478: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_479: Annotated[str, Field()]

    To_Surface_479: Annotated[str, Field()]

    View_Factor_479: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_480: Annotated[str, Field()]

    To_Surface_480: Annotated[str, Field()]

    View_Factor_480: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_481: Annotated[str, Field()]

    To_Surface_481: Annotated[str, Field()]

    View_Factor_481: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_482: Annotated[str, Field()]

    To_Surface_482: Annotated[str, Field()]

    View_Factor_482: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_483: Annotated[str, Field()]

    To_Surface_483: Annotated[str, Field()]

    View_Factor_483: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_484: Annotated[str, Field()]

    To_Surface_484: Annotated[str, Field()]

    View_Factor_484: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_485: Annotated[str, Field()]

    To_Surface_485: Annotated[str, Field()]

    View_Factor_485: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_486: Annotated[str, Field()]

    To_Surface_486: Annotated[str, Field()]

    View_Factor_486: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_487: Annotated[str, Field()]

    To_Surface_487: Annotated[str, Field()]

    View_Factor_487: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_488: Annotated[str, Field()]

    To_Surface_488: Annotated[str, Field()]

    View_Factor_488: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_489: Annotated[str, Field()]

    To_Surface_489: Annotated[str, Field()]

    View_Factor_489: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""

    From_Surface_490: Annotated[str, Field()]

    To_Surface_490: Annotated[str, Field()]

    View_Factor_490: Annotated[float, Field(le=1.0)]
    """This value is the view factor value From Surface => To Surface"""